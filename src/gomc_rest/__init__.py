"""gomc-rest (Python, Pattern B).

Bundles the gomc-rest server binary and offers two entry points over the same
PLCClient (from gomc-rest-client):

* ``launch()`` — auto-start the bundled server as a subprocess (optionally
  exposed to the network) and talk to it.
* ``connect()`` — act as a client to a gomc-rest server that is already
  running elsewhere, without starting anything.

The HTTP layer is provided entirely by gomc-rest-client; this package only adds
binary bundling and process lifecycle.

    import gomc_rest

    with gomc_rest.launch(plc_host="192.168.0.1") as plc:
        plc.read("D100", 3)

    plc = gomc_rest.connect("http://192.168.0.1:8080", token="...")
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


def connect(
    base_url: str = "http://127.0.0.1:8080",
    token: str | None = None,
) -> PLCClient:
    """Return a PLCClient for a gomc-rest server that is already running.

    Use this to talk to a server started elsewhere — another machine, a shared
    instance, or one you launched with ``server_mode=True`` — without spawning
    the bundled binary. Supports the context-manager protocol::

        with gomc_rest.connect("http://192.168.0.1:8080", token="...") as plc:
            plc.read("D100", 3)

    For the bundled, auto-started server use ``launch()`` instead.
    """
    return PLCClient(base_url, token=token)


__all__ = [
    "launch",
    "connect",
    "Server",
    "PLCClient",
    "GomcRestBusyError",
    "GomcRestPLCProtocolError",
    "GomcRestUnauthorizedError",
    "__version__",
]
