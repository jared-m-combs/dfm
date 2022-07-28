#!/usr/bin/env python3
import sys
import os
import shutil
from argparse import ArgumentParser
from pathlib import Path
from enum import IntFlag
from typing import Iterable, Callable


class Status(IntFlag):
    OK = 0
    ERR = 1


def main(argv: list[str]) -> Status:
    args = argparse().parse_args(argv)
    dotfiles_home = ensure_dir(Path(args.dotfiles))
    if hasattr(args, 'paths'):
        paths = (Path(p) for p in args.paths)
    else:
        paths = dotfiles_home.iterdir()
    return fold(dotfiles_home, paths, args.func)


def argparse() -> ArgumentParser:
    default_dotfiles_home = os.environ.get('DOTFILES_HOME', '~/.dotfiles') 

    parser = ArgumentParser(prog='dfm', description="""
        Tool for managing dotfiles in a separate directory with symlinks to their original locations.
        Includes commands for adding files to and removing files from this directory.
        An existing dotfiles directory can be bootstrapped with the 'install' command and
        all symlinks can be removed with the 'uninstall' command.
        """)

    parser.add_argument('--dotfiles', '-d', default=default_dotfiles_home, help="""
        Directory where dotfiles are stored. Defaults to the 'DOTFILE_HOME' \
        environment variable if specified or to '~/.dotfiles' otherwise.""")
    subparsers = parser.add_subparsers(required=True)

    parser_add = subparsers.add_parser('add', aliases=['a'], help="""
        Moves the file to the dotfiles directory and leaves a symlink in its place.""")
    parser_add.add_argument('paths', type=str, nargs='+', help="""
        The paths of the files to add to the dotfiles directory.""")
    parser_add.set_defaults(func=add)

    parser_remove = subparsers.add_parser('remove', aliases=['r', 'rm'], help="""
        Removes the symlink and restores the file from the dotfiles directory to its original location.""")
    parser_remove.add_argument('paths', type=str, nargs ='+', help="""
        The paths can be either the symlinks or the actual files in the dotfiles directory.""")
    parser_remove.set_defaults(func=remove)
    
    parser_install = subparsers.add_parser('install', aliases=['i'], help="""
        Adds symlinks for all of the non-hidden files in the dotfiles directory.""")
    parser_install.set_defaults(func=install)

    parser_uninstall = subparsers.add_parser('uninstall', aliases=['u'], help="""
        Removes symlinks for all of the files in the dotfiles directory.""")
    parser_uninstall.set_defaults(func=uninstall)

    return parser


def err(path: Path, msg: str) -> Status:
    print(f'{path}: {msg}', file=sys.stderr)
    return Status.ERR


def ensure_dir(path: Path) -> Path:
    path = path.expanduser().resolve()
    if not path.exists():
        path.mkdir(parents = True)
    return path


def fold(dotfiles_home: Path, paths: Iterable[Path], op: Callable[[Path,Path],Status]) -> Status:
    exit_status = Status.OK
    for path in paths:
        exit_status |= op(dotfiles_home, path)
    return exit_status


def add(dotfiles_home: Path, path: Path) -> Status:
    src_path = Path(path).expanduser().absolute()
     
    if not src_path.exists():
        return err(path, 'does not exist')

    if src_path.is_symlink():
        return err(path, 'cannot add symlinks')

    if src_path.is_relative_to(dotfiles_home):
        return err(path, 'is already in dotfiles directory')

    if not src_path.is_relative_to(Path.home()):
        return err(path, 'not in home directory')

    src_path = src_path.resolve()
    relative_path = src_path.relative_to(Path.home())
    dest_path = dotfiles_home / str(relative_path)[1:]

    if not str(relative_path).startswith('.'):
        return err(path, 'is not a dotfile')

    if dest_path.exists():
        return err(path, 'collides with existing file in dotfiles directory')

    ensure_dir(dest_path.parent)
    shutil.move(str(src_path), str(dest_path))
    src_path.symlink_to(dest_path)
    return Status.OK


def remove(dotfiles_home: Path, path: Path) -> Status:
    src_path = path.expanduser().resolve()

    if not src_path.exists():
        return err(path, 'does not exist')

    if not src_path.is_relative_to(dotfiles_home):
        return err(path, 'not in dotfiles directory')

    relative_path = src_path.relative_to(dotfiles_home)
    dest_path = Path.home() / ('.' + str(relative_path))

    if not dest_path.is_symlink():
        return err(path, 'is not a symlink')

    if dest_path.readlink() != src_path:
        return err(path, 'symlink to incorrect file')

    dest_path.unlink()
    shutil.move(str(src_path), str(dest_path))
    return Status.OK


def install(dotfiles_home: Path, path: Path) -> Status:
    relative_path = path.relative_to(dotfiles_home)
    dest_path = Path.home() / ('.' + str(relative_path))

    if str(relative_path).startswith('.'):
        return Status.OK

    if dest_path.is_symlink() and dest_path.readlink() == path:
        return Status.OK

    if dest_path.is_dir():
        return fold(dotfiles_home, path.iterdir(), install)

    if dest_path.exists():
        return err(dest_path, 'already exists')

    dest_path.symlink_to(path)
    return Status.OK


def uninstall(dotfiles_home: Path, path: Path) -> Status:
    relative_path = path.relative_to(dotfiles_home)
    dest_path = Path.home() / ('.' + str(relative_path))

    if str(relative_path).startswith('.'):
        return Status.OK

    if dest_path.is_symlink() and dest_path.readlink() == path:
        dest_path.unlink()
        return Status.OK

    if dest_path.is_dir():
        return fold(dotfiles_home, path.iterdir(), uninstall)

    return Status.OK


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]).value)
