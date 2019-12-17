import os
from typing import Iterable, List


def list_dir_objects(*path_parts: Iterable[str]) -> List[str]:
    solution_names = []
    for dirname in os.listdir(os.path.join(*path_parts)):
        if dirname.startswith("."):
            continue

        solution_names.append(dirname)

    solution_names.sort()
    return solution_names
