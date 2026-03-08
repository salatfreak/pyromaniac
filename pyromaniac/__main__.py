import traceback
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
source = None


def ignition():
    # only reload source if not from a character device (like standard input)
    global source
    if source is None or not args.input.is_char_device():
        try:
            source = args.input.read_text()
        except IOError as e:
            raise MainComponentIOError() from e

    # set library view path if component in subdirectory
    pwd, dir_in = Path().absolute(), args.input.resolve().parent
    in_sub_dir = not args.input.is_absolute() and dir_in.is_relative_to(pwd)
    path = ".".join(dir_in.relative_to(pwd).parts) if in_sub_dir else ""

    # compile source and return ignition
    return compile(source, remote, path, tuple(args.args), parse_args=True)


try:
    match args.mode:
        case 'ign':
            print(ignition())
        case 'iso':
            customize(
                ignition(), args.iso_arch, args.iso_stream, args.iso_net, args.iso_disk,
                args.installer,
            )
        case 'serve':
            serve(remote, ignition, Path("."))
except PyromaniacError as e:
    if args.verbose:
        exit(traceback.format_exc())
    else:
        exit(f"Error: {e}")
