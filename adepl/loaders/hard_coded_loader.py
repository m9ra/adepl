from typing import List

from adepl.deployment.solution_instance import SolutionInstance
from adepl.executors.python_conda_executor import PythonCondaExecutor
from adepl.loaders.loader_base import LoaderBase
from adepl.code_providers.git_synced_project import GitSyncedProject


class HardCodedLoader(LoaderBase):
    def _load_solution_instances(self) -> List[SolutionInstance]:
        main_recognizer_project = GitSyncedProject.parse({
            "path": "../lcd-digit-recognizer"
        })

        recognizer_worker_project = GitSyncedProject.parse({
            "path": "../recognize-seven-segment"
        })

        executors = []
        executors.append(
            PythonCondaExecutor.parse({
                "name": "web",
                "env": "p36",
                "project": main_recognizer_project,
                "start_module": "lcd_digit_recognizer.web.app",
                "restart_triggers": [main_recognizer_project]
            })
        )

        for i in range(10):
            executors.append(
                PythonCondaExecutor.parse({
                    "name": "worker" + str(i),
                    "env": "p36",
                    "project": main_recognizer_project,
                    "start_module": "lcd_digit_recognizer.web.recognition_processor.local_recognition_worker",
                    "restart_triggers": [main_recognizer_project, recognizer_worker_project],
                    "extra_code_dependencies": [
                        recognizer_worker_project,
                    ],
                    "package_dependencies": [
                        "matplotlib"
                    ]
                })
            )

        solution_instance = SolutionInstance(
            "cupr", executors
        )

        return [solution_instance]
