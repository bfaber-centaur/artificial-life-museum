"""Provenance manifests: which files, at which git revision, made which figure."""
import hashlib
import json
import pathlib
import platform
import subprocess

import matplotlib
import numpy

REPO = pathlib.Path(__file__).resolve().parents[3]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def last_commit(path):
    """Last commit that touched path (the revision of the data as plotted)."""
    return git("log", "-n", "1", "--format=%h", "--", str(path))


def manifest(figure_id, inputs, outputs, command, claims, notes=()):
    """Describe a figure build. Paths are recorded relative to the repo root."""
    rel = lambda p: str(pathlib.Path(p).resolve().relative_to(REPO))
    return {
        "figure": figure_id,
        "command": command,
        "claims": claims,
        "inputs": [{"path": rel(p), "sha256": sha256(p), "last_commit": last_commit(p)}
                   for p in sorted(set(map(str, inputs)))],
        "outputs": [rel(p) for p in outputs],
        "code_commit": git("rev-parse", "--short", "HEAD"),
        "code_dirty": bool(git("status", "--porcelain", "--", "research/figures")),
        "versions": {"python": platform.python_version(), "numpy": numpy.__version__,
                     "matplotlib": matplotlib.__version__},
        "notes": list(notes),
    }


def write_manifest(path, data):
    pathlib.Path(path).write_text(json.dumps(data, indent=2) + "\n")
