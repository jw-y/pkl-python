import os
from pathlib import Path

import pytest

import pkl
from pkl.binary_manager import BinaryManager


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


def test_latest_release():
    manager = BinaryManager()
    urls = manager.get_latest_pkl_release_urls()
    assert len(urls) == 7


def test_without_download_binary():
    manager = BinaryManager()
    output = manager.check()
    assert output.lower().startswith("pkl")


def test_download_binary(monkeypatch: pytest.MonkeyPatch):
    remove_pkl_binary()
    remove_pkl_from_path(monkeypatch)
    manager = BinaryManager()
    output = manager.check()
    assert output.lower().startswith("pkl")

    removed = remove_pkl_binary()
    assert manager.binary_path == removed


def test_binary_file_exists():
    manager = BinaryManager()
    manager.is_command_available()

    fp = manager.get_binary_filepath()
    assert os.path.exists(fp), f"Binary file not found at {fp}"
