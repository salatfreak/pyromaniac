"""Collection of paths for runtime files."""

from pathlib import PosixPath as Path

butane = Path("/usr/local/bin/butane")
installer = Path("/usr/sbin/coreos-installer")

stdlib = Path("/usr/local/lib/pyromaniac")

data = Path("/data")
secrets = data / "secrets"
cache = data / "cache"
images = cache / "images"
