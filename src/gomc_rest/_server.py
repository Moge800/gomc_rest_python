"""Launch and manage the bundled gomc-rest server as a subprocess (Pattern B)."""

from __future__ import annotations

import atexit
import socket
import subprocess
import time

from gomc_rest_client import PLCClient

from ._binaries import binary_path


def _free_port() -> int:
    """Pick a currently-free TCP port on the loopback interface."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class Server:
    """Owns a gomc-rest subprocess and a PLCClient pointed at it.

    Prefer the context-manager form::

        with Server(plc_host="192.168.0.1") as plc:
            plc.read("D100", 3)

    When not used as a context manager the subprocess is still terminated at
    interpreter exit via atexit.
    """

    def __init__(
        self,
        plc_host: str = "192.168.0.1",
        plc_port: int = 5007,
        extra_args: list[str] | None = None,
        startup_timeout: float = 10.0,
    ) -> None:
        self._port = _free_port()
        self.base_url = f"http://127.0.0.1:{self._port}"

        args = [
            str(binary_path()),
            "-listen", f":{self._port}",
            "-host", plc_host,
            "-port", str(plc_port),
            *(extra_args or []),
        ]
        self._proc = subprocess.Popen(args)
        atexit.register(self.close)

        self.client = PLCClient(self.base_url)
        self._wait_until_healthy(startup_timeout)
        self._check_version()

    def _wait_until_healthy(self, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._proc.poll() is not None:
                raise RuntimeError(
                    f"gomc-rest exited during startup (code {self._proc.returncode})."
                )
            try:
                self.client.health()
                return
            except Exception:
                time.sleep(0.1)
        self.close()
        raise TimeoutError(f"gomc-rest did not become healthy within {timeout}s.")

    def _check_version(self) -> None:
        if not self.client.is_supported_version():
            self.close()
            raise RuntimeError(
                f"Bundled gomc-rest {self.client.version()} is not supported by "
                "the installed gomc-rest-client. Update the bundled binary."
            )

    def close(self) -> None:
        """Terminate the subprocess. Safe to call more than once."""
        proc = getattr(self, "_proc", None)
        if proc is None or proc.poll() is not None:
            return
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

    def __enter__(self) -> PLCClient:
        return self.client

    def __exit__(self, *exc) -> None:
        self.close()
