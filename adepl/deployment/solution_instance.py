import traceback
from queue import Queue
from threading import Thread
from typing import List, Optional, Iterable

from adepl.deployment.event_bus_reader_base import EventBusReaderBase
from adepl.executors.executor_base import ExecutorBase


class SolutionInstance(object):
    def __init__(self, name: str, executors: List[ExecutorBase]):
        self._name = name
        self._executors = list(executors)
        self._projects = set()
        self._solution_worker_thread: Optional[Thread] = None
        self._event_bus_input = Queue()
        self._event_bus_readers: List[EventBusReaderBase] = []

        for executor in self._executors:
            self._projects.update(executor.dependencies)

    @property
    def name(self):
        return self._name

    def start(self):
        if self._solution_worker_thread is not None:
            raise AssertionError("Can't start solution twice")

        self._solution_worker_thread = Thread(target=self._solution_worker)
        self._solution_worker_thread.daemon = False  # worker will handle its shutdown
        self._solution_worker_thread.start()

    def stop(self):
        self.trigger(EventBusReaderBase.solution_stop_event, self)

    def add_plugins(self, *plugins: EventBusReaderBase):
        for plugin in plugins:
            plugin.start(self)

    def subscribe(self, reader: EventBusReaderBase):
        self._event_bus_readers.append(reader)

    def trigger(self, event_name, event_args):
        self._event_bus_input.put((event_name, event_args))

    def _solution_worker(self):
        # TODO collect processing logs

        for project in self._projects:
            project.start(self)

        # TODO wait on projects to initialize

        for executor in self._executors:
            executor.start(self)

        while True:
            event = self._event_bus_input.get()
            if event is None:
                return  # ending signal

            for reader in self._event_bus_readers:
                try:
                    reader.receive(*event)
                except:
                    traceback.print_exc()
                    # todo log this

            if event[0] == EventBusReaderBase.solution_stop_event:
                print("Solution stopped")
                return
