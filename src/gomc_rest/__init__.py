"""gomc-rest (Python, Pattern B).

Bundles the gomc-rest server binary, auto-launches it as a subprocess, and
hands back a PLCClient (from gomc-rest-client) pointed at it. The HTTP layer is
provided entirely by gomc-rest-client; this package only adds binary bundling
and process lifecycle.

    import gomc_rest

    with gomc_rest.launch(plc_host="192.168.0.1") as plc:
        plc.read("D100", 3)
"""

from __future__ import annotations

from gomc_rest_client import (
    GomcRestBusyError,
    GomcRestPLCProtocolError,
    PLCClient,
)

from ._server import Server

__version__ = "0.1.0"


def launch(
    plc_host: str = "192.168.0.1",
    plc_port: int = 5007,
    server_mode: bool = False,
    extra_args: list[str] | None = None,
    startup_timeout: float = 10.0,
) -> Server:
    """Start the bundled gomc-rest server and return a managed Server.

    Use as a context manager to get the PLCClient and auto-stop the server::

        with gomc_rest.launch(plc_host="192.168.0.1") as plc:
            plc.read("D100", 3)

    By default the server binds to loopback only, so no other app or host can
    reach it. Set ``server_mode=True`` to bind all interfaces and let other
    apps on the network call the REST API (the server has no auth/TLS — only
    expose it on a trusted network).

    ``extra_args`` are passed through to the gomc-rest binary (e.g.
    ``["-enable-remote"]`` or ``["-readonly"]``).
    """
    return Server(
        plc_host=plc_host,
        plc_port=plc_port,
        server_mode=server_mode,
        extra_args=extra_args,
        startup_timeout=startup_timeout,
    )


__all__ = [
    "launch",
    "Server",
    "PLCClient",
    "GomcRestBusyError",
    "GomcRestPLCProtocolError",
    "__version__",
]
