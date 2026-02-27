from collections.abc import Iterator
from io import StringIO
import tokenize as t

from .token import Token


class Stream:
    """Token stream with look ahead and matching.

    Produces an endless stream of ERRORTOKENs after the ENDMARKER or when an
    unclosed pair (parantheses, quotes, etc.) is encountered.

    :param code: source code to parse
    """

    def __init__(self, code: str):
        self.buffer = []
        self.stream = generate(code)

    def match(self, *pattern: int | tuple[int, str]) -> bool:
        """Check if leading tokens have specified types (and strings).

        Returns True iff the next tokens in the stream match the specified
        types (and string contents) in the specified order.

        :param pattern: list of types and optionally strings to match against
        :returns: whether the leading tokens match the pattern
        """
        for i, pat in enumerate(pattern):
            if i > 0 and self.get(i - 1).type == t.ENDMARKER:
                return False

            # check type and string
            match pat, self.get(i):
                case int(typ), tok if typ != tok.type:
                    return False
                case (pt, ps), tok if (pt, ps) != (tok.type, tok.string):
                    return False

        # return True if no mismatch occured
        return True

    def consume(self, what: int | list[int]) -> Token | None:
        """Remove specified tokens from the start of the stream.

        If *what* is an integer it is interpretet as the amount of tokens to
        remove. If it is a list of integers it is interpreted as a list of
        token types which are removed until a token with a different type is at
        the next one in the stream.

        :param what: count or token types to remove
        :returns: last removed token if any
        """
        last = None

        if isinstance(what, int):
            for i in range(what):
                last = self.get(0, True)
        else:
            while self.get(0).type in what:
                last = self.get(0, True)

        return last

    def get(self, i: int, pop: bool = False) -> Token:
        """Get the token at position *i* and remove it if requested.

        Makes sure, at least *i + 1* tokens are buffered and returns the
        requested token, removing it if requested.

        :param i: index of token to return
        :param pop: whether to remove the token
        :returns: the requested token
        """
        while len(self.buffer) <= i:
            self.buffer.append(next(self.stream))
        return self.buffer.pop(i) if pop else self.buffer[i]


# generate tokens with position in source code
def generate(code: str) -> Iterator[Token]:
    lines = code.splitlines(keepends=True)
    current_line, line_start = 0, 0
    try:
        for info in t.generate_tokens(StringIO(code).readline):
            # get token start
            while current_line < info.start[0] - 1:
                line_start += len(lines[current_line])
                current_line += 1
            start = line_start + info.start[1]

            # get token end
            while current_line < info.end[0] - 1:
                line_start += len(lines[current_line])
                current_line += 1
            end = line_start + info.end[1]

            # yield token and position
            yield Token(info, slice(start, end))
    except t.TokenError:
        pass

    # Keep yielding error token on further reading
    message = 'invalid token'
    info = t.TokenInfo(t.ERRORTOKEN, message, info.start, info.start, message)
    token = Token(info, slice(len(code), len(code)))
    while True:
        yield token
