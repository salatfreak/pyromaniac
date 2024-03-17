<p align="center">
  <a href="https://salatfreak.github.io/pyromaniac/">
    <img src="docs/assets/title.png" alt="Pyromaniac" style="width: 80%;" />
  </a><br />
  🔥 Obsessed with creating Ignition 🔥<br />
  <br />
  <a href="../../actions/workflows/tests.yml"><img
    src="../../actions/workflows/tests.yml/badge.svg" alt="tests badge"
  /></a>
  <img src="docs/assets/beta.svg" alt="beta badge" />
</p>

*Pyromaniac* is a framework for configuring and deploying self-maintaining
server operating systems and services in a declarative, reproducible, and
modular way based on *Fedora CoreOS*, *Butane*, and *Jinja*. Use it as a more
powerful drop-in replacement for *Butane*, break your config up into reusable
parameterized components, or build and publish your own libraries with ease.

> [!TIP]
> You can learn all about *Pyromaniac* in [the documentation][docs] or keep
> reading this document to get an overview of some of *Pyromaniacs* main
> features.

[docs]: https://salatfreak.github.io/pyromaniac/

# 💫 One Tool to Rule Them All 💫
*Pyromaniac* combines the powers of [Butane][butane], the [CoreOS
Installer][installer], and even comes with an *HTTP(S)* server for loading your
configurations over the network, saving you the hassle of generating a new
installer when your configuration changes.

Switch out *Butane* for *Pyromaniac* to generate your *Ignition* file:

```sh
pyromaniac --pretty config.bu > config.ign
```

Generate an *ISO* for unattended installation from your configuration with a
single command:

```sh
pyromaniac --iso --iso-disk /dev/sda config.bu > installer.iso
```

Render and serve your configuration over *HTTPS*:

```sh
pyromaniac --serve --address https://192.168.1.100:8000/ config.bu
```

A self-signed *TLS* certificate and authentication credentials will
automatically be generated and can easily be embedded into your remote
installer for a mutually secured connection.

Learn more in the [CLI Documentation][cli].

[butane]: https://coreos.github.io/butane/
[installer]: https://coreos.github.io/coreos-installer/
[cli]: https://salatfreak.github.io/pyromaniac/cli.html

# 🧁 Sugar, Parameterization, and Decomposition 🧁
*Pyromaniac* extends the *Butane* format with support for composite keys,
[Jinja][jinja] templating using the "\`" (backtick) delimiter, and
parameterized components for better clarity and maintainability.

Configure three text files using composite keys and without repeating yourself:

```yaml
storage.files:
{%- for name in ["Alice", "Bob", "Carol"] %}
  - path: `"/" + name + ".txt"`
    contents.inline: `name + " was here!"`
{%- endfor %}
```

Turn your configuration into a reusable component:

`files.pyro`
```yaml
(*names: str, ext: str = ".txt")

{%- for name in names %}
- path: `"/" + name + ext`
  contents.inline: `name + " was here"`
{%- endfor %}
```

And include it from your main component:

`main.pyro`
```yaml
storage:
  files: `files("Alice", "Bob", "Carol", ext=".md")`
  links[0]:
    path: /favourite.md
    target: /Carol.md
```

Learn more in the [Component Documentation][components].

[jinja]: https://jinja.palletsprojects.com/
[components]: https://salatfreak.github.io/pyromaniac/components.html

# 🐍 Arbitrary Python Code, Local Files, and More! 🐍
*Pyromaniac* allows you to include arbitrary *python* code into your
configuration including the definition of functions and even classes, to make
your components even more powerful. It also comes with a standard library of
components for loading files, rendering *Jinja* templates, adding file system
nodes, etc.

Add a python block with a helper function to your component and use the *file*
and *load* standard library components to configure a file from a local Jinja
template:

```python
(name: str)

---
def path(name: str) -> str:
  return f"/greeting-{name.lower()}.txt"
---

storage.files[0]: `file(path(name), load(_/"greeting.jinja", name=name))`
```

Load two butane configurations specified in TOML format, render them and create
an ignition merge from them:

```python
---
config1 = load.toml(_/"config-1.toml")
config2 = load.toml(_/"config-2.toml")
---

ignition.config.merge: `merge(config1, config2)`
```

Learn more in the [Standard Library Documentation][stdlib].

[stdlib]: https://salatfreak.github.io/pyromaniac/components-stdlib.html

# ❤️ Charityware ❤️
*Pyromaniac* is charityware. It is GPL licensed and you may therefore freely
use and modify it without charge. It would however be great if you took a
minute to consider your power to fundamentally change other people's lives for
the better.

You can [restore a person's eyesight][sight] for half a week's pay or [save a
child from getting malaria][malaria] for a third of an hourly wage.
Contributing to [non-human animal focused charities][animals] is plausibly even
orders of magnitude more effective, since our society brutalizes them in such
inconceivable numbers.

Many people [pledge to give 10%][pledge-10] of their income to charity. Some
even [pledge to donate 99%][pledge-99] of their wealth. Whatever small or large
contribution you are able and willing to make can mean the world to those who
benefit from it.

Please read up on [effective altruism][ea] and the devastating [effects of
animal agriculture][animal-ag] on our planet ❤️

[sight]: https://www.hollows.org/au/home
[malaria]: https://www.malariaconsortium.org/
[animals]: https://animalcharityevaluators.org/
[pledge-10]: https://www.givingwhatwecan.org/pledge
[pledge-99]: https://www.givingpledge.org/pledger?pledgerId=177
[ea]: https://en.wikipedia.org/wiki/Effective_altruism
[animal-ag]: https://en.wikipedia.org/wiki/Environmental_impacts_of_animal_agriculture
