import os
import time

from adepl.deployment.event_bus_reader_base import EventBusReaderBase


class ConsoleWriter(EventBusReaderBase):
    def __init__(self):
        super().__init__()

        self._open_files = {}

        self._set_event_handler("stdout", lambda d: self._write_data("STDOUT", d))
        self._set_event_handler("stderr", lambda d: self._write_data("STDERR", d))

    def _write_data(self, device, data):
        file_path = os.path.join("/tmp", "adepl", "console_writer", self._owner.name, data["owner"].name, "console.txt")
        file = self._get_file(file_path)
        line = f"[{device} - {time.time()}] {data['line']} \n"
        file.write(line)
        file.flush()

    def _get_file(self, path):
        if not path in self._open_files:
            dirname = os.path.dirname(path)
            os.makedirs(dirname, exist_ok=True)

            self._open_files[path] = open(path, "w", buffering=1)  # line buffered file

        return self._open_files[path]

    def _on_stop(self):
        for file in self._open_files.values():
            file.close()
