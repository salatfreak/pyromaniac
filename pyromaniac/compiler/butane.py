from typing import Any
import sys
import subprocess
from pathlib import PosixPath as Path
import yaml

from .. import paths
from .errors import RenderError
from .url import URL

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


# configure Path and URL serialization
def representer(dumper: yaml.Dumper, data: Any):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))


yaml.add_representer(Path, representer)
yaml.add_representer(URL, representer)
