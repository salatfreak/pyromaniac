from .args import parse
from .iso import customize
from .__init__ import compile

args = parse()


def ignition():
    # only reload source if not from a character device (like standard input)
    global source
    if 'source' not in globals() or not args.input.is_char_device():
        source = args.input.read_text()

    return compile(source, args.address, args.auth)


match args.mode:
    case 'ign':
        print(ignition())
    case 'iso':
        customize(ignition(), args.iso_arch, args.iso_net, args.iso_disk)
    case 'serve':
        raise NotImplementedError()
