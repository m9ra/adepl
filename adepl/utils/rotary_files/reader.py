from threading import Lock
from typing import Callable, IO, Optional

from adepl.utils.rotary_files.writer import Writer


class Reader(object):
    def __init__(self, directory: str):
        self._directory = directory
        self._callback = None
        self._observer = None

        self._current_index = Writer.find_file_indexes(self._directory)[0]
        self._total_capacity = None
        self._current_file = None

    def subscribe(self, callback: Callable[[bytes], None]):
        if self._callback is not None:
            raise AssertionError("Multiple subscribers are not supported")

        self._callback = callback

        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
        from watchdog.observers.inotify_buffer import InotifyBuffer

        InotifyBuffer.delay = 0.01

        storage = self

        class Handler(FileSystemEventHandler):
            def __init__(self):
                self._L_read = Lock()

            def on_modified(self, event):
                if event.is_directory:
                    return  # we are interested in file changes only

                with self._L_read:
                    new_data = storage.read()
                    if new_data:
                        storage._callback(new_data)

        handler = Handler()
        observer = Observer(timeout=1)
        observer.schedule(handler, self._directory, recursive=False)
        with handler._L_read:
            self._observer = observer
            observer.start()
            initial_data = self.read()
            if initial_data:
                self._callback(initial_data)

    def read(self) -> bytes:
        result = bytes()
        while True:
            data = self._read_raw()
            if not data:
                break

            result += data

        return result

    def close(self):
        if self._current_file:
            self._current_file.close()
            self._current_file = None

        if self._observer:
            self._observer.stop()

    def _read_raw(self) -> Optional[bytes]:
        file = self._get_current_file()
        if file is None:
            return None

        return file.read()

    def _get_current_file(self) -> IO[bytes]:
        if self._current_file is None:
            # no file is opened at the moment
            self._current_file, self._current_capacity = self._try_open_file(self._current_index)
        elif self._current_file.tell() >= self._current_capacity + Writer.preamble_byte_count:
            self._current_file.close()
            self._current_index += 1
            self._current_file, self._current_capacity = self._try_open_file(self._current_index)

        return self._current_file

    def _try_open_file(self, index):
        current_file = None
        current_capacity = None
        try:
            current_file = open(Writer.get_file_path(self._directory, index), mode="rb")
            capacity_bytes = current_file.read(Writer.preamble_byte_count)
            if len(capacity_bytes) != Writer.preamble_byte_count:
                # preamble is not complete yet
                current_file.close()
                return None, None

            current_capacity = int.from_bytes(capacity_bytes, Writer.preamble_encoding)

        except FileNotFoundError:
            # the target file is not existing yet, or we are too late
            current_bottom = Writer.find_file_indexes(self._directory)[0]
            if current_bottom > index:
                raise AssertionError(f"Reading {self._directory} missed for {index} when bottom was {current_bottom}")

        return current_file, current_capacity
