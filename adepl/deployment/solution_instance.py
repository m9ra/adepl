from queue import Queue
from threading import Thread
from typing import List, Optional

from adepl.deployment.event_bus_reader_base import EventBusReaderBase
from adepl.executors.executor_base import ExecutorBase


class SolutionInstance(object):
    def __init__(self, name: str, projects: List[ExecutorBase]):
        self._name = name
        self._projects = list(projects)
        self._solution_worker_thread: Optional[Thread] = None
        self._event_bus_input = Queue()
        self._event_bus_readers = List[EventBusReaderBase]

    def start(self):
        if self._solution_worker_thread is not None:
            raise AssertionError("Can't start solution twice")

        self._solution_worker_thread = Thread(target=self._solution_worker)
        self._solution_worker_thread.daemon = True
        self._solution_worker_thread.start()

    def _solution_worker(self):
        # TODO collect processing logs
        for project in self._projects:
            project.start(self)

        while True:
            event = self._event_bus_input.get()
            if event is None:
                return  # ending signal

            raise NotImplementedError("")
