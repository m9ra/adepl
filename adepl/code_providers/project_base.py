from typing import Dict

from adepl.deployment.event_bus_reader_base import EventBusReaderBase


class ProjectBase(EventBusReaderBase):
    code_change_event = "code_change"

    def __init__(self, **kwargs):
        super().__init__()

        if kwargs:
            raise AssertionError("Non-processed configuration left " + str(kwargs))

    @classmethod
    def parse(cls, configuration: Dict) -> 'ProjectBase':
        project = cls(**configuration)
        return project

    def _report_change(self):
        self._trigger(ProjectBase.code_change_event, self)
