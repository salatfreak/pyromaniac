from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import PosixPath as Path
from tempfile import NamedTemporaryFile
from datetime import datetime, timezone, timedelta
from ipaddress import ip_address
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.types import (
    CertificateIssuerPrivateKeyTypes
)
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
        generate_crt(ROOT_CRT, ROOT_NAME, ROOT_KEY, ROOT_NAME, ROOT_KEY, 20 * 365, [
            (x509.BasicConstraints(True, None), True),
            (x509.KeyUsage(*(i == 5 for i in range(9))), True),
        ])

    # return file paths
    return ROOT_CRT, ROOT_KEY


@contextmanager
def server(host: str) -> Iterator[tuple[Path, Path]]:
    """Generate a certificate for the given host and provide it through context manager.

    :param host: ip address or host name to certify
    :returns: context manager providing paths to the new certificate and its private key
    """

    # create alternative name
    try:
        alt = x509.IPAddress(ip_address(host))
    except ValueError:
        alt = x509.DNSName(host)

    # ensure root certificate exists
    root()

    # create temporary files to write key and cert to
    with (
        NamedTemporaryFile(delete_on_close=False) as key_file,
        NamedTemporaryFile(delete_on_close=False) as crt_file,
    ):
        # generate key
        key_path = generate_key(Path(key_file.name))

        # generate certificate
        crt_path = generate_crt(
            Path(crt_file.name), ROOT_NAME, ROOT_KEY, SERVER_NAME, key_path, 365, [
                (x509.BasicConstraints(False, None), True),
                (x509.KeyUsage(*(i == 0 for i in range(9))), True),
                (x509.SubjectAlternativeName([alt]), False),
            ], concat=ROOT_CRT,
        )

        # yield file paths to be provided by the context manager
        yield crt_path, key_path


# generate key and write it to file
def generate_key(path: Path) -> Path:
    key = rsa.generate_private_key(65537, 2048)
    path.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ))
    return path


# load key from file
def load_key(path: Path) -> CertificateIssuerPrivateKeyTypes:
    key = serialization.load_pem_private_key(path.read_bytes(), None)
    assert isinstance(key, CertificateIssuerPrivateKeyTypes)
    return key


# generate certificate
def generate_crt(
    path: Path,
    issuer: x509.Name, issuer_key: Path,
    subject: x509.Name, subject_key: Path,
    days: int = 365, extensions: list[tuple[x509.ExtensionType, bool]] = [],
    concat: Path | None = None,
) -> Path:
    ikey, skey = load_key(issuer_key), load_key(subject_key)
    time_start = datetime.now(timezone.utc)
    time_end = time_start + timedelta(days=days)

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
