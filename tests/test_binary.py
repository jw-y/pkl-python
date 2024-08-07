import os
from pathlib import Path

import pytest

import pkl
from pkl.binary_manager import BinaryManager


def test_latest_release():
    manager = BinaryManager()
    manager.get_latest_pkl_release_url()


def remove_pkl_from_path(monkeypatch):
    manager = BinaryManager()
    path = manager.is_command_available()
    if path is None:
        return
    path = path.rsplit("/", 1)[0]
    original_path = os.environ.get("PATH", "")
    paths = original_path.split(os.pathsep)
    paths = [p for p in paths if path not in p]
    monkeypatch.setenv("PATH", os.pathsep.join(paths))


def remove_pkl_binary():
    path = Path(pkl.__file__)
    ls = list((path.parent / "bin").iterdir())
    if len(ls) == 0:
        return
    assert len(ls) == 1
    binary_path = ls[0]
    os.remove(binary_path)
    return binary_path


def test_download_binary(capfd, monkeypatch: pytest.MonkeyPatch):
    remove_pkl_binary()
    remove_pkl_from_path(monkeypatch)
    manager = BinaryManager()
    out, _ = capfd.readouterr()
    assert out.startswith("Successfully installed")
    removed = remove_pkl_binary()

    assert manager.binary_path == removed


def test_binary_file_exists():
    manager = BinaryManager()
    fp = manager.get_binary_filepath()
    assert os.path.exists(fp), f"Binary file not found at {fp}"


def test_binary_manager_exists():
    manager = BinaryManager()
    manager.is_command_available()


def test_detect_system():
    manager = BinaryManager()
    os_name, arch = manager.detect_system()
    assert os_name == "linux"
    assert arch == "AMD64"
    url = manager._determine_binary_url()
    assert url.endswith("pkl-linux-amd64")
