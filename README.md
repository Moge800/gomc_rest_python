# gomc-rest (Python)

English / [日本語](https://github.com/Moge800/gomc_rest_python/blob/main/README_JP.md)

**A Python library for talking to Mitsubishi PLCs.** Read and write PLC devices
over the MC protocol (3E/4E frames) — the protocol is handled for you by a bundled
[gomc-rest](https://github.com/Moge800/gomc-rest) server that the package
auto-launches, so you never have to start or distribute an executable yourself.

**Bonus — expose a REST API.** Enable `server_mode` to make the bundled
server's REST API reachable from other apps on your network (a GUI, another
machine, another language); and `connect()` talks to a gomc-rest server that is
already running elsewhere. See [Access control](#access-control).

Under the hood the HTTP layer is provided by
[gomc-rest-client](https://github.com/Moge800/gomc_rest_client); this package
adds the bundled binary and its process lifecycle.

```text
your Python process
└─ gomc_rest.launch()
     ├─ spawns the bundled gomc-rest on a free loopback port  ── MC protocol ──▶ PLC
     └─ returns a Server that provides a PLCClient pointed at it
```

## Install

```bash
pip install gomc-rest
```

## Usage

```python
import gomc_rest

with gomc_rest.launch(plc_host="192.168.0.1") as plc:
    values = plc.read("D100", 3)
    plc.write("D100", [10, 20, 30])
# the bundled server is stopped automatically on exit
```

`launch()` returns a `Server`; using it as a context manager yields a
`PLCClient` (see gomc-rest-client for the full read/write/remote API) and stops
the server on exit. Without `with`, the server is stopped at interpreter exit.

Pass server flags through `extra_args`:

```python
with gomc_rest.launch(plc_host="192.168.0.1", extra_args=["-enable-remote"]) as plc:
    plc.remote_run()
```

### Client mode (connect to an existing server)

To talk to a gomc-rest server that is already running elsewhere — a shared
instance, another machine, or one you launched with `server_mode=True` — use
`connect()` instead of starting the bundled binary:

```python
with gomc_rest.connect("http://192.168.0.1:8080", token="...") as plc:
    plc.read("D100", 3)
```

Both `launch()` and `connect()` hand you the same `PLCClient`, so one package
covers "bundle and run the server" and "just be a client".

`connect()` needs no bundled binary, so it works even on platforms without a
prebuilt wheel (macOS, Windows arm64, glibc < 2.34): there `pip install
gomc-rest` installs from the sdist, and only `launch()` is unavailable (it
raises a clear error).

## Access control

Two independent layers protect the server, both on by default:

1. **Per-launch bearer token.** A random token is generated each launch and
   required by the server, so even another process on the same host that
   discovers the port cannot call the API. It is set automatically on the
   returned client and exposed as `server.token`. Pass an explicit `token=` to
   share with another app, or `token=""` to disable auth (closed-network use).
2. **Loopback binding.** By default the server binds to `127.0.0.1`, so no
   other host can reach it.

Set `server_mode=True` to bind all interfaces so other apps on the network
(e.g. gomc-rest-gui, curl from another machine) can call it — give them
`server.token`:

```python
server = gomc_rest.launch(plc_host="192.168.0.1", server_mode=True)
print(server.base_url)   # other apps connect to http://<this-host>:<port>
print(server.token)      # ...with this bearer token
try:
    server.client.read("D100", 3)
finally:
    server.close()
```

The server has no TLS — only enable `server_mode` on a trusted network.

**Threat model.** The token is passed to the server via the `GOMCR_TOKEN`
environment variable (not the command line), so it does not appear in the
process list. It protects against other hosts and other OS users. It does
**not** protect against another process running as the **same OS user**, which
can read the server's environment (e.g. `/proc/<pid>/environ`); the OS user
boundary is the trust boundary here.

## Versions

This package bundles a pinned `gomc-rest` binary (currently **v1.4.0**, set in
`GOMC_REST_VERSION`) that must satisfy `gomc-rest-client`'s
`MINIMUM_SUPPORTED_GOMC_REST_VERSION`; `launch()` verifies this on startup. The
`gomc-rest-client` dependency is capped (`>=0.10.0,<0.11`) so a future client
that raises its minimum server version can't be installed without also bumping
the bundled binary.

## Development

Release procedure and bundled-binary maintenance are documented in
[RELEASING.md](https://github.com/Moge800/gomc_rest_python/blob/main/RELEASING.md).
