Dotfile Manager
===============

Tool for managing dotfiles in a separate directory with symlinks to
their original locations. Provides the `add` and `remove` commands for
adding files to and removing files from this directory. An existing 
dotfiles directory can be bootstrapped with the `install` command and 
all symlinks can be removed with the `uninstall` command.

Installation
------------
As a python package, this project can be installed in the typical manner
using `pip`.

```
pip3 install --user git+https://github.com/jared-m-combs/dfm.git 
```

Alternatively, this tool has no dependencies other than Python 3.
You can simply clone this repository and copy `dfm/dfm.py` to
a directory on your `PATH`. e.g.

```
git clone git+https://github.com/jared-m-combs/dfm.git 
sudo cp dfm/dfm/dfm.py /usr/local/bin/dfm
sudo chmod +x /usr/local/bin/dfm
```

If you can't or would prefer not to use `sudo`, `~/.local/bin` is a
good installation location provided that it is on your `PATH`.

Usage
-----
```
usage: dfm [-h] [--dotfiles DOTFILES] {add,a,remove,r,rm,install,i,uninstall,u} ...

positional arguments:
  {add,a,remove,r,rm,install,i,uninstall,u}
    add (a)             Moves the file to the dotfiles directory and leaves a 
                        symlink in its place.
    remove (r, rm)      Removes the symlink and restores the file from the dotfiles
                        directory to its original location.
    install (i)         Adds symlinks for all of the non-hidden files in the dotfiles
                        directory.
    uninstall (u)       Removes symlinks for all of the files in the dotfiles directory.

options:
  -h, --help            show this help message and exit
  --dotfiles DOTFILES, -d DOTFILES
                        Directory where dotfiles are stored. Defaults to the 'DOTFILE_HOME'
                        environment variable if specified or to '~/.dotfiles' otherwise.
```
```                       
usage: dfm add [-h] paths [paths ...]

positional arguments:
  paths       The paths of the files to add to the dotfiles directory.
```
```
usage: dfm remove [-h] paths [paths ...]

positional arguments:
  paths       The paths can be either the symlinks or the actual files in the dotfiles directory.
```
```
usage: dfm install [-h]
```
```
usage: dfm uninstall [-h]
```

### Dotfile Home Directory
The dotfiles directory can be specified with the `DOTFILES_HOME`
environment variable or via the `--dotfiles` command line flag.
```
dfm --dotfiles ~/.customdotfiles add <file>
DOTFILES_HOME=~/.customdotfiles dfm add <file>
```
If neither of these are provided, the dotfiles directory will
default to `~/.dotfiles`.

### Adding and Removing Files
Files can be added to the dotfiles directory with the `add` command.
```
dfm add ~/.examplerc
```
After running this command, you will notice that the file has been
repaced to with a symlink to the dotfiles directory.
```
ls -al ~/.examplerc
lrwxrwxrwx 1 user user 36 Jul 28 13:52 .examplerc -> ~/.dotfiles/examplerc
```
If you want to reverse this operation, use the `remove` command.
```
dfm remove ~/.examplerc
ls -al ~/.examplerc
-rw-r--r-- 1 user user 0 Jul 28 13:52 ~/.examplerc
```
The remove operation can also be used on the files in the dotfiles directory. e.g.
```
dfm remove ~/.dotfiles/examplerc
```

### Bootstrapping
Symlinks for an existing dotfiles directory can be created with the
`install` command.
```
dfm --dotfiles ~/.existingdotfiles install
```
If any files exist where a symlink would have been created, an
error message will be printed. The command can be repeated as many
times as necessary until all the problems are resolved. The `install`
command will never overwrite, delete, or move an existing file.

The symlinks can be removed with the `uninstall` command.
```
dfm --dotfiles ~/.existingdotfiles uninstall
```
This command will not delete any files unless they are symlinks to 
a file in the dotfiles directory.

Contributing
------------
This script was created because I felt the existing dotfiles tools
did more than was necessary and I wanted something more
minimal. I'm relucant to add more features to this script but feel
free to fork or open a pull request and I'll consider it. This script
is licensed with the [Unlicense](https://unlicense.org/) and you can
do with it as you please.
