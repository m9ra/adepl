from typing import List

from adepl.core.solution_instance import SolutionInstance


class LoaderBase(object):
    def load_solution_instances(self) -> List[SolutionInstance]:
        return self._load_solution_instances()

    def _load_solution_instances(self) -> List[SolutionInstance]:
        raise NotImplementedError("must be overridden")
