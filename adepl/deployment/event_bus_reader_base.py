from typing import Any, Optional, Callable, Dict


class EventBusReaderBase(object):
    solution_stop_event = "solution_stop"
    project_change = "project_change"

    def _on_stop(self):
        raise NotImplementedError("must be overridden")

    def __init__(self):
        self._owner: Optional['SolutionInstance'] = None
        self._event_handlers: Dict[str, Callable[[Any], None]] = {}

        self._set_event_handler(EventBusReaderBase.solution_stop_event, self._handle_stop)
        self._is_stopped = False

    @property
    def is_stopped(self):
        return self._is_stopped

    def start(self, owner: 'SolutionInstance'):
        if self._owner is not None:
            raise AssertionError("Can't start the reader twice")

        self._owner = owner
        self._owner.subscribe(self)

    def receive(self, event_name, event_args):
        handler = self._event_handlers.get(event_name)
        if handler is not None:
            handler(event_args)

    def _set_event_handler(self, event_name: str, handler: Callable[[Any], None]):
        self._event_handlers[event_name] = handler

    def _trigger(self, event_name: str, event_args: Any):
        self._owner.trigger(event_name, event_args)

    def _handle_stop(self, initiator):
        self._is_stopped = True
        self._on_stop()
