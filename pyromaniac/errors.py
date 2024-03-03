class PyromaniacError(Exception):
    """Base class for all pyromaniac errors."""


class MainComponentIOError(PyromaniacError):
    """Error raised when main component can't be read."""

    def __str__(self) -> str:
        return "Reading the main component failed."
