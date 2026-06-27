"""Smoke test: the bundled server starts with default settings and is healthy.

Skipped automatically when the server binary has not been vendored (so the
suite still passes locally without a download); CI vendors it first.
"""

from __future__ import annotations

import pytest

import gomc_rest
from gomc_rest._binaries import binary_path


def _binary_available() -> bool:
    try:
        binary_path()
        return True
    except RuntimeError:
        return False


pytestmark = pytest.mark.skipif(
    not _binary_available(), reason="server binary not vendored"
)


def test_launch_default_is_healthy():
    # Default settings generate a random token and pass it to both ends.
    with gomc_rest.launch() as plc:
        assert isinstance(plc.health(), dict)


def test_launch_auth_disabled():
    server = gomc_rest.launch(token="")
    try:
        assert server.token is None
        assert isinstance(server.client.health(), dict)
    finally:
        server.close()
