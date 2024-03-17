---
parent: Recipes
nav_order: 60
---

# Rootless Podman
Even though you can easily embed raw executables and systemd services into your
deployments, *Fedora CoreOS* comes with *docker* and *podman* preinstalled and
is optimized for container workloads.

In regards to building secure systems, the *podman* engine has the major
advantage of being geared towards rootless containers. You can use this to add
an extra layer of separation by running different services as different *Linux*
users. When an attacker manages to compromise your service and also to break
out of the container, they will still not have control over the entire system
or other containers running on it.

## Systemd Units
The recommended way to manage *podman* containers outside of platforms like
*Kubernetes* is using [Quadlet][quadlet]. *Quadlet* allows you to specify your
container deployments inside special kinds of *systemd* unit files like the
following.

`my-service.container`
```ini
[Unit]
Description=My Service

[Container]
Image=docker.io/my/image

[Service]
Restart=always

[Install]
WantedBy=default.target
```

You can use the *tree* standard library component to include an entire
directory of such units into your deployment like this:

```python
---
dirs = directories(".", ".config/containers", "myuser")
units = tree(".config/containers/systemd", _/"units", "myuser")
---

storage:
    directories: `dirs + units['directories']`
    files: `units['files']`
```

[quadlet]: https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html

## Templating
The great thing about *Pyromaniac* is that you can outsource code and build
abstractions very easily. You can write a component for constructing a unit
file from a Jinja template or even for creating units from scratch.

A component for creating *Quadlet* units from scratch might look something like
this:

`quadlet.pyro`
```python
(user: str, name: str, ext: str = "container", **sections: dict[str, str])
---
lines = []
for section, fields in sections.items():
    lines.append(f"[{section.capitalize()}]")
    for key, value in fields.items():
        key = "".join(w.capitalize() for w in key.split("_"))
        lines.append(f"{key}={value}")

file(f".config/containers/systemd/{name}.{ext}", "\n".join(lines), user)
```

It could be used to add a file for the unit from above as follows:

```python
---
unit = quadlet(
    "myuser", "my-service",
    unit={"description": "My Service"},
    container={"image": "docker.io/my/image"},
    service={"restart": "always"},
    install={"wanted_by": "default.target"},
)
---

storage.files[0]: `unit`
```
