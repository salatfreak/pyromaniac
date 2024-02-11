from .args import parse
from .__init__ import compile

args = parse()

print(compile(args.input.read_text(), args.address, args.auth))
