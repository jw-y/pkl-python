import atexit
import os
import platform
import signal
import stat
import subprocess
from pathlib import Path

import msgpack
import requests

BINARIES = {
    ("darwin", "64bit"): "pkl-macos-amd64",
    ("darwin", "aarch64"): "pkl-macos-aarch64",
    ("linux", "64bit"): "pkl-linux-amd64",
    ("linux", "aarch64"): "pkl-linux-aarch64",
    ("linux", "64bit", "alpine"): "pkl-alpine-linux-amd64",
}
PKL_VERSION = "0.25.3"
BASE_PATH = "https://github.com/apple/pkl/releases/download/"


def preexec_function():
    # Cause the child process to be terminated when the parent exits
    signal.signal(signal.SIGHUP, signal.SIG_IGN)


def detect_system():
    os_name = platform.system().lower()
    arch, _ = platform.architecture()
    return os_name, arch


def is_alpine_linux():
    return os.path.isfile("/etc/alpine-release")


def execute_binary(binary_path):
    subprocess.run([binary_path, "server"], check=True)


def download_binary(file, target_fp):
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


_PROCESSES = []


def terminate_processes():
    for process in _PROCESSES:
        process.terminate()
        process.wait()


atexit.register(terminate_processes)


class PKLServer:
    def __init__(self, cmd=None, debug=False):
        self.cmd = cmd or [get_binary_path(), "server"]
        self.next_request_id = 1
        self.unpacker = msgpack.Unpacker()

        env = {"PKL_DEBUG": "1"} if debug else {}

        self.process = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            bufsize=0,
            preexec_fn=preexec_function,
            env=env,
        )
        self.stdout = self.process.stdout
        self.stdin = self.process.stdin
        self.stderr = self.process.stderr
        self.closed = False

        os.set_blocking(self.stdout.fileno(), False)
        os.set_blocking(self.stderr.fileno(), False)
        _PROCESSES.append(self.process)

    def get_request_id(self):
        ret = self.next_request_id
        self.next_request_id += 1
        return ret

    def send(self, msg):
        if self.closed:
            raise ValueError("Server closed")
        self.stdin.write(msg)
        self.stdin.flush()

    def _read(self, stream):
        msg = None
        while msg is None:
            msg = stream.read()
        return msg

    def _receive(self, stream):
        while True:
            for unpacked in self.unpacker:
                return unpacked
            msg = self._read(stream)
            self.unpacker.feed(msg)

    def receive(self):
        if self.closed:
            raise ValueError("Server closed")
        return self._receive(self.stdout)

    def receive_err(self):
        if self.closed:
            raise ValueError("Server closed")
        msg = self.stderr.read()
        if msg is not None:
            print(msg.decode(), end="")

    def terminate(self):
        self.process.terminate()
        self.process.stdout.close()
        self.process.stderr.close()
        self.process.stdin.close()
        self.process.wait()
        self.closed = True
