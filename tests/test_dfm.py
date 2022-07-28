import os
import pytest
from dfm import dfm, Status
from pathlib import Path
from pytest import CaptureFixture


@pytest.fixture
def home_dir(tmp_path: Path):
    home_dir = (tmp_path / 'home')
    home_dir.mkdir()
    os.environ['HOME'] = str(home_dir)
    return home_dir


@pytest.fixture
def dotfiles_dir(home_dir: Path):
    dotfiles_dir = home_dir / '.dotfiles'
    os.environ['DOTFILES_HOME'] = str(dotfiles_dir) 
    return dotfiles_dir


def ensure_parent_dir(path: Path):
    if not path.parent.exists():
        path.parent.mkdir(parents=True)


def touch(path: Path) -> Path:
    ensure_parent_dir(path)
    path.touch()
    return path


def link(src: Path, dest: Path) -> Path:
    ensure_parent_dir(dest)
    dest.symlink_to(src)
    return dest


class TestAdd:
    def test_add_new_file(self, home_dir: Path, dotfiles_dir: Path):
        config_path = touch(home_dir / '.config/test')
        status = dfm(['add', str(config_path)])
        assert status == Status.OK
        assert (dotfiles_dir / 'config/test').exists()
        assert config_path.is_symlink()

    def test_file_must_exist(self, capsys: CaptureFixture[str]):
        status = dfm(['add', '.config/test'])
        assert status == Status.ERR
        assert 'does not exist' in capsys.readouterr()[1]

    def test_disallow_symlinks(self, capsys: CaptureFixture[str], home_dir: Path, dotfiles_dir: Path):
        config_path = touch(dotfiles_dir / 'config/test')
        link_path = link(config_path, home_dir / '.config/test')
        status = dfm(['add', str(link_path)])
        assert status == Status.ERR
        assert 'cannot add symlinks' in capsys.readouterr()[1]

    def test_disallow_files_in_dotfiles_dir(self, capsys: CaptureFixture[str], dotfiles_dir: Path):
        config_path = touch(dotfiles_dir / 'config/test')
        status = dfm(['add', str(config_path)])
        assert status == Status.ERR
        assert 'already in dotfiles directory' in capsys.readouterr()[1]

    def test_must_be_in_home_dir(self, capsys: CaptureFixture[str], tmp_path: Path):
        config_path = touch(tmp_path / 'etc/test')
        status = dfm(['add', str(config_path)])
        assert status == Status.ERR
        assert 'not in home directory' in capsys.readouterr()[1]

    def test_must_begin_with_dot(self, capsys: CaptureFixture[str], home_dir: Path):
        config_path = touch(home_dir / 'test')
        status = dfm(['add', str(config_path)])
        assert status == Status.ERR
        assert 'is not a dotfile' in capsys.readouterr()[1]

    def test_must_not_collide_with_existing_file(self, capsys: CaptureFixture[str], home_dir: Path, dotfiles_dir: Path):
        config_path = touch(home_dir / '.config/test')
        touch(dotfiles_dir / 'config/test')
        status = dfm(['add', str(config_path)])
        assert status == Status.ERR
        assert 'collides with existing file' in capsys.readouterr()[1]


class TestRemove:
    def test_rm_existing_file(self, home_dir: Path, dotfiles_dir: Path):
        config_path = touch(dotfiles_dir / 'config/test')
        link_path = link(config_path, home_dir / '.config/test')
        status = dfm(['rm', str(config_path)])
        assert status == Status.OK
        assert(not config_path.exists())
        assert(link_path.exists())
        assert(not link_path.is_symlink())

    def test_rm_existing_symlink(self, home_dir: Path, dotfiles_dir: Path):
        config_path = touch(dotfiles_dir / 'config/test')
        link_path = link(config_path, home_dir / '.config/test')
        status = dfm(['rm', str(link_path)])
        assert status == Status.OK
        assert(not config_path.exists())
        assert(link_path.exists())
        assert(not link_path.is_symlink())

    def test_file_must_exist(self, capsys: CaptureFixture[str]):
        status = dfm(['rm', '/.config/test'])
        assert status == Status.ERR
        assert 'does not exist' in capsys.readouterr()[1]

    def test_symlink_must_not_be_broken(self, capsys: CaptureFixture[str], home_dir: Path, dotfiles_dir: Path):
        config_path = touch(dotfiles_dir / 'config/test')
        link_path = link(config_path, home_dir / '.config/test')
        config_path.unlink()
        status = dfm(['rm', str(link_path)])
        assert status == Status.ERR
        assert 'does not exist' in capsys.readouterr()[1]

    def test_must_be_in_dotfiles_dir(self, capsys: CaptureFixture[str], home_dir: Path):
        config_path = touch(home_dir / '.config/test')
        status = dfm(['rm', str(config_path)])
        assert status == Status.ERR
        assert 'not in dotfiles directory' in capsys.readouterr()[1]

    def test_installed_file_must_be_symlink(self, capsys: CaptureFixture[str], home_dir: Path, dotfiles_dir: Path):
        touch(home_dir / '.config/test')
        config_path = touch(dotfiles_dir / 'config/test')
        status = dfm(['rm', str(config_path)])
        assert status == Status.ERR
        assert 'is not a symlink' in capsys.readouterr()[1]

    def test_must_link_to_correct_file(self, capsys: CaptureFixture[str], home_dir: Path, dotfiles_dir: Path):
        wrong_path = touch(dotfiles_dir / 'config/wrong')
        link(wrong_path, home_dir / '.config/test')
        config_path = touch(dotfiles_dir / 'config/test')
        status = dfm(['rm', str(config_path)])
        assert status == Status.ERR
        assert 'symlink to incorrect file' in capsys.readouterr()[1]


class TestInstall:
    def test_install_file(self, home_dir: Path, dotfiles_dir: Path):
        install_dir = home_dir / '.config/test'
        ensure_parent_dir(install_dir)
        touch(dotfiles_dir / 'config/test')
        status = dfm(['install'])
        assert status == Status.OK
        assert install_dir.exists()
        assert install_dir.is_symlink()

    def test_must_ignore_dotfiles(self, home_dir: Path, dotfiles_dir: Path):
        dest_path = home_dir / '.git'
        touch(dotfiles_dir / '.git')
        status = dfm(['install'])
        assert status == Status.OK
        assert not dest_path.exists()

    def test_file_must_not_exist(self, capsys: CaptureFixture[str], home_dir: Path, dotfiles_dir: Path):
        touch(home_dir / '.config/test')
        touch(dotfiles_dir / 'config/test')
        status = dfm(['install'])
        assert status == Status.ERR
        assert 'already exists' in capsys.readouterr()[1]


class TestUninstall:
    def test_uninstall_file(self, home_dir: Path, dotfiles_dir: Path):
        config_path = touch(dotfiles_dir / 'config/test')
        link_path = link(config_path, home_dir / '.config/test')
        status = dfm(['uninstall'])
        assert status == Status.OK
        assert not link_path.exists()
        assert config_path.exists()
        assert not config_path.is_symlink()
