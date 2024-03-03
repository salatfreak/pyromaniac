from .errors import PyromaniacError, MainComponentIOError
from .args import parse
from .compiler.butane import configure
from .iso import customize
from .server import serve
from .compile import compile

args = parse()
configure(args.butane)


def ignition():
    # only reload source if not from a character device (like standard input)
    global source
    if 'source' not in globals() or not args.input.is_char_device():
        try:
            source = args.input.read_text()
        except IOError as e:
            raise MainComponentIOError() from e

    return compile(source, args.address, args.auth, tuple(args.args))


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
            serve(ignition, *args.address[:2], args.auth)
except PyromaniacError as e:
    exit(f"Error: {e}")
