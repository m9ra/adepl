import os
from time import sleep
from typing import List

from adepl.core import EVENT
from adepl.executors.executor_base import ExecutorBase
from adepl.executors.process_proxy import ProcessProxy


class PythonCondaExecutor(ExecutorBase):
    def __init__(self, env: str, start_module: str, extra_code_dependencies: List = None,
                 package_dependencies: List = None, **kwargs):
        super().__init__(**kwargs)

        self._extra_code_dependencies = list(extra_code_dependencies or [])
        self._package_dependencies = list(package_dependencies or [])

        self._env = env
        self._start_module = start_module

        self._process_proxy = ProcessProxy()

    def _executor(self):
        while not self.is_stopped:
            # TODO handle package dependencies
            # TODO handle conda envs
            env = os.environ.copy()
            if self._extra_code_dependencies:
                env["PYTHONPATH"] = ":".join(d.root for d in self._extra_code_dependencies)

            execution_command = f"python -u -m {self._start_module}"
            self._trigger(EVENT.CMD_EXECUTED, {"command": execution_command})

            self._process_proxy.start(
                execution_command, cwd=self._project.working_directory,
                stdout=self._stdout_reader, stderr=self._stderr_reader,
                env=env
            )
            self._process_proxy.wait()
            self._trigger(EVENT.CMD_EXECUTED)
            sleep(1)  # prevent rapid spinning

    def _restart(self):
        self._process_proxy.kill()

    def _stdout_reader(self, line):
        self._trigger(EVENT.STDOUT, {"line": line})

    def _stderr_reader(self, line):
        self._trigger(EVENT.STDERR, {"line": line})

    def _on_stop(self):
        super()._on_stop()
        self._process_proxy.kill()
