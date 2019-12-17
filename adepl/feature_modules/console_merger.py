import os
import re
import time

from adepl.core.event_bus_reader_base import EventBusReaderBase


class ConsoleMerger(EventBusReaderBase):
    def __init__(self, matcher, result_alias):
        super().__init__()

        self._matcher_regex = re.compile(matcher)
        self._result_alias = result_alias
        self._open_files = {}

        self._set_event_handler("stdout", lambda d: self._merge_data("stdout", d))
        self._set_event_handler("stderr", lambda d: self._merge_data("stderr", d))

    @property
    def name(self):
        return self._result_alias

    def _merge_data(self, event_name, data):
        if not self._matcher_regex.search(data["owner"].name):
            return  # nothing we would merge here

        new_payload = dict(data)
        new_payload["line"] = f"{data['owner'].name} {data['line']}"

        self._trigger(event_name, new_payload)

    def _on_stop(self):
        pass  # nothing to cleanup
