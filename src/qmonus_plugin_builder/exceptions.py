class Error(Exception):
    pass


class ScenarioError(Error):
    pass


class CommandError(ScenarioError):
    pass


class DaemonError(Error):
    pass


class DaemonCommandError(DaemonError):
    pass


class ClassError(Error):
    pass


class ModuleError(Error):
    pass


class FatalError(Error):
    pass
