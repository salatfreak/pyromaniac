class IsoError(Exception):
    pass


class DownloadError(IsoError):
    def __init__(self, message):
        self.message = message


class CustomizeError(IsoError):
    def __init__(self, message):
        self.message = message
