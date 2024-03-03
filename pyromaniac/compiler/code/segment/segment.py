from .segmenter import Segmenter


def segment(
    code: str
) -> tuple[str | None, str | None, str | None, str | None]:
    """Segment the source code into doc string, signature, python, and yaml.

    Returns either the segment string or None for each possible segment. Makes
    sure that the line numbers stay unaltered for python and yaml code to
    enable accurate error messages during parsing.

    :param code: source code to create segments from
    :returns: string or None for each segment respectively
    """
    doc, sig, python, yaml = Segmenter(code).segment()
    return (
        code[doc] if doc is not None else None,
        extract(code, sig) if sig is not None else None,
        extract(code, python) if python is not None else None,
        extract(code, yaml) if yaml is not None else None,
    )


# extract code segment without altering line numbers
def extract(code: str, slc: slice):
    return "\n" * code[:slc.start].count("\n") + code[slc]
