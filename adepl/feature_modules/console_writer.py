import os
import time

from adepl import ADEPL_RUNTIME_DIR
from adepl.deployment.event_bus_reader_base import EventBusReaderBase
from adepl.utils.rotary_files.reader import Reader
from adepl.utils.rotary_files.writer import Writer

CONSOLE_ROTARY_FILE_NAME = "console.txt"


class ConsoleWriter(EventBusReaderBase):
    def __init__(self):
        super().__init__()

        self._open_files = {}

        self._set_event_handler("stdout", lambda d: self._write_data("STDOUT", d))
        self._set_event_handler("stderr", lambda d: self._write_data("STDERR", d))

    @classmethod
    def create_reader(cls, solution_name, executor_name) -> Reader:
        file_path = os.path.join(ADEPL_RUNTIME_DIR, solution_name, executor_name, CONSOLE_ROTARY_FILE_NAME)
        reader = Reader(file_path)

        return reader

    def _write_data(self, device, data):
        file_path = os.path.join(ADEPL_RUNTIME_DIR, self._owner.name, data["owner"].name, CONSOLE_ROTARY_FILE_NAME)
        file = self._get_file(file_path)
        if device == "STDOUT":
            device = "OUT"
        elif device == "STDERR":
            device = "ERR"

        line = f"[{device} {time.strftime('%Y-%m-%d %H:%M:%S')}] {data['line']} \n"
        file.write(line)
        file.flush()

    def _get_file(self, path):
        if not path in self._open_files:
            writer = Writer(path, 10 * 1024)
            self._open_files[path] = writer

        return self._open_files[path]

    def _on_stop(self):
        for file in self._open_files.values():
            file.close()
