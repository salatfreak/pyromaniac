from pathlib import PosixPath as Path
from tempfile import NamedTemporaryFile
from datetime import datetime, timezone, timedelta
from ipaddress import ip_address
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509 import NameAttribute as Attr
from cryptography.x509.oid import NameOID as OID
from cryptography import x509

from .. import paths

ROOT_KEY = paths.secrets / "root.key"
ROOT_CRT = paths.secrets / "root.cert"

ROOT_NAME = x509.Name([
    Attr(OID.COUNTRY_NAME, "UK"),
    Attr(OID.ORGANIZATION_NAME, "Pyromaniac"),
    Attr(OID.COMMON_NAME, "Pyromaniac Root"),
])

SERVER_NAME = x509.Name([
    Attr(OID.COUNTRY_NAME, "UK"),
    Attr(OID.ORGANIZATION_NAME, "Pyromaniac"),
    Attr(OID.COMMON_NAME, "Pyromaniac Server"),
])


def root() -> tuple[Path, Path]:
    """Make sure a self-signed root certificate exists and return it.

    :returns: the path to the certificate and the path to its private key
    """

    # generate key if not exists
    if not ROOT_KEY.exists():
        generate_key(ROOT_KEY)

    # generate certificate if not exists
    if not ROOT_CRT.exists():
        generate_crt(ROOT_NAME, ROOT_KEY, ROOT_NAME, ROOT_KEY, 20 * 365, [
            (x509.BasicConstraints(True, None), True),
            (x509.KeyUsage(*(i == 5 for i in range(9))), True),
        ], path=ROOT_CRT)

    # return file paths
    return ROOT_CRT, ROOT_KEY


def server(host: str) -> tuple[Path, Path]:
    """Generate a certificate for the given host and return it.

    :param host: ip address or host name to certify
    :returns: the path to the certificate and the path to its private key
    """

    # ensure root certificate exists
    root()

    # generate key
    key_path = generate_key()

    # create alternative name
    try:
        alt = x509.IPAddress(ip_address(host))
    except ValueError:
        alt = x509.DNSName(host)

    # generate certificate
    crt_path = generate_crt(ROOT_NAME, ROOT_KEY, SERVER_NAME, key_path, 365, [
        (x509.BasicConstraints(False, None), True),
        (x509.KeyUsage(*(i == 0 for i in range(9))), True),
        (x509.SubjectAlternativeName([alt]), False),
    ], concat=ROOT_CRT)

    # return file paths
    return crt_path, key_path


# generate key and write it to file
def generate_key(path: Path | None = None) -> Path:
    if not path:
        path = Path(NamedTemporaryFile(delete=False).name)
    key = rsa.generate_private_key(65537, 2048)
    path.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ))
    return path


# load key from file
def load_key(path: Path) -> rsa.RSAPrivateKey:
    return serialization.load_pem_private_key(path.read_bytes(), None)


# generate certificate
def generate_crt(
    issuer: x509.Name, issuer_key: Path,
    subject: x509.Name, subject_key: Path,
    days: int = 365, extensions: list[tuple[x509.Extension, bool]] = [],
    concat: Path | None = None, path: Path | None = None,
) -> Path:
    ikey, skey = load_key(issuer_key), load_key(subject_key)
    time_start = datetime.now(timezone.utc)
    time_end = time_start + timedelta(days=days)
    if not path:
        path = Path(NamedTemporaryFile(delete=False).name)

    builder = x509.CertificateBuilder() \
        .issuer_name(issuer).subject_name(subject) \
        .public_key(skey.public_key()) \
        .serial_number(x509.random_serial_number()) \
        .not_valid_before(time_start).not_valid_after(time_end)

    for extension, critical in extensions:
        builder = builder.add_extension(extension, critical)

    cert = builder.sign(ikey, hashes.SHA256())
    cert_bytes = cert.public_bytes(serialization.Encoding.PEM)
    if concat:
        cert_bytes += concat.read_bytes()
    path.write_bytes(cert_bytes)
    return path
