from pathlib import PosixPath as Path

from .errors import PyromaniacError, MainComponentIOError
from .args import parse
from .remote import Remote
from .compiler.butane import configure
from .iso import customize
from .server import serve
from .compile import compile

args = parse()
configure(args.butane)
remote = Remote.create(args.address, args.auth)


def ignition():
    # only reload source if not from a character device (like standard input)
    global source
    if 'source' not in globals() or not args.input.is_char_device():
        try:
            source = args.input.read_text()
        except IOError as e:
            raise MainComponentIOError() from e

    return compile(source, remote, tuple(args.args))


try:
    match args.mode:
        case 'ign':
            print(ignition())
        case 'iso':
            customize(
                ignition(), args.iso_arch, args.iso_net, args.iso_disk,
                args.installer,
            )
        case 'serve':
            serve(remote, ignition, Path("."))
except PyromaniacError as e:
    exit(f"Error: {e}")
