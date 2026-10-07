"""Provenance helpers: code version, environment and state fingerprints."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys

import numpy as np

from . import __version__
from .specimens import REPO_ROOT

# Paths whose uncommitted changes would make a run's commit hash a lie.
CODE_PATHS = ("src", "pyproject.toml")


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


def code_version() -> dict:
    commit = _git("rev-parse", "HEAD")
    commit = commit.strip() if commit else None
    status = _git("status", "--porcelain", "--", *CODE_PATHS)
    return {
        "package": "alm",
        "version": __version__,
        "git_commit": commit,
        "git_dirty": None if status is None else bool(status.strip()),
        "git_dirty_paths": [l[3:] for l in (status or "").splitlines() if l.strip()],
    }


def environment() -> dict:
    import scipy

    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
    }


def state_sha256(A: np.ndarray) -> str:
    """Bitwise fingerprint of a float64 state (little-endian, C order)."""
    return hashlib.sha256(np.ascontiguousarray(A, dtype="<f8").tobytes()).hexdigest()


def config_hash(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()
