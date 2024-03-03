from ..errors import PyromaniacError


class IsoError(PyromaniacError):
    """Base class for ISO generation errors.

    :param output: coreos-installer error output or custom message
    """

    def __init__(self, output: str):
        super().__init__()
        self.output = output


class DownloadError(IsoError):
    """Error raised when downloading base ISO failed."""

    def __str__(self) -> str:
        lns = self.output.strip().splitlines()
        if lns[0].startswith("Downloading") and lns[0].endswith("signature"):
            lns[0] += " failed:"
        if lns[1].startswith("Error: "):
            lns[1] = lns[1][7:8].upper() + lns[1][8:]
        if lns[-1][-1] != ".":
            lns[-1] += "."
        message = "\n".join(lns)
        return message


class CustomizeError(IsoError):
    """Error raised when customizating ISO image failed."""

    def __str__(self) -> str:
        message = self.output.strip()
        if message.startswith("Error: "):
            message = message[7:8].upper() + message[8:]
        return f"Customizing downloaded ISO image failed:\n{message}"
