---
parent: Command Line Interface
nav_order: 80
---

# Help Text
This is the full help text of the pyromaniac program as produced by executing
`pyromaniac --help`.

```
Usage: pyromaniac [-p] [-s] [--iso] [--iso-arch ISO_ARCH] [--iso-net ISO_NET]
                  [--iso-disk ISO_DISK] [--serve] [--address ADDRESS]
                  [--auth AUTH] [-h]
                  [input] [args ...]

Compile a pyromaniac config into ignition format and output it as a string,
as a live or installer ISO image or over HTTP(S). Automatically generate TLS
certificates and authentication credentials for secured network-based
installations.

The pyromaniac configuration format is described in the official
documentation:
https://salatfreak.github.io/pyromaniac/

Downloaded ISO images and encryption keys are stored in /data/cache and
/data/secrets respectively and should be persisted as volumes.

Positional:
  input                Pyromaniac file or directory to compile. (default:
                       standard input)
  args                 Arguments to pass to the main component.

Options:
  -p, --pretty         Make butane produce pretty formatted JSON.
  -s, --strict         Make butane fail on any warnings.
  --iso                Generate an ISO live or installer image instead of an
                       ignition config and write it to standard output.
  --iso-arch ISO_ARCH  Set the processor architecture to generate the ISO
                       image for. (default: x86_64)
  --iso-net ISO_NET    Set static network configuration values for the ISOs
                       "ip=" kernel parameter as a comma-separated list of
                       "KEY=VALUE" pairs. The keys correspond to fields in
                       the kernel parameter without "-ip" suffixes. See the
                       example below.
  --iso-disk ISO_DISK  Make the installer automatically install Fedora CoreOS
                       to the specified disk and use the compiled ignition
                       config for the target system instead of creating a
                       live image from it.
  --serve              Serve the compiled ignition config over HTTP(S)
                       instead of writing it to standard out or generating an
                       ISO image. Also serve secrets requested from
                       "/+([a-z0-9-]).secret" by querying the user. These can
                       be used in the config for requesting encryption keys
                       to avoid storing those in plain text.
  --address ADDRESS    Set the host and optionally the scheme and port the
                       server is reachable at. The host can be an IPv4
                       address, an IPv6 address in square brackets, or a
                       domain name. These are used for generating
                       certificates (in the case of HTTPS) and authentication
                       credentials (if configured to be generated
                       automatically) for a mutually secured connection.
                       (default: http://127.0.0.1:8000/)
  --auth AUTH          Set the credentials for HTTP(S) basic authentication
                       in the format "USER:PASS". Use "auto" to generate
                       credentials from a cryptographic hash of the address
                       and a randomly generated but persistent salt. Use
                       "none" to disable. (default: "none" for HTTP, "auto"
                       for HTTPS)
  -h, --help           Show this help message and exit.

Additionally, when generating an ISO you can specify flags to be passed on to
`coreos-installer iso customize` by prefixing them with "--iso-raw-" (e.g.,
"--iso-raw-dest-karg-append quiet").

Examples:

Create a pretty ignition config for placing a file "/foo.txt":
$ pyromaniac --pretty > main.ign \
... <<< 'storage.files[0]: `file("/foo.txt", "bar")`'

Create an ISO image for installation based on a configuration fetched over a
mutually authenticated encrypted statically configured network connection:
$ pyromaniac --iso \
... --iso-net client=192.168.0.32,netmask=255.255.255.0,gw=192.168.0.1 \
... --iso-disk /dev/sda \
... --address https://192.168.0.16:443443/ \
... <<< '`remote.merge()`' > installer.iso

Serve a config over a mutually authenticated encrypted network connection:
$ pyromaniac --serve --address https://192.168.0.16:443443/ -i config.py
```
