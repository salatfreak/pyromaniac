from ..errors import PyromaniacError


class IsoError(PyromaniacError):
    def __init__(self, output: str):
        self.output = output


class DownloadError(IsoError):
    def __str__(self) -> str:
        lns = self.output.strip().splitlines()
        if lns[0].startswith("Downloading") and lns[0].endswith("signature"):
            lns[0] += " failed:"
        message = "\n".join(lns)
        return message


class CustomizeError(IsoError):
    def __str__(self) -> str:
        message = self.output.strip()
        return f"Customizing downloaded ISO image failed:\n{message}"
