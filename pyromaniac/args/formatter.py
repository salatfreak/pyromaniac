from argparse import HelpFormatter


class Formatter(HelpFormatter):
    """Help formatter that respects manual line breaks"""

    def add_usage(self, usage, actions, groups, prefix="Usage: "):
        return super(Formatter, self).add_usage(usage, actions, groups, prefix)

    def _fill_text(self, text, width, indent):
        return '\n'.join(
            super(Formatter, self)._fill_text(line, width, indent) for line in
            text.splitlines()
        )

    def _split_lines(self, text, width):
        return [
            line for original in text.splitlines() for line in
            super(Formatter, self)._split_lines(original, width)
        ]
