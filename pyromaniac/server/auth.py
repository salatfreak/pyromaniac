from os import urandom
from ipaddress import ip_address
from base64 import b64encode
from cryptography.hazmat.primitives import hashes

from .. import paths

SALT_FILE = paths.secrets / "salt.hex"


def auto_auth(scheme: str, host: str, port: int) -> str:
    """Generate basic auth credentials for a given address.

    The user name will be "pyromaniac" and the password will be a base64
    encoded cryptographic hash of the normalized address string and a random
    but persistent salt.

    :param scheme: http or https
    :param host: host name or IP address
    :param port: TCP port
    :returns: basic auth credentials in the format "USER:PASS"
    """

    # assemble address
    try:
        host = ip_address(host).exploded
    except ValueError:
        host = host.lower()
    address = f"{scheme}://{host}:{port}"

    # create password as hash of address with salt
    digest = hashes.Hash(hashes.SHA256())
    digest.update(salt())
    digest.update(address.encode())
    password = b64encode(digest.finalize()).decode()

    # return auth string
    return f"pyromaniac:{password}"


# load or generate and store persistent salt
def salt() -> bytes:
    # load salt if it exists
    if SALT_FILE.exists():
        salt = bytes.fromhex(SALT_FILE.read_text())
    # create and store salt else
    else:
        salt = urandom(32)
        SALT_FILE.write_text(salt.hex())

    return salt
