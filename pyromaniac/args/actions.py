from argparse import _StoreAction, _AppendAction, _AppendConstAction


class IsoStore(_StoreAction):
    """Store action that sets mode to \"iso\""""

    def __call__(self, parser, namespace, *args, **kwargs):
        super().__call__(parser, namespace, *args, **kwargs)
        setattr(namespace, 'mode', 'iso')


class IsoAppend(_AppendAction):
    """Append action that sets mode to \"iso\""""

    def __call__(self, parser, namespace, *args, **kwargs):
        super().__call__(parser, namespace, *args, **kwargs)
        setattr(namespace, 'mode', 'iso')


class IsoAppendConst(_AppendConstAction):
    """Append const action that sets mode to \"iso\""""

    def __call__(self, parser, namespace, *args, **kwargs):
        super().__call__(parser, namespace, *args, **kwargs)
        setattr(namespace, 'mode', 'iso')
