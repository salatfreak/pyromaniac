import sys
import subprocess
import yaml

from .. import paths
from .errors import RenderError

config: list[str] = []


def configure(new: list[str]):
    """Configure butane command line parameters.

    :param new: list of butane command line parameters
    """
    global config
    config = new


def butane(source: dict) -> str:
    """Transpile butane config to ignition.

    :param source: butane config structured dict
    :returns: ignition config as string
    """
    res = subprocess.run(
        [paths.butane, "--files-dir", ".", *config],
        input=yaml.dump(source), capture_output=True, text=True,
    )
    if res.returncode != 0:
        raise RenderError(res.stderr.strip())

    warning = res.stderr.strip()
    warning == "" or print(warning, file=sys.stderr)

    return res.stdout.strip()
