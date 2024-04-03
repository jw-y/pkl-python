import os
import platform
import stat
from pathlib import Path

import setuptools
from setuptools.command.install import install

BINARIES = {
    ("darwin", "64bit"): "pkl-macos-amd64",
    ("darwin", "aarch64"): "pkl-macos-aarch64",
    ("linux", "64bit"): "pkl-linux-amd64",
    ("linux", "aarch64"): "pkl-linux-aarch64",
    ("linux", "64bit", "alpine"): "pkl-alpine-linux-amd64",
}
PKL_VERSION = "0.25.3"
BASE_PATH = "https://github.com/apple/pkl/releases/download/"


def detect_system():
    os_name = platform.system().lower()
    arch, _ = platform.architecture()
    return os_name, arch


def is_alpine_linux():
    return os.path.isfile("/etc/alpine-release")


def download_binary(file, target_fp):
    import requests

    url = BASE_PATH + PKL_VERSION + "/" + file
    response = requests.get(url)
    with open(target_fp, "wb") as f:
        f.write(response.content)


def get_binary_path():
    os_name, arch = detect_system()
    if os_name == "linux" and is_alpine_linux():
        os_name = "alpine"
    binary_key = (os_name, arch)
    if binary_key == ("linux", "64bit") and is_alpine_linux():
        binary_key += ("alpine",)
    bin_file = BINARIES.get(binary_key)

    if bin_file is None:
        raise OSError("No compatible binary found for your system.")

    bin_parent_path = (Path("~/.pkl/bin/") / PKL_VERSION).expanduser()
    binary_path = bin_parent_path / bin_file

    if not binary_path.exists():
        binary_path.parent.mkdir(exist_ok=True, parents=True)
        download_binary(bin_file, binary_path)

    current_permissions = os.stat(binary_path).st_mode
    new_permissions = current_permissions | stat.S_IXUSR
    os.chmod(binary_path, new_permissions)

    return binary_path


class CustomInstallCommand(install):
    def run(self):
        get_binary_path()
        install.run(self)


setuptools.setup(
    cmdclass={"install": CustomInstallCommand},
    setup_requires=["requests"],
)
