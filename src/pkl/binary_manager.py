import argparse
import os
import platform
import stat
import subprocess
from functools import cache
from pathlib import Path

import requests

ARM_BINARIES = {
    "darwin": "pkl-macos-aarch64",
    "linux": "pkl-linux-aarch64",
}
AMD64_BINARIES = {
    "darwin": "pkl-macos-amd64",
    "linux": "pkl-linux-amd64",
    "alpine-linux": "pkl-alpine-linux-amd64",
    "windows": "pkl-windows-amd64.exe",
}
# PKL_VERSION = "0.26.3"
# BASE_PATH = "https://github.com/apple/pkl/releases/download/"


class BinaryManager:
    def __init__(self, download_binary=True):
        binary_fp = self.is_command_available() or self._downloaded_binary_path()
        need_to_download = binary_fp is None
        if download_binary and need_to_download:
            binary_dir = self._default_bin_dir()
            binary_url: str = self._determine_binary_url()
            binary_fp = self.download_binary(binary_dir, binary_url)

        self.binary_path = binary_fp

        # self.binary_dir: Path = binary_dir or self._default_bin_dir()
        # self.binary_name: str = binary_name or self._determine_binary_name()
        # self.binary_path: Path = self.binary_dir / self.binary_name
        # self.binary_base_url = BASE_PATH + PKL_VERSION + "/"
        # self.binary_url = self.binary_base_url + self.binary_path.name

    def _downloaded_binary_path(self):
        binary_dir: Path = self._default_bin_dir()
        if not binary_dir.exists():
            return None
        ls = list(binary_dir.iterdir())

        if len(ls) == 0:
            return None
        elif len(ls) == 1:
            return Path(ls[0])
        else:
            raise Exception("Something went wrong")

    @cache
    def get_latest_pkl_release_urls(self):
        url = "https://api.github.com/repos/apple/pkl/releases/latest"
        response = requests.get(url)
        release = response.json()
        assets = release["assets"]
        urls = {a["name"]: a["browser_download_url"] for a in assets}
        return urls

    def is_command_available(self):
        """
        Check if a command is available in the system's PATH.
        """
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["where", "pkl"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            else:
                result = subprocess.run(
                    ["which", "pkl"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            return result.stdout.decode().splitlines()[0].strip()
        except subprocess.CalledProcessError:
            return None

    def download_binary(self, binary_dir: Path, binary_url: str):
        binary_dir.mkdir(exist_ok=True, parents=True)
        return self._download_and_save_binary(binary_url, binary_dir)

    def get_binary_filepath(self):
        return str(self.binary_path)

    def detect_system(self):
        def is_alpine_linux():
            return os.path.isfile("/etc/alpine-release")

        def detect_processor_architecture():
            architecture = platform.machine().lower()
            if "arm" in architecture or "aarch64" in architecture:
                return "ARM"
            elif "x86_64" in architecture or "amd64" in architecture:
                return "AMD64"
            else:
                return None

        os_name = platform.system().lower()
        if os_name == "linux" and is_alpine_linux():
            os_name = "alpine-linux"
        arch = detect_processor_architecture()
        return os_name, arch

    def _determine_binary_url(self) -> str:
        os_name, arch = self.detect_system()
        if arch == "ARM":
            bin_name = ARM_BINARIES.get(os_name)
        else:
            bin_name = AMD64_BINARIES.get(os_name)

        if bin_name is None:
            raise OSError(
                f"No compatible binary found for your system: {os_name}, {arch}"
            )
        name_to_url_map = self.get_latest_pkl_release_urls()
        url = name_to_url_map[bin_name]
        return url

    @classmethod
    def _default_bin_dir(cls) -> Path:
        bin_dir = Path(__file__).parent / "bin"
        return bin_dir

    """
    def download_all_binary(self):
        download_dir = self._default_bin_dir()
        download_dir.mkdir(exist_ok=True)
        for filename in BINARIES.values():
            url = self.binary_base_url + filename
            self._download_and_save_binary(url, download_dir)
    """

    @classmethod
    def _fetch_binary(cls, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    @classmethod
    def _download_and_save_binary(
        cls, url, target_dir: Path, filename=None, skip_exists=True
    ) -> Path:
        assert target_dir.is_dir()
        content = cls._fetch_binary(url)

        default_filename = Path(url).name
        binary_fp = target_dir / (filename or default_filename)

        if skip_exists and binary_fp.exists():
            return binary_fp

        with open(binary_fp, "wb") as f:
            f.write(content)
        print(f"Successfully installed {binary_fp}")
        os.chmod(binary_fp, os.stat(binary_fp).st_mode | stat.S_IXUSR)
        return binary_fp

    def check(self):
        cmd = [self.binary_path, "-v"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        stdout = result.stdout
        return stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary_dir")
    args = parser.parse_args()

    binary_dir = Path(args.binary_dir)
    manager = BinaryManager(binary_dir=binary_dir)
    manager.download_all_binary()


if __name__ == "__main__":
    main()
