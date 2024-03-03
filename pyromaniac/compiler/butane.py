from typing import Any
import sys
import re
import subprocess
from pathlib import PosixPath as Path
import yaml

from .. import paths
from .errors import NotADictError, ButaneError
from .url import URL

LINE_RE = re.compile(
    '^((?:warning|error) at .*), line [0-9]+ col [0-9]+(: .*)$',
)

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
    if not isinstance(source, dict):
        raise NotADictError(source)

    code = yaml.dump(source)
    res = subprocess.run(
        [paths.butane, "--files-dir", ".", *config],
        input=code, capture_output=True, text=True,
    )
    if res.returncode != 0:
        raise ButaneError(clean(res.stderr.strip()), code)

    warning = res.stderr.strip()
    warning == "" or print(clean(warning), file=sys.stderr)

    return res.stdout.strip()


def clean(text: str) -> str:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = LINE_RE.match(line)
        if match:
            lines[i] = match[1] + match[2]
    return "\n".join(lines)


# configure Path and URL serialization
def representer(dumper: yaml.Dumper, data: Any):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))


yaml.add_representer(Path, representer)
yaml.add_representer(URL, representer)
