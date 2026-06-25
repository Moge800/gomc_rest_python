"""Locate the bundled gomc-rest server binary for the current platform."""

from __future__ import annotations

import platform
import stat
from pathlib import Path

_BINARIES_DIR = Path(__file__).parent / "binaries"

# (system, machine) -> bundled binary file name.
# Machine names are normalised to the keys below before lookup.
_BINARY_NAMES = {
    ("windows", "amd64"): "gomc-rest.exe",
    ("linux", "amd64"): "gomc-rest-linux-amd64",
    ("linux", "arm64"): "gomc-rest-linux-arm64",
}

_MACHINE_ALIASES = {
    "x86_64": "amd64",
    "amd64": "amd64",
    "aarch64": "arm64",
    "arm64": "arm64",
}


def _normalise_platform() -> tuple[str, str]:
    system = platform.system().lower()
    machine = _MACHINE_ALIASES.get(platform.machine().lower(), platform.machine().lower())
    return system, machine


def binary_path() -> Path:
    """Return the path to the bundled server binary for this platform.

    Raises RuntimeError if the platform is unsupported or the binary is missing
    from the package (e.g. a sdist install without the platform wheel).
    """
    system, machine = _normalise_platform()
    name = _BINARY_NAMES.get((system, machine))
    if name is None:
        raise RuntimeError(
            f"Unsupported platform {system}/{machine}. "
            f"gomc-rest ships binaries for: {sorted(_BINARY_NAMES)}."
        )

    path = _BINARIES_DIR / name
    if not path.exists():
        raise RuntimeError(
            f"Bundled server binary '{name}' was not found at {path}. "
            "Install the platform-specific wheel, or place the binary there "
            "(see gomc_rest/binaries/README.md)."
        )

    # sdists/VCS checkouts may drop the executable bit.
    if system != "windows":
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return path
