import os
import time

from adepl.deployment.event_bus_reader_base import EventBusReaderBase
from adepl.utils.rotary_files.writer import Writer


class ConsoleWriter(EventBusReaderBase):
    def __init__(self):
        super().__init__()

        self._open_files = {}

        self._set_event_handler("stdout", lambda d: self._write_data("STDOUT", d))
        self._set_event_handler("stderr", lambda d: self._write_data("STDERR", d))

    def _write_data(self, device, data):
        file_path = os.path.join("/tmp", "adepl", "console_writer", self._owner.name, data["owner"].name, "console.txt")
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
