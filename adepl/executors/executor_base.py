from threading import Thread
from typing import Dict, Optional, List

from adepl.core import EVENT
from adepl.core.event_bus_reader_base import EventBusReaderBase


class ExecutorBase(EventBusReaderBase):

    def _executor(self):
        raise NotImplementedError("must be overridden")

    def _restart(self):
        raise NotImplementedError("must be overridden")

    def __init__(self, name: str, project: 'ProjectBase', restart_triggers: [], **kwargs):
        super().__init__()

        if kwargs:
            raise AssertionError("Non-processed configuration left " + str(kwargs))

        self._name = name
        self._restart_triggers = set(restart_triggers)
        self._executor_thread: Optional[Thread] = None
        self._project = project

        self._set_event_handler(EVENT.PROJECT_CHANGED, self._change_handler)

    @property
    def name(self):
        return self._name

    @property
    def dependencies(self) -> List['ProjectBase']:
        return list(self._restart_triggers) + [self._project]

    @classmethod
    def parse(cls, configuration: Dict) -> 'ProjectBase':
        executor = cls(**configuration)
        return executor

    def start(self, owner: 'SolutionInstance'):
        if self._executor_thread is not None:
            raise AssertionError("Can't start executor twice")

        super().start(owner)

        self._executor_thread = Thread(target=self._executor)
        self._executor_thread.daemon = False  # the executor has to deliver stopping message to the work in progress
        self._executor_thread.start()

    def _on_stop(self):
        self._is_stopped = True

    def _change_handler(self, initiator):
        if initiator in self._restart_triggers:
            self._restart()
