---
nav_order: 10
---

# Installation
The intended way to run *Pyromaniac* is as a *podman* or *docker* container.
A small *Bash* script is available to make this as easy as possible.

## Installation of the Bash Script
To run *Pyromaniac* using the script, make sure [Bash][bash] and
[podman][podman] are installed on your machine and download the [script from
GitHub][script]. If you rename it to `pyromaniac` and place it in your *PATH*
or alternatively create a link to it with that name in your *PATH* (e.g., in
*~/.local/bin/*), you can simply run it by executing `pyromaniac [ARG...]` in
your command line.

[bash]: https://www.gnu.org/software/bash/
[podman]: https://podman.io/
[script]: https://github.com/salatfreak/pyromaniac/blob/main/pyromaniac.sh

## Directly Running the Image
You can run the latest version of the container image without the script by
making sure [podman][podman] (or [docker][docker]) is installed and executing
the following command.

```bash
podman run \
  --rm --interactive \
  --security-opt label=disable \
  --publish 8000:8000 \
  --volume pyromaniac-secrets:/data/secrets \
  --volume pyromaniac-cache:/data/cache \
  --volume .:/spec:ro \
  ghcr.io/salatfreak/pyromaniac:latest [ARG...]
```

You can skip or adjust the `--publish 8000:8000` line, if you don't need the
*HTTP(S)* server or would like it to be reachable under another *TCP* port. You
can also skip the `--volume pyromaniac-secrets:/data/secrets`, if you don't
need the securing of the *HTTP* server. The `--volume
pyromaniac-cache:/data/cache` is only necessary for caching *Fedora CoreOS*
*ISO* images. You can even skip the `--volume .:/spec:ro`, if you provide the
entire configuration via standard input.

You can build the container image yourself by cloning the [GitHub
repository][repo] and executing `podman build -t pyromaniac .` in it.

[docker]: https://www.docker.com/
[repo]: https://github.com/salatfreak/pyromaniac

## Installing Pyromaniac Manually
Make sure you have *pip3*, *butane*, and the *CoreOS Installer* installed on
your system. You can then install the *Pyromaniac* *python* package manually by
cloning the [GitHub repository][repo], adjusting the file system paths in
*pyromaniac/paths.py*, and executing `pip3 install .`. The components in the
*stdlib* directory should be placed in a directory named *lib* inside the
directory the `stdlib` variable in *pyromaniac/paths.py* points to.

You can run the *python* package by executing `python3 -m pyromaniac [ARG...]`.
