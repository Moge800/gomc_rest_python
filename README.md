# gomc-rest (Python)

Python package for talking to Mitsubishi PLCs via
[gomc-rest](https://github.com/Moge800/gomc-rest) — **Pattern B**: the
`gomc-rest` server binary is bundled and auto-launched as a subprocess, so you
never have to start or distribute the executable yourself.

The HTTP layer is provided by
[gomc-rest-client](https://github.com/Moge800/gomc_rest_client); this package
adds only the bundled binary and its process lifecycle.

```text
your Python process
└─ gomc_rest.launch()
     ├─ spawns gomc-rest (bundled exe) on a free loopback port  ── MC protocol ──▶ PLC
     └─ returns a gomc_rest_client.PLCClient pointed at it
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

## Versions

This package bundles a pinned `gomc-rest` binary. The bundled server must
satisfy `gomc-rest-client`'s `MINIMUM_SUPPORTED_GOMC_REST_VERSION`
(currently **v1.3.0**); `launch()` verifies this on startup.

## Releasing / bundled binaries

The bundled server version is pinned in `GOMC_REST_VERSION`. Binaries are not
committed to git; they are fetched from the matching gomc-rest GitHub release.

- Locally: `python scripts/vendor_binaries.py` downloads all three binaries
  into `src/gomc_rest/binaries/`.
- On a `v*` tag, `.github/workflows/release.yml` builds one platform-specific
  wheel per OS (each bundling only its matching binary) and publishes to PyPI
  via trusted publishing.

To bump the bundled server, edit `GOMC_REST_VERSION` (keep it >= the client's
`MINIMUM_SUPPORTED_GOMC_REST_VERSION`) and cut a new tag.
