class PyromaniacError(Exception):
    pass


class MainComponentIOError(PyromaniacError):
    def __str__(self) -> str:
        return "Reading the main component failed."
