from ..errors import PyromaniacError


class IsoError(PyromaniacError):
    pass


class DownloadError(IsoError):
    def __init__(self, message: str):
        self.message = message


class CustomizeError(IsoError):
    def __init__(self, message: str):
        self.message = message
