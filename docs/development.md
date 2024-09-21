---
nav_order: 80
---

# Development
*Pyromaniac* is developed in *Python* and, like [Butane][butane], intended to
be distributed and run as a container image. It can simply be built by running
`podman build -t pyromaniac .` in the repository's root directory.

The project is non-commercial, and contributions are very welcome. Consider
opening a [GitHub issue][issues] first to discuss your ideas and get feedback on
whether your changes would be approved.

[butane]: https://coreos.github.io/butane/
[issues]: https://github.com/salatfreak/pyromaniac/issues

## Structure
*Pyromaniac* is structured as a runnable *Python* package which is designed to
be shipped in a container image based on *Butane* and the [CoreOS Installer]
[coreos-installer].

The code is structured into manageable modules and subpackages to improve
separation of concerns and maintainability.

Function signatures are annotated with types. All classes and functions that
are supposed to be used outside of their module should be augmented with a
reST-formatted docstring.

Imports are ordered by their level of abstraction. A library that is or would
be more likely to be used by another one is imported before it.

Any *Python* code should pass [pycodestyle][pycodestyle] without warnings.

[coreos-installer]: https://coreos.github.io/coreos-installer/
[pycodestyle]: https://github.com/PyCQA/pycodestyle

## Version Control
Commits and pull requests shall be performed against the [dev][dev] branch or
dedicated feature branches named "feat/" followed by a brief description of the
feature in kebab-case. When a stable version is reached, the *dev* branch may
be merged into the *main* branch.

Commit messages follow a simple version of [Conventional
Commits][conventional-commits]. They are not capitalized and shall be prefixed
with "feat: " (for new features and general additions), "fix: " (for bug
fixes), "refactor: " (for code refactoring), "test: " (for everything test case
related), "docs: " (for everything documentation related), or "merge: " (for
merge commits). Commit bodies are optional free-form descriptions and
explanations of the changes.

Commits that would contain changes from multiple of these categories shall be
broken up to match this scheme. Individual commits may introduce temporary
restrictions in functionality but should not produce invalid code or
malfunction of enabled features.

[dev]: https://github.com/salatfreak/pyromaniac/tree/dev
[conventional-commits]: https://www.conventionalcommits.org/en/v1.0.0/

## Testing
*Python*'s built-in [unittest][unittest] framework is used for testing. Test
cases shall be placed in the */tests* directory, which is not shipped with the
container. The test modules are named after the subpackage or module they are
providing tests for.

There should be test cases covering all major features of the package. All
tests must succeed before code is merged into the *main* branch.

It is recommended to run the tests directly in the *Pyromaniac* container:

```sh
podman run --rm \
  --volume ./pyromaniac:/src/pyromaniac:ro \
  --volume ./stdlib:/usr/local/lib/pyromaniac/std:ro \
  --volume ./tests:/src/tests:ro \
  --workdir /src \
  --entrypoint "/usr/bin/python3" \
  pyromaniac -m unittest
```

[unittest]: https://docs.python.org/3/library/unittest.html

## Updating
Whenever a new release is pulled to the main branch, the *pyromaniac.sh* script
should reference the container image with the version number the release will
get.

Updates to used *Python* package, *Butane*, or the *CoreOS Installer* should be
brought in by bumping up their version number in the *pyproject.toml* or
*Containerfile* respectively. The unit tests should then be executed, and a new
minor release of *pyromaniac* should be published.

If an update to the *CoreOS Installer* modifies the command line flags to the
`iso customize` subcommand, *Pyromaniac*'s argument parsing needs to be updated
to be able to pass them on via the `--iso-raw-*` flags. Assuming the format of
the `iso customize --help` message doesn't change, the updated list of flags
for the argument parser can be generated using the following command:

```sh
podman run --rm "quay.io/coreos/coreos-installer:v${VERSION}" \
  iso customize --help \
  | sed -n \
    -e 's/^  \(-[a-z0-9],\|   \) --\([a-z0-9_-]\+\)$/  ("\2", 0),/p' \
    -e 's/^  \(-[a-z0-9],\|   \) --\([a-z0-9_-]\+\) <.*>$/  ("\2", 1),/p'
```
