# Bundled server binaries

This directory holds the platform-specific `gomc-rest` server binaries that the
Python package auto-launches (Pattern B):

| Platform        | File name                |
| --------------- | ------------------------ |
| Windows (amd64) | `gomc-rest.exe`          |
| Linux (amd64)   | `gomc-rest-linux-amd64`  |
| Linux (arm64)   | `gomc-rest-linux-arm64`  |

The binaries are **not committed to git**. They are vendored in at release time
from a pinned [gomc-rest](https://github.com/Moge800/gomc-rest) version, and each
platform wheel ships only its matching binary. `_binaries.py` resolves the
correct file for the current platform at runtime.
