---
parent: Recipes
nav_order: 20
---

# Project Structure
*Pyromaniac* leaves you with a lot of freedom on how and in which language to
declare what your server should look like. This page contains some
recommendations for structuring your *Pyromaniac* projects.

The directory structure for a larger project could, e.g., look something like
this:

```
.
├─ README.md
├─ main.pyro
├─ config.toml
├─ component_a.pyro
├─ component_b.pyro
├─ .gitmodules
├─📂 component_c
│ ├─ main.pyro
│ └─ component_d.pyro
└─📂 lib
  ├─📂 library_a
  │ ├─ main.pyro
  │ └─ ...
  └─📂 library_b
    ├─ main.pyro
    └─ ...
```

## Version Control
First of all, *Pyromaniac* puts great emphasis on maintainability and clarity
by enabling you to set up your servers in a declarative and modular fashion
without boilerplate or unwieldy tooling. All you need is a couple of plain text
files with whatever file structure you see fit.

This makes it easier than ever to put your server configuration under source
control. Whether you want to publish your configuration on *GitHub*, store it
on a self-hosted repository platform, or just on your local machine: Go ahead
and initialize a *Git* repository and come up with a suitable commit and
deployment strategy.

While you're at it: Document your strategy and the required commands to build
your project in the repository's *README.md*.

## Main Component
*Pyromaniac* allows you to supply your main component on standard input or
specify any file or pipe to read it from. The convention, however, is to place
it in a file named *main.pyro* in your repository's root directory.

Even though excess positional command line parameters to *Pyromaniac* will
be [passed on to your main component][main-args], it is usually recommended to
place your customizations in a configuration file instead, as described in the
next section.

There are some valid use-cases for main component arguments though. If you
would like to configure a set of multiple hosts through your project, you could
place host-specific configuration in files like *hosts/\<host>.toml* and
require a `host: str` argument to decide which one to load. If you would like
to be able to generate a slightly adjusted version of your server config for
local testing, you could add an optional `testing: bool = False` argument. Your
final *Pyromaniac* invocation could look like this: `pyromaniac . -- my-host
--testing`.

You have a lot of freedom in how your `main.pyro` produces its final result.
Splitting your configurations up and organizing them in trees of components and
libraries is where *Pyromaniac* shines though.

[main-args]: components-signature.html#passing-arguments-to-the-main-component

## Configuration
*Pyromaniac* makes it very easy to build abstractions and keep your
projects configurable. Consider placing all deployment or brand-specific
information in a central configuration file or directory. Depending on your
use case, you might only want to commit a generic template for that
configuration to your main project's source control.

A solid choice would be to create a *config.toml* (and/or *config.toml.tmpl*)
file, load it from your main component using the [*std.load.toml*][toml] and
[*std.magic*][magic] standard library components, and pass the options on as
arguments to your other components.

Your main component might look something like this:

`main.pyro`
```python
---
config = std.magic(std.load.toml(_/"config.toml"))

std.merge(
    my_server(**config.server),
    my_storage(config.storage.root_size or 8000),
)
```

[toml]: components-stdlib.html#load-toml-from-disk-injecting-variables-using-jinja
[magic]: components-stdlib.html#wrap-value-in-magic-type-for-convenient-member-access-and-default-handling

## Libraries
Information technology is all about managing complexity and breaking hard
problems down into easier ones. It is very straightforward to outsource bits
of your configuration into reusable components or libraries in *Pyromaniac*.

Consider bundling all such libraries in a *lib* directory as *Git* submodules.
This allows you to maintain and version control your libraries separately and 
keep your individual projects more manageable. Read more about libraries on the
[Component Libraries][libraries] recipe page.

[libraries]: recipes-libraries.html

## Building on Top of Pyromaniac
If you have built an extensive component framework for making the declaration
of new systems for your use cases a breeze, you can even package it as your own
container image based on *Pyromaniac*.

Add your components to the image's */usr/local/lib/pyromaniac* directory and
optionally configure a new entry point to make your image behave however you
like. Your *Python* scripts can simply import the `pyromaniac` module and
build on top of it. You can even go so far as to specifying your entirely own
*YAML* or *TOML* based specification format, have your *Pyromaniac* components
transform it into a corresponding *Butane* configuration, and produce bootable
disk images within no time.
