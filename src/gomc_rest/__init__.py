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
    GomcRestUnauthorizedError,
    PLCClient,
)

from ._server import Server

__version__ = "0.1.0"


def launch(
    plc_host: str = "192.168.0.1",
    plc_port: int = 5007,
    server_mode: bool = False,
    token: str | None = None,
    extra_args: list[str] | None = None,
    startup_timeout: float = 10.0,
) -> Server:
    """Start the bundled gomc-rest server and return a managed Server.

    Use as a context manager to get the PLCClient and auto-stop the server::

        with gomc_rest.launch(plc_host="192.168.0.1") as plc:
            plc.read("D100", 3)

    A random bearer token is generated per launch and required by the server,
    so even another process on this host that learns the port cannot call the
    API. Pass an explicit ``token`` to share with another app, or ``token=""``
    to disable auth (closed-network use). The token is available as
    ``server.token``.

    By default the server also binds to loopback only. Set ``server_mode=True``
    to bind all interfaces and let other apps on the network call the REST API
    (give them ``server.token``). The server has no TLS — only expose it on a
    trusted network.

    ``extra_args`` are passed through to the gomc-rest binary (e.g.
    ``["-enable-remote"]`` or ``["-readonly"]``).
    """
    return Server(
        plc_host=plc_host,
        plc_port=plc_port,
        server_mode=server_mode,
        token=token,
        extra_args=extra_args,
        startup_timeout=startup_timeout,
    )


__all__ = [
    "launch",
    "Server",
    "PLCClient",
    "GomcRestBusyError",
    "GomcRestPLCProtocolError",
    "GomcRestUnauthorizedError",
    "__version__",
]
