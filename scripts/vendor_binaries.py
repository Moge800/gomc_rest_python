#!/usr/bin/env python3
"""Download the pinned gomc-rest server binaries into the package.

The binaries are not committed to git; this script fetches them from the
gomc-rest GitHub release named in the GOMC_REST_VERSION file (override with
the GOMC_REST_VERSION env var) and writes them into src/gomc_rest/binaries/.

Usage:
    python scripts/vendor_binaries.py            # all platforms
    python scripts/vendor_binaries.py --only gomc-rest-linux-amd64
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.request
from pathlib import Path

REPO = "Moge800/gomc-rest"
ASSETS = [
    "gomc-rest.exe",
    "gomc-rest-linux-amd64",
    "gomc-rest-linux-arm64",
]

_ROOT = Path(__file__).resolve().parent.parent
_DEST = _ROOT / "src" / "gomc_rest" / "binaries"


def _version() -> str:
    env = os.environ.get("GOMC_REST_VERSION")
    if env:
        return env.strip()
    return (_ROOT / "GOMC_REST_VERSION").read_text().strip()


def _download(version: str, asset: str) -> None:
    url = f"https://github.com/{REPO}/releases/download/{version}/{asset}"
    out = _DEST / asset
    print(f"  {asset} <- {url}")
    urllib.request.urlretrieve(url, out)
    if not asset.endswith(".exe"):
        out.chmod(0o755)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        choices=ASSETS,
        help="Download a single binary instead of all (used for per-platform wheels).",
    )
    args = parser.parse_args()

    version = _version()
    targets = [args.only] if args.only else ASSETS
    _DEST.mkdir(parents=True, exist_ok=True)
    print(f"Vendoring gomc-rest {version} into {_DEST}")
    for asset in targets:
        _download(version, asset)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
