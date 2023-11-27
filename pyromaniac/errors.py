class PyromaniacError(Exception):
    def __init__(self, msg, *args, **kwargs):
        super().__init__(msg[0].lower() + msg[1:], *args, **kwargs)

class LoadError(PyromaniacError):
    def __init__(self, typ, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = typ
        self.name = name

class RenderError(PyromaniacError):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

class ComponentError(PyromaniacError):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
