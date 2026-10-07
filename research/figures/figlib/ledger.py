"""Read claim statuses from research/claims.md so figures never carry their own copy.

A figure declares which status each illustrated claim must have for its encoding to be
correct (e.g. a hatched "numerically fragile" row needs C027 to be NUMERICALLY_FRAGILE).
`require()` checks that against the ledger at build time and raises if the ledger has moved,
so a stale figure cannot be rebuilt silently. The badges are then drawn from the ledger's
own status text, and the manifest records the ledger's commit and hash: every rendered
figure is a dated snapshot of the ledger it was checked against.
"""
import pathlib
import re

from . import provenance as P

LEDGER = P.REPO / "research" / "claims.md"
VOCAB = ("INDEPENDENTLY_CHECKED", "NUMERICALLY_FRAGILE", "REPRODUCED", "OBSERVED", "CONJECTURED",
         "REFUTED")

_HEAD = re.compile(r"^### (C\d{3}) — (.*)$")
_STATUS = re.compile(r"^- \*\*Status:\*\*\s*(.*)$")
_FIELD = re.compile(r"^- \*\*")


class LedgerMismatch(RuntimeError):
    pass


def parse(path=LEDGER):
    """{claim_id: {"title", "status_text", "status"}}; status = first vocabulary word."""
    claims, cur, in_status = {}, None, False
    for line in pathlib.Path(path).read_text().splitlines():
        m = _HEAD.match(line)
        if m:
            cur = claims.setdefault(m.group(1), {"title": m.group(2).strip(), "status_text": ""})
            in_status = False
            continue
        if cur is None:
            continue
        m = _STATUS.match(line)
        if m:
            cur["status_text"], in_status = m.group(1).strip(), True
        elif in_status and line.startswith("  ") and not _FIELD.match(line):
            cur["status_text"] += " " + line.strip()
        else:
            in_status = False
    for c in claims.values():
        found = [(c["status_text"].find(v), v) for v in VOCAB if v in c["status_text"]]
        c["status"] = min(found)[1] if found else None
    return claims


def require(expected, path=LEDGER):
    """Check {claim_id: status} against the ledger; return the ledger entries used.

    Raises LedgerMismatch listing every claim whose primary status differs (or is missing),
    so the figure is redrawn deliberately rather than left wrong."""
    claims = parse(path)
    bad = [f"{cid}: figure expects {want}, ledger has {claims.get(cid, {}).get('status')}"
           for cid, want in expected.items() if claims.get(cid, {}).get("status") != want]
    if bad:
        raise LedgerMismatch("claims.md no longer matches this figure's encoding:\n  " + "\n  ".join(bad))
    return {cid: claims[cid] for cid in expected}


def snapshot(expected, path=LEDGER):
    """Manifest block: ledger revision plus the status text each claim had when checked."""
    used = require(expected, path)
    return {
        "ledger": str(pathlib.Path(path).resolve().relative_to(P.REPO)),
        "ledger_commit": P.last_commit(path),
        "ledger_sha256": P.sha256(path),
        "claims": {cid: {"status": c["status"], "status_text": c["status_text"], "title": c["title"]}
                   for cid, c in used.items()},
    }
