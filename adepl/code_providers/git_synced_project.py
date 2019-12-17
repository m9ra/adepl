from time import sleep

from adepl.code_providers.project_base import ProjectBase
import os.path

from adepl.executors.process_proxy import ProcessProxy


class GitSyncedProject(ProjectBase):
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)

        self._path = os.path.abspath(path)
        self._proxy = ProcessProxy()

    @property
    def root(self):
        return self._path

    @property
    def working_directory(self):
        return self._path

    def _get_name(self):
        return os.path.basename(self._path)

    def _project_worker(self):
        while not self.is_stopped:
            if self._pull_changes():
                self._report_change()

            sleep(5)

    def _pull_changes(self):
        self._change_registered = False
        self._proxy.start("git pull", cwd=self._path, stdout=self._stdout_handler, stderr=self._stderr_handler)
        self._proxy.wait()
        return self._change_registered

    def _on_stop(self):
        self._proxy.kill()

    def _stdout_handler(self, line):
        self._trigger("stdout", {"line": line})

        if line is not None:
            has_change = "files changed" in line or "file changed" in line
            self._change_registered = self._change_registered or has_change

    def _stderr_handler(self, line):
        self._trigger("stderr", {"line": line})
