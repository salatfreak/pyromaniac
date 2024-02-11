from pathlib import Path
import subprocess

from .. import paths
from .errors import DownloadError, CustomizeError


def customize(
    ignition: str, arch: str, net: str | None = None, disk: str | None = None
):
    """Write ISO image with embedded ignition config to stdout.

    Creates an automatic installer image if the target *disk* is specified and
    a live ISO image if it is not.

    :param ignition: ignition config to be embedded
    :param arch: processor architecture to create ISO image for
    :param net: optional value for adding "ip=" kernel argument
    :param disk: optional disk path for automatic installation
    """

    # get base image
    base = get_base_image(arch)

    # customize image
    customize_base_image(base, ignition, net, disk)


def get_base_image(arch: str) -> Path:
    # make sure directory exists
    paths.images.mkdir(parents=True, exist_ok=True)

    # download image
    res = subprocess.run([
        paths.installer, "download", "-f", "iso",
        "--architecture", arch, "-C", paths.images,
    ], capture_output=True, text=True)

    if res.returncode != 0:
        raise DownloadError(res.stderr)

    # get image path
    image = Path(res.stdout.splitlines()[-1])
    if not image.is_relative_to(paths.images) or image.suffix != ".iso":
        raise DownloadError(f"unexpected download output:\n{res.stdout}")

    # remove old image versions
    suffix = ".".join(image.name.split(".")[-2:])
    for f in paths.images.glob("*.iso"):
        if not f.name.endswith(suffix) or f.samefile(image):
            continue
        f.unlink()
        f.with_name(f.name + ".sig").unlink()

    # return image path
    return image


def customize_base_image(
    image: Path, ignition: str, net: str | None, disk: str | None
):
    # collect arguments
    args = ["iso", "customize", image]
    args += ["--output", "-"]

    if net is not None:
        args += ["--live-karg-append", f"ip={net}"]

    if disk is None:
        args += ["--live-ignition", "/dev/stdin"]
    else:
        args += ["--dest-ignition", "/dev/stdin"]
        args += ["--dest-device", disk]

    # customize image
    res = subprocess.run(
        [paths.installer, *args],
        input=ignition.encode(), stderr=subprocess.PIPE
    )
    if res.returncode != 0:
        raise CustomizeError(res.stderr.decode())
