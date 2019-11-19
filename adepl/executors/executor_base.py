from threading import Thread
from typing import Dict, Optional

from adepl.deployment.event_bus_reader_base import EventBusReaderBase


class ExecutorBase(EventBusReaderBase):
    def __init__(self, name: str, restart_triggers: [], **kwargs):
        super().__init__()

        if kwargs:
            raise AssertionError("Non-processed configuration left " + str(kwargs))

        self._name = name
        self._restart_triggers = list(restart_triggers)
        self._executor_thread: Optional[Thread] = None

    @classmethod
    def parse(cls, configuration: Dict) -> 'ProjectBase':
        project = cls(**configuration)
        return project

    def start(self, owner: 'SolutionInstance'):
        if self._executor_thread is not None:
            raise AssertionError("Can't start executor twice")

        super().start(owner)

        self._executor_thread = Thread(target=self._executor)
        self._executor_thread.daemon = True
        self._executor_thread.start()

    def _executor(self):
        raise NotImplementedError("must be overridden")

    def _restart(self):
        raise NotImplementedError("must be overridden")
