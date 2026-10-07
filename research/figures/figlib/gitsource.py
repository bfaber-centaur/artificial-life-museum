"""Read evidence files at a pinned git commit, without checking that commit out.

Used when a figure must show evidence that is still under review (an unmerged PR). The
figure cites the exact commit, and nothing is copied into main. Every read is logged with
the commit, path, git blob id and SHA-256, so the manifest names precisely what was plotted.
"""
import csv
import hashlib
import io
import subprocess

from .provenance import REPO


class Pinned:
    def __init__(self, ref, label):
        self.commit = subprocess.run(["git", "rev-parse", ref], cwd=REPO, capture_output=True, text=True,
                                     check=True).stdout.strip()
        self.label = label
        self.reads = {}

    def bytes(self, path):
        spec = f"{self.commit}:{path}"
        data = subprocess.run(["git", "show", spec], cwd=REPO, capture_output=True, check=True).stdout
        blob = subprocess.run(["git", "rev-parse", spec], cwd=REPO, capture_output=True, text=True,
                              check=True).stdout.strip()
        self.reads[path] = {"commit": self.commit, "source": self.label, "path": path, "blob": blob,
                            "sha256": hashlib.sha256(data).hexdigest()}
        return data

    def csv(self, path):
        return list(csv.DictReader(io.StringIO(self.bytes(path).decode())))

    def text(self, path):
        return self.bytes(path).decode()

    def manifest(self):
        return [self.reads[p] for p in sorted(self.reads)]
