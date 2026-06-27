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

## Versions

This package bundles a pinned `gomc-rest` binary. The bundled server must
satisfy `gomc-rest-client`'s `MINIMUM_SUPPORTED_GOMC_REST_VERSION`
(currently **v1.3.0**); `launch()` verifies this on startup.

## Status

Early scaffold. The binaries are vendored at release time (see
`src/gomc_rest/binaries/README.md`) and are not committed to git.
