import atexit
import os
import signal
import subprocess

import msgpack


def preexec_function():
    # Cause the child process to be terminated when the parent exits
    signal.signal(signal.SIGHUP, signal.SIG_IGN)


_PROCESSES = []


def terminate_processes():
    for process in _PROCESSES:
        process.terminate()
        process.wait()


atexit.register(terminate_processes)


class PKLServer:
    def __init__(self, cmd=None, debug=False):
        from pkl.binary_manager import BinaryManager

        manager = BinaryManager()
        binary_path = manager.get_binary_filepath()

        self.cmd = cmd or [binary_path, "server"]
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
