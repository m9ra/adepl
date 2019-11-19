from typing import Any, Optional


class EventBusReaderBase(object):
    def __init__(self):
        self._owner: Optional['SolutionInstance'] = None

    def start(self, owner: 'SolutionInstance'):
        if self._owner is not None:
            raise AssertionError("Can't start the reader twice")

        self._owner = owner

    def _trigger(self, event_name: str, event_param: Any):
        self._owner.trigger(event_name, event_param)
