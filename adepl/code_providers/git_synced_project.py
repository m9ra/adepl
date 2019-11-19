from adepl.code_providers.project_base import ProjectBase


class GitSyncedProject(ProjectBase):
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)

        self._path = path

    @property
    def root(self):
        return self._path

    def start(self):
        raise NotImplementedError("run git pull periodically")
