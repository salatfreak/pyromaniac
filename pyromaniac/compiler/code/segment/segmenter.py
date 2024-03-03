import tokenize as t

from .errors import UnexpectedTokenError, SignatureSyntaxError
from .token import Token
from .stream import Stream

# token types to ignore between meaningfull tokens
TYPES = [t.NL, t.NEWLINE, t.COMMENT]


class Segmenter:
    """Source code segmenter.

    :param code: source code to segment"""

    def __init__(self, code: str):
        self.tokens = Stream(code)
        self.length = len(code)

    def segment(
        self
    ) -> tuple[slice | None, slice | None, slice | None, slice | None]:
        """Segment source code into doc string, signature, python and yaml.

        Returns either a slice or None for each possible segment. If a slice,
        it can be used to index the source code to get the according segment.
        Raises errors when doc string or signature are followed by unexpected
        tokens or the signature isn't finished but leaves all other error
        detection to the python and yaml parsers.

        :returns: tuple of optional slices representing source code positions
        """
        # initialize result slices
        doc, sig, python, yaml = (None,) * 4

        # consume encoding token
        last = self.tokens.consume([t.ENCODING])
        if last is None:
            token = self.tokens.get(0)
            raise UnexpectedTokenError(token, "at the beginning")

        # get doc string if present
        last = self.tokens.consume(TYPES) or last
        if self.tokens.match(t.STRING):
            doc, last = self.read_doc()
            last = self.tokens.consume(TYPES)
            if last is None:
                token = self.tokens.get(0)
                raise UnexpectedTokenError(token, "after the doc string")

        # get signature if present
        if self.tokens.match((t.OP, '(')):
            sig, last = self.read_signature()
            last = self.tokens.consume(TYPES)
            if last is None:
                token = self.tokens.get(0)
                raise UnexpectedTokenError(token, "after the signature")

        # get python code if present
        if self.tokens.match(
            (t.OP, '-'), (t.OP, '-'), (t.OP, '-'), t.NEWLINE,
        ):
            last = self.tokens.consume(3)
            python, last, end = self.read_python()
        else:
            end = False

        # get yaml code if present
        if not end:
            yaml = slice(last.stop, self.length)

        # return slices
        return doc, sig, python, yaml

    # read doc string and return the slice and the last consumed token
    def read_doc(self) -> tuple[slice, Token]:
        last = self.tokens.consume(1)
        return last.slice, last

    # read the signature and return the slice and the last consumed token
    def read_signature(self) -> tuple[slice, Token]:
        balance = 0

        # consume opening paranthesis
        last = self.tokens.consume(1)
        start = last.start + 1
        balance += 1

        # consume until matching closing paranthesis
        while balance > 0:
            if self.tokens.match((t.OP, '(')):
                balance += 1
            elif self.tokens.match((t.OP, ')')):
                balance -= 1
            elif self.tokens.match(t.ERRORTOKEN):
                raise SignatureSyntaxError(self.tokens.get(0))
            last = self.tokens.consume(1)

        return slice(start, last.stop - 1), last

    # read the python code and return slice, the last token, and whether at end
    def read_python(self) -> tuple[slice, Token, bool]:
        last = self.tokens.consume(1)
        start = self.tokens.get(0).start

        while True:
            if self.tokens.match(t.ENDMARKER):
                return slice(start, last.stop), last, True
            elif self.tokens.match(t.ERRORTOKEN):
                return slice(start, self.length), last, True
            elif last.type in (t.NL, t.NEWLINE) and self.tokens.match(
                (t.OP, '-'), (t.OP, '-'), (t.OP, '-'), t.NEWLINE,
            ):
                return slice(start, last.stop), self.tokens.consume(4), False
            else:
                last = self.tokens.consume(1)
