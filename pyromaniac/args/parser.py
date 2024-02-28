"""Construct argument parser"""

from pathlib import PosixPath as Path
from argparse import ArgumentParser

from .. import paths
from .formatter import Formatter
from . import types
from .installer import generate


parser = ArgumentParser(prog="pyromaniac", description=(
    "Compile a pyromaniac config into ignition format and output it as a "
    "string, as an live or installer ISO image or over HTTP(S). Automatically "
    "generate TLS certificates and authentication credentials for secured "
    "network based installations."
    "\n\n"
    "The pyromaniac config format is described in the GitHub repo:\n"
    "https://github.com/salatfreak/pyromaniac"
    "\n\n"
    f"Downloaded ISO images and encryption keys are stored in {paths.cache}"
    f" and {paths.secrets} respectively and should be persisted as volumes."
), epilog=(
    "Additionally, when generating an ISO you can specify flags to be passed "
    "on to `coreos-installer iso customize` by prefixing them with "
    '"--installer-" (e.g. "--installer-dest-karg-append quiet").'
    "\n\n"
    "Examples:"
    "\n\n"
    'Create a pretty ignition config for placing a file "/foo.txt":\n'
    '''$ pyromaniac --pretty <<< "file('/foo.txt', 'bar')" > main.ign'''
    "\n\n"
    "Create an ISO image for installation based on a configuration fetched "
    "over a mutually authenticated encrypted statically configured network "
    "connection:\n"
    "$ pyromaniac --iso \\\n"
    "... --iso-net "
    "client=192.168.0.32,netmask=255.255.255.0,gw=192.168.0.1 \\\n"
    "... --iso-disk /dev/sda \\\n"
    "... --address https://192.168.0.16:443443/ \\\n"
    '... <<< "pyromaniac.netinstall()" > installer.iso'
    "\n\n"
    "Serve a config over a mutually authenticated encrypted network "
    "connection:\n"
    "$ pyromaniac --serve --address https://192.168.0.16:443443/ -i config.py"
), formatter_class=Formatter, add_help=False)
parser._positionals.title = "Positional"
parser._optionals.title = "Options"

butane_args = {'action': 'append_const', 'dest': 'butane', 'default': []}
parser.add_argument(
    "-p", "--pretty", **butane_args, const='--pretty',
    help="Make butane produce pretty formatted json.",
)
parser.add_argument(
    "-s", "--strict", **butane_args, const='--strict',
    help="Make butane fail on any warnings.",
)

parser.add_argument(
    "--iso", action='store_const', dest='mode', const='iso', default='ign',
    help=(
        "Generate an ISO live or installer image instead of an ignition "
        "config and write it to standard output."
    )
)
parser.add_argument("--iso-arch", default="x86_64", help=(
    "Set the processor architecture to generate the ISO image for. (default: "
    "%(default)s)"
))
parser.add_argument("--iso-net", type=types.net, help=(
    'Set static network configuration values for the ISOs "ip=" kernel '
    'parameter as a comma separated list of "KEY=VALUE" pairs. The keys '
    'correspond to fields in the kernel parameter without "-ip" suffixes. See '
    "the example below."
))
parser.add_argument("--iso-disk", help=(
    "Make the installer automatically install Fedora CoreOS to the specified "
    "disk and use the compiled ignition config for the target system instead "
    "of creating a live image from it."
))

parser.add_argument(
    "--serve", action='store_const', dest='mode', const='serve',
    help=(
        "Serve the compiled ignition config over HTTP(S) instead of writing "
        "it to standard out or generating an ISO image. Also serve secrets "
        'requested from "/+([a-z0-9-]).secret" by querying the user. These '
        "can be used in the config for requesting encryption keys to avoid "
        "storing those in plain text."
    ),
)

parser.add_argument(
    "--address", default="http://127.0.0.1:8000/", type=types.address,
    help=(
        "Set the host and optionally the scheme and port the server is "
        "reachable at. The host can be an IPv4 address, an IPv6 address in "
        "square brackets or a domain name. These are used for generating "
        "certificates (in the case of HTTPS) and authentication credentials "
        "(if configured to be generated automatically) for a mutually secure "
        "connection. (default: %(default)s)"
    ),
)
parser.add_argument("--auth", default='default', help=(
    "Set the credentials for HTTP(S) basic authentication in the format "
    '"USER:PASS". Use "auto" to generate credentials from a cryptographic '
    "hash of the address and a randomly generated but persistent salt. Use "
    '"none" to disable. (default: "none" for HTTP, "auto" for HTTPS)'
))

parser.add_argument("-h", "--help", action="help", help=(
    "Show this help message and exit."
))

parser.add_argument(
    "input", nargs='?', default="/dev/stdin", type=Path,
    help="Pyromaniac file or directory to compile. (default: standard input)",
)

parser.add_argument(
    "args", nargs='*', default=[],
    help="Arguments to pass to the main component",
)

for args, kwargs in generate():
    parser.add_argument(*args, **kwargs)
