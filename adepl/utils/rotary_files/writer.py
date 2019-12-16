import contextlib
import os
from typing import Union, Tuple, IO, List


class Writer(object):
    file_suffix = ".rtrf"
    history_file_count = 3
    preamble_byte_count = 4
    preamble_encoding = "big"

    def __init__(self, directory: str, history_limit: int):
        self._directory = directory
        self._history_limit = history_limit

        os.makedirs(directory, exist_ok=True)

        self._current_file_index = self.find_last_file_index(self._directory)

        self._current_file = None
        self._capacity = 0

    def write(self, data: Union[str, bytes]):
        if isinstance(data, str):
            raw_data = data.encode('utf8')
        elif isinstance(data, bytes):
            raw_data = data
        else:
            raise AssertionError(f"Invalid data type {data.__class__}. Str or bytes expected")

        while raw_data:
            raw_data = self._write_raw(raw_data)

    def flush(self):
        if self._current_file:
            self._current_file.flush()

    def close(self):
        self._current_file.close()
        self._current_file = None
        self._capacity = None

    @classmethod
    def find_last_file_index(cls, directory) -> int:
        file_names = cls.find_file_indexes(directory)

        return file_names[-1]

    @classmethod
    def find_file_indexes(cls, directory) -> List[int]:
        file_names = [
            int(f[:-len(cls.file_suffix)]) for f in filter(lambda f: f.endswith(cls.file_suffix), os.listdir(directory))
        ]
        file_names.sort()

        if not file_names:
            file_names.append(0)

        return file_names

    @classmethod
    def get_file_path(cls, directory: str, index: int) -> str:
        return os.path.join(directory, str(index) + Writer.file_suffix)

    @classmethod
    def try_open_existing_file(cls, directory: str, index: int):
        path = cls.get_file_path(directory, index)

        try:
            file = open(path, "r+b")
            file.seek(0, os.SEEK_END)
            offset = file.tell()
            if offset > Writer.preamble_byte_count:
                file.seek(0, os.SEEK_SET)
                file_capacity = int.from_bytes(file.read(Writer.preamble_byte_count), Writer.preamble_encoding)
                file.seek(0, os.SEEK_END)
                return file, file_capacity - offset + Writer.preamble_byte_count
            else:
                # otherwise corrupted file
                file.close()

        except FileNotFoundError:
            pass

        return None, None

    def _write_raw(self, data: bytes) -> bytes:
        current_file, capacity = self._get_current_file()

        bytes_to_write = min(capacity, len(data))
        written_bytes = current_file.write(data[:bytes_to_write])

        self._capacity -= written_bytes

        return data[written_bytes:]

    def _get_current_file(self) -> Tuple[IO[bytes], int]:
        if self._capacity <= 0:
            if self._current_file:
                self._current_file.close()
                self._current_file_index = self._current_file_index + 1

            self._current_file, self._capacity = self._open_file(self._current_file_index)

        return self._current_file, self._capacity

    def _open_file(self, index: int) -> Tuple[IO[bytes], int]:
        directory = self._directory

        file, capacity = self.try_open_existing_file(directory, index)
        if file is not None:
            return file, capacity

        path = self.get_file_path(directory, index)
        old_path = self.get_file_path(directory, index - Writer.history_file_count)
        with contextlib.suppress(FileNotFoundError):
            os.remove(old_path)

        file = open(path, "wb")
        written_bytes = file.write(self._history_limit.to_bytes(Writer.preamble_byte_count, Writer.preamble_encoding))
        if written_bytes != Writer.preamble_byte_count:
            raise AssertionError("Invalid preamble write")

        return file, self._history_limit
