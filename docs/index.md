---
nav_order: 0
---

# Pyromaniac
*Pyromaniac* is a framework for configuring and deploying self-maintaining
server operating systems and services in a declarative, reproducible, and
modular way based on [Fedora CoreOS][fcos], [Butane][butane], and
[Jinja][jinja]. Use it as a more powerful drop-in replacement for *Butane*,
break your config up into reusable parameterized components, or build and
publish your own libraries with ease.

[fcos]: https://fedoraproject.org/coreos/
[butane]: https://coreos.github.io/butane/
[jinja]: https://jinja.palletsprojects.com/

## How to Read this Documentation
First of all to get *Pyromaniac* running, check out the
[Installation][installation] page.

To learn about how to execute *Pyromaniac* read the [Command Line
Interface][cli] page. You can mostly use it as a drop-in replacement for
*Butane* but *Pyromaniac* doesn't support all of its command line options and
has a couple exciting additional features.

You will write your configuration source code as *Pyromaniac* components. Don't
worry: Your existing *Butane* configuration files are already valid
*Pyromaniac* components. The [Components][components] page is all about the
syntax and built-in functions that *Pyromaniac* has to offer.

*Pyromaniac* executes arbitrary python code from your source files but it does
so in an optionally read-only container. Read more about this on the [Security
Considerations][security] page.

This is a non-commercial project and you are welcome to contribute. Please read
the [Development][development] page to learn about what to pay attention to.

[installation]: installation.html
[cli]: cli.html
[components]: components.html
[security]: security.html
[development]: development.html
