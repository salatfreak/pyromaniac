---
parent: Recipes
nav_order: 30
---

# Component Libraries
Outsourcing parts of your configuration into reusable libraries is a great way
to keep your projects manageable and create a good foundation for future ones.
You can even nest libraries as deeply as you like.

You won't have to learn a new build system or package manager, because
you can simply employ *Git* submodules for this.

## Creating a Library
All you need to do to create a library is initialize a separate repository
(`git init`) and populate it with your source files.

The [Project Structure][structure] page's recommendations about version control
and main components apply to libraries as well, except for the convention to
refrain from taking positional and keyword arguments in your main component.
The parameters defined in your main (and other) component's signatures should
in fact be the only way to parameterize your library.

Projects incorporating your library can, of course, access all of its files and
components. Depending on its purpose, it might make sense to design your
library to expose its entire functionality through the main component, though.

What's only a strong recommendation in the context of standalone projects is
vital when it comes to libraries: All references to files and components within
your library must be relative, while references to standard library components
must be absolute. Use `_.my_component()` but
`magic(load.toml(_/"config.toml"))`. Otherwise, your library will break when
moved within the directory structure.

The return values of your library can be whatever you need. They might be
completely custom data, functions, classes, etc. They might also be a list or
dict to populate some field of the *Butane* configuration you are constructing.
Or they might be a complete configuration, ready to be merged with the rest of
your projects' configs using the [*merge* standard library component][merge].

When your library has arrived at a stable state, consider adding a version tag
(`git tag vX.Y.Z`) to easily manage different projects using different versions
of your library.

[structure]: recipes-structure.html
[merge]: components-stdlib.html#create-merge-fields-for-inline-local-andor-remote-configs

## Adding a Library to Your Project
A good place to add all your project's libraries is the *lib* directory. Its
purpose will be obvious, you'll know where to look for your libraries, and you
avoid cluttering your repository's root directory with external code.

To add a library to your project, simply add it as a *Git* submodule and
optionally check out a version tag. Execute, e.g., `git submodule add SOURCE
lib/NAME && cd lib/NAME && git checkout vX.Y.Z` to add a library from a
specific source at a specific version to your *lib* directory with a specific
name. Don't forget to add and commit these changes in your project repository.

If your library has a *main.pyro* component, you can now simply reference and
execute it using `_.lib.NAME(...)`.
