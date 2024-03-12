---
nav_order: 20
has_children: true
has_toc: false
---

# Command Line Interface
The core functionality of compiling your configurations into ignition format
works just like *Butane* including the *--strict* flag to make *Pyromaniac*
fail on any warnings and the *--pretty* flag to produce pretty formatted
*JSON*. Other *Butane* flags are not supported directly.

See the [Help Text][help] page or execute `pyromaniac --help` to see the full
CLI help text.

[help]: cli-help.html

## Input Configuration
If no positional parameters are passed to *Pyromaniac* it will attempt to read
the configuration from standard input. Otherwise it will interpret the first
positional parameter as the path to the main configuration component file.

All further parameters will be used as string arguments to the main component.
If the parameter count doesn't match the main components signature, compilation
will fail with an appropriate error message. It is recommended to rather put
custom configuration into *TOML*, *YAML*, or *JSON* files and read them from
inside your main component.

Passing "." as the main component name will make *Pyromaniac* read the
*main.pyro* file from the working directory. This is the recommended way for
multi-component configurations.

Following these conventions will allow you to always just run `pyromaniac . >
config.ign` in your projects root directories without thinking twice about how
to compile specific *Pyromaniac* projects.

## Filesystem Mounts
The current working directory is usually mounted into the container, such that
*Pyromaniac* can read components and local files from it. Referencing files in
a parent directory or using absolute paths will therefore not work. Executing
something like `pyromaniac ../config.pyro` or referencing files outside the
current working directory within your components will fail unless you installed
*Pyromaniac* outside a container.

*Pyromaniac* always writes its results to the standard output to avoid having
to give the container write access to your host file system. You'll have to
redirect it to a file yourself. To compile a component *config.pyro* and write
the resulting *Ignition* code to *config.ign*, simply execute `pyromaniac
config.pyro > config.ign`.

By default, the *Bash* script mounts writable named volumes into the container
to cache *ISO* images, *TLS* certificates, and authentication secrets. To
disable this, pass the `--no-cache` flag to the script. This will however break
*TLS* and auto generated authentication credentials when starting a server or
generating remote *ISO* images.

For debugging you may provide the `--debug` flag which will cause the *Bash*
script to mount the *pyromaniac* and *stdlib* source code directories into
the container. That way you don't need to rebuild the container image whenever
you'd like to test a change to the source code. Both of these directories need
to reside as siblings in the same directory the *Bash* script lies in.

The latter two flags only affect the behavior of the *Bash* script and are
therefore not mentioned in *Pyromaniac*s help text.

## Advanced Features
Besides producing *Ignition* files, *Pyromaniac* can also directly output *ISO*
images and serve configurations over *HTTP(S)*. You can read all about these
features on the [ISO Generation][iso] and [HTTP(S) Server][server] pages.

[iso]: cli-iso.html
[server]: cli-serve.html
