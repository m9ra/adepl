from time import sleep
from typing import List

from adepl.executors.executor_base import ExecutorBase
from adepl.executors.process_proxy import ProcessProxy


class PythonCondaExecutor(ExecutorBase):
    def __init__(self, env: str, working_directory: str, start_module: str, extra_code_dependencies: List = None,
                 package_dependencies: List = None, **kwargs):
        super().__init__(**kwargs)

        self._extra_code_dependencies = list(extra_code_dependencies or [])
        self._package_dependencies = list(package_dependencies or [])

        self._env = env
        self._working_directory = working_directory
        self._start_module = start_module

        self._process_proxy = ProcessProxy()

    def _executor(self):
        while True:
            # TODO handle package dependencies
            # TODO handle conda envs
            execution_command = f"python -m {self._start_module}"
            self._process_proxy.start(
                execution_command, cwd=self._working_directory,
                stdout=self._stdout_reader, stderr=self._stderr_reader
            )
            self._process_proxy.wait()
            sleep(1)  # prevent rapid spinning

    def _restart(self):
        self._process_proxy.kill()

    def _stdout_reader(self, data):
        self._trigger("stdout", {
            "owner": self,
            "line": data
        })

    def _stderr_reader(self, line):
        self._trigger("stderr", {
            "owner": self,
            "line": line
        })
