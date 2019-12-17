from threading import Thread
from typing import Dict, Optional

from adepl.core import EVENT
from adepl.core.event_bus_reader_base import EventBusReaderBase



class ProjectBase(EventBusReaderBase):
    def _project_worker(self):
        raise NotImplementedError("must be overridden")

    def _get_name(self):
        raise NotImplementedError("must be overridden")

    def __init__(self, **kwargs):
        super().__init__()

        if kwargs:
            raise AssertionError("Non-processed configuration left " + str(kwargs))

        self._project_worker_thread: Optional[Thread] = None

    @property
    def name(self):
        return self._get_name()

    @classmethod
    def parse(cls, configuration: Dict) -> 'ProjectBase':
        project = cls(**configuration)
        return project

    def start(self, owner: 'SolutionInstance'):
        if self._project_worker_thread is not None:
            raise AssertionError("Can't start project twice")

        super().start(owner)

        self._project_worker_thread = Thread(target=self._project_worker)
        self._project_worker_thread.daemon = True  # TODO project should have a chance to cleanup
        self._project_worker_thread.start()

    def _report_change(self):
        self._trigger(EVENT.PROJECT_CHANGED)

    def _on_stop(self):
        pass  # nothing to do by default
