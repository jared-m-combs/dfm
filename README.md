Dotfile Manager
===============

Tool for managing dotfiles in a separate directory with symlinks to
their original locations. Includes commands for adding and removing
files from this directory. An existing dotfiles directory can be
bootstrapped with the `install` command and all symlinks can be
removed with the `uninstall` command.

usage: `dfm [-h] [--dotfiles DOTFILES] {add,a,remove,r,rm,install,i,uninstall,u} ...`

options
-------
`--dotfiles`, `-d`

Directory where dotfiles are stored. Defaults to the `DOTFILE_HOME`
environment variable if specified or to `~/.dotfiles` otherwise.

Default: `~/.dotfiles`

add (a)
-------
Moves the file to the dotfiles directory and leaves a symlink in
its place.

`dfm add [-h] paths [paths ...]`

*Positional Arguments*

`paths` - The paths of the files to add to the dotfiles directory.

remove (r, rm)
--------------
Removes the symlink and restores the file from the dotfiles
directory to its original location.

`dfm remove [-h] paths [paths ...]`

*Positional Arguments*

`paths` - The paths can be either the symlinks or the actual files in the dotfiles directory.

install (i)
-----------
Adds symlinks for all of the non-hidden files in the dotfiles
directory.

`dfm install [-h]`

uninstall (u)
-------------
Removes symlinks for all of the files in the dotfiles directory.

`dfm uninstall [-h]`
