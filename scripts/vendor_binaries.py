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
import hashlib
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
_CHECKSUMS = _ROOT / "checksums"


def _version() -> str:
    env = os.environ.get("GOMC_REST_VERSION")
    if env:
        return env.strip()
    return (_ROOT / "GOMC_REST_VERSION").read_text().strip()


def _expected_checksums(version: str) -> dict[str, str]:
    """Load the trusted SHA-256 values pinned in this repo for `version`.

    These are committed, not fetched from the same release, so swapping a
    release asset after the fact is detected. Missing file -> fail closed.
    """
    path = _CHECKSUMS / f"{version}.sha256"
    if not path.exists():
        raise RuntimeError(
            f"No pinned checksums for {version} at {path}. Add the trusted "
            "SHA-256 values before vendoring."
        )
    sums: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        digest, name = line.split()
        sums[name] = digest
    return sums


def _download(version: str, asset: str, expected: dict[str, str]) -> None:
    url = f"https://github.com/{REPO}/releases/download/{version}/{asset}"
    out = _DEST / asset
    print(f"  {asset} <- {url}")
    urllib.request.urlretrieve(url, out)

    want = expected.get(asset)
    if want is None:
        out.unlink(missing_ok=True)
        raise RuntimeError(f"No pinned checksum for {asset} in {version}.sha256.")
    got = hashlib.sha256(out.read_bytes()).hexdigest()
    if got != want:
        out.unlink(missing_ok=True)
        raise RuntimeError(
            f"Checksum mismatch for {asset}: expected {want}, got {got}."
        )

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
    expected = _expected_checksums(version)
    targets = [args.only] if args.only else ASSETS
    _DEST.mkdir(parents=True, exist_ok=True)
    print(f"Vendoring gomc-rest {version} into {_DEST}")
    for asset in targets:
        _download(version, asset, expected)
    print("Done (checksums verified).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
