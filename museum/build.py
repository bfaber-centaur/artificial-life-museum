"""Build the ALM static museum from museum/rooms/*.html into museum/site/.

The museum never carries its own copy of a scientific fact it can read instead:

- Claim statuses come from research/claims.md through Lane 9's parser (figlib.ledger), and
  badge words and colours from research/figures/conventions.json.
- Each room declares the status its prose assumes for every claim it cites ("expect"). If the
  ledger has moved, the build stops, so a room is rewritten deliberately rather than left
  saying something the ledger no longer supports.
- Every image, video and source link must name a file that exists in the repository, and
  every room must cite at least one source.

Room files are HTML fragments with a JSON header comment and these directives:

    {{claim:C038}}           claim chip: ID + status badge, links to the claims page
    {{status:C038}}          the ledger's full status text for that claim
    {{src:path|label}}       link to a repository file or folder on GitHub (must exist)
    {{asset:path}}           relative URL of a repository file for <img>/<video> (must exist)
    {{page:slug|label}}      link to another museum page (must exist)
    {{pr:27|label}}          link to an open pull request; only in a room marked "provisional"
                             that lists the number under "under_review"

A provisional room shows work that has not reached main or the ledger yet. It gets a banner
saying so, and its prose must attribute every such finding to the PR it comes from.

Usage (from the repo root): .venv/bin/python museum/build.py [--out DIR]
"""
import argparse
import hashlib
import html
import json
import os
import pathlib
import re
import subprocess
import sys

MUSEUM = pathlib.Path(__file__).resolve().parent
REPO = MUSEUM.parent
ROOMS = MUSEUM / "rooms"
SITE = MUSEUM / "site"
LEDGER = REPO / "research" / "claims.md"
CONVENTIONS = REPO / "research" / "figures" / "conventions.json"
GITHUB = "https://github.com/bfaber-centaur/artificial-life-museum"

sys.path.insert(0, str(REPO / "research" / "figures"))
from figlib import ledger  # noqa: E402  (Lane 9's parser: one reading of the ledger for everyone)

_HEADER = re.compile(r"\A\s*<!--meta\s*(\{.*?\})\s*-->\s*", re.S)
_DIRECTIVE = re.compile(r"\{\{(claim|status|src|asset|page|pr):([^}|]+)(?:\|([^}]*))?\}\}")


class MuseumBuildError(RuntimeError):
    pass


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def git_last_commit(path):
    try:
        out = subprocess.run(["git", "log", "-n", "1", "--format=%h", "--", str(path)], cwd=REPO,
                             capture_output=True, text=True, check=True).stdout.strip()
        return out or None
    except (OSError, subprocess.CalledProcessError):
        return None


def load_rooms():
    rooms = []
    for path in sorted(ROOMS.glob("*.html")):
        text = path.read_text()
        m = _HEADER.match(text)
        if not m:
            raise MuseumBuildError(f"{path.name}: missing <!--meta {{...}} --> header")
        meta = json.loads(m.group(1))
        for key in ("slug", "title", "order"):
            if key not in meta:
                raise MuseumBuildError(f"{path.name}: header lacks '{key}'")
        meta.setdefault("expect", {})
        meta.setdefault("kicker", "")
        meta.setdefault("summary", "")
        meta.setdefault("provisional", False)
        meta.setdefault("under_review", [])
        if meta["under_review"] and not meta["provisional"]:
            raise MuseumBuildError(f"{path.name}: only a provisional room may cite work under review")
        meta["file"] = path.name
        meta["body"] = text[m.end():]
        rooms.append(meta)
    rooms.sort(key=lambda r: r["order"])
    slugs = [r["slug"] for r in rooms]
    if len(set(slugs)) != len(slugs):
        raise MuseumBuildError(f"duplicate room slugs: {slugs}")
    return rooms


def badge(claim, conv, short=False):
    status = claim["status"]
    enc = conv["status"].get(status)
    if enc is None:
        return '<span class="badge s-NONE">no status</span>'
    word = enc["short"] if short else enc["badge"]
    return (f'<span class="badge s-{status}" title="{html.escape(claim["status_text"], quote=True)}">'
            f"{html.escape(word)}</span>")


def repo_path(raw, where):
    rel = raw.strip().strip("/")
    p = (REPO / rel).resolve()
    if REPO not in p.parents and p != REPO:
        raise MuseumBuildError(f"{where}: path escapes the repository: {raw}")
    if not p.exists():
        raise MuseumBuildError(f"{where}: no such file or folder in the repository: {rel}")
    return rel, p


def render_body(room, claims, conv, slugs, cited, sources):
    where = room["file"]

    def sub(m):
        kind, arg, label = m.group(1), m.group(2).strip(), m.group(3)
        if kind in ("claim", "status"):
            if arg not in claims:
                raise MuseumBuildError(f"{where}: {arg} is not in research/claims.md")
            if arg not in room["expect"]:
                raise MuseumBuildError(f"{where}: cites {arg} without declaring the status its text "
                                       f"assumes (add it to 'expect')")
            cited.setdefault(arg, set()).add(room["slug"])
            c = claims[arg]
            if kind == "status":
                return f'<span class="status-text">{html.escape(c["status_text"])}</span>'
            return (f'<a class="claim" href="claims.html#{arg}" title="{html.escape(c["title"], quote=True)}">'
                    f'<span class="cid">{arg}</span>{badge(c, conv, short=True)}</a>')
        if kind == "src":
            rel, p = repo_path(arg, where)
            sources.add(rel)
            url = f"{GITHUB}/{'tree' if p.is_dir() else 'blob'}/main/{rel}"
            text = html.escape(label) if label else f"<code>{html.escape(rel)}</code>"
            return f'<a class="src" href="{url}">{text}</a>'
        if kind == "asset":
            rel, p = repo_path(arg, where)
            if p.is_dir():
                raise MuseumBuildError(f"{where}: asset must be a file: {rel}")
            return "../../" + rel  # site pages live at museum/site/*.html
        if kind == "pr":
            if not arg.isdigit() or int(arg) not in room["under_review"]:
                raise MuseumBuildError(f"{where}: PR {arg} is not listed in this room's 'under_review'")
            return f'<a class="pr" href="{GITHUB}/pull/{arg}">{html.escape(label or "PR #" + arg)}</a>'
        if kind == "page":
            if arg not in slugs:
                raise MuseumBuildError(f"{where}: link to unknown page '{arg}'")
            return f'<a href="{arg}.html">{html.escape(label or arg)}</a>'
        raise AssertionError(kind)

    body = _DIRECTIVE.sub(sub, room["body"])
    if "{{" in body:
        raise MuseumBuildError(f"{where}: unrecognised directive near: "
                               f"{body[body.index('{{'):body.index('{{') + 40]!r}")
    return body


def nav(rooms, current):
    items = []
    for r in rooms:
        if r.get("nav") is False:
            continue
        cls = ' class="here"' if r["slug"] == current else ""
        items.append(f'<li><a{cls} href="{r["slug"]}.html">{html.escape(r.get("nav_label", r["title"]))}</a></li>')
    cls = ' class="here"' if current == "claims" else ""
    items.append(f'<li><a{cls} href="claims.html">Reference · Claims on display</a></li>')
    return "\n".join(items)


def page(rooms, room, body, stamp, prev_next):
    title = room["title"] if room["slug"] == "index" else f"{room['title']} · ALM museum"
    prev_r, next_r = prev_next
    walk = ""
    if prev_r or next_r:
        left = (f'<a class="prev" href="{prev_r["slug"]}.html"><small>Back</small>{html.escape(prev_r["title"])}</a>'
                if prev_r else "<span></span>")
        right = (f'<a class="next" href="{next_r["slug"]}.html"><small>Next room</small>{html.escape(next_r["title"])}</a>'
                 if next_r else "<span></span>")
        walk = f'<nav class="walk" aria-label="Tour">{left}{right}</nav>'
    kicker = f'<p class="kicker">{html.escape(room["kicker"])}</p>' if room["kicker"] else ""
    if room.get("provisional"):
        prs = ", ".join(f'<a href="{GITHUB}/pull/{n}">#{n}</a>' for n in room["under_review"])
        kicker += (f'<div class="provisional-banner"><strong>Provisional room.</strong> Parts of these '
                   f'exhibits come from work still under review ({prs}) and not yet in the claims '
                   f'ledger. Badges appear only for ledger claims; everything else is attributed to the '
                   f'lane and pull request it comes from, and may change.</div>')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(room['summary'], quote=True)}">
<link rel="stylesheet" href="museum.css">
</head>
<body class="room-{room['slug']}">
<header class="site">
  <a class="brand" href="index.html">ALM <span>an artificial-life natural history museum</span></a>
  <details class="map"><summary>Rooms</summary><ol>
{nav(rooms, room['slug'])}
  </ol></details>
</header>
<main>
{kicker}
{body}
{walk}
</main>
<footer class="site">
  <p>{stamp}</p>
  <p>Every picture here is a recorded simulation or a figure drawn from committed data. Statuses
  are the claims ledger's, not the museum's: a badge never says more than
  <a href="{GITHUB}/blob/main/research/claims.md">research/claims.md</a> does.</p>
</footer>
</body>
</html>
"""


def claims_page(rooms, claims, conv, cited, stamp):
    rows = []
    for cid in sorted(cited):
        c = claims[cid]
        where = ", ".join(f'<a href="{s}.html">{html.escape(next(r["title"] for r in rooms if r["slug"] == s))}</a>'
                          for s in sorted(cited[cid], key=lambda s: next(r["order"] for r in rooms if r["slug"] == s)))
        rows.append(f"""<tr id="{cid}">
  <th scope="row"><a href="{GITHUB}/blob/main/research/claims.md#{_anchor(cid, c['title'])}">{cid}</a></th>
  <td>{html.escape(c['title'])}</td>
  <td>{badge(c, conv)}<div class="status-text">{html.escape(c['status_text'])}</div></td>
  <td>{where}</td>
</tr>""")
    legend = "\n".join(
        f'<li>{badge({"status": s, "status_text": s}, conv)} {html.escape(_MEANING[s])}</li>'
        for s in ledger.VOCAB)
    body = f"""<h1>Claims on display</h1>
<p class="lede">These are the claims the museum's rooms cite, with the status each one has in the
ledger right now. The ledger has more; read it whole in
<a href="{GITHUB}/blob/main/research/claims.md">research/claims.md</a>, where every claim carries
its parameters, run IDs, reproduction command, caveats and history.</p>
<h2>How to read a badge</h2>
<ul class="legend">
{legend}
</ul>
<p>A badge shows the first status word of the ledger entry. Many entries qualify it (for example
"reproduced, not yet by a second lane"); the full status text is printed under each badge here,
and appears when you hover over a badge anywhere in the museum.</p>
<div class="table-wrap"><table class="claims">
<thead><tr><th scope="col">ID</th><th scope="col">Claim</th><th scope="col">Status in the ledger</th><th scope="col">Shown in</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table></div>"""
    meta = {"slug": "claims", "title": "Claims on display", "kicker": "Reference",
            "summary": "Every claim the museum cites, with its current ledger status."}
    return page(rooms, meta, body, stamp, (None, None))


_MEANING = {
    "INDEPENDENTLY_CHECKED": "a second lane ran a distinct implementation and got the same answer.",
    "REPRODUCED": "seen again from a clean process with the same inputs.",
    "OBSERVED": "seen in at least one recorded run; not yet reproduced.",
    "CONJECTURED": "a hypothesis without direct supporting runs yet.",
    "NUMERICALLY_FRAGILE": "changes or disappears under a modest change of timestep, resolution or boundary.",
    "REFUTED": "contradicted by recorded evidence. Refuted claims stay on display.",
}


def _anchor(cid, title):
    """GitHub's heading anchor for '### Cxxx — title'."""
    s = f"{cid} — {title}".lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def css(conv):
    st = conv["status"]
    dark_text = {"REPRODUCED", "NUMERICALLY_FRAGILE"}
    hatch = {
        "NUMERICALLY_FRAGILE": "repeating-linear-gradient(135deg, transparent 0 4px, rgba(0,0,0,.18) 4px 6px)",
        "REFUTED": "repeating-linear-gradient(45deg, transparent 0 4px, rgba(255,255,255,.28) 4px 5px),"
                   " repeating-linear-gradient(135deg, transparent 0 4px, rgba(255,255,255,.28) 4px 5px)",
        "CONJECTURED": "radial-gradient(rgba(255,255,255,.35) 1px, transparent 1.4px) 0 0 / 4px 4px",
    }
    rules = []
    for s, enc in st.items():
        bg = enc["color"] + (f"; background-image: {hatch[s]}" if s in hatch else "")
        fg = "#111" if s in dark_text else "#fff"
        rules.append(f".s-{s} {{ background-color: {bg}; color: {fg}; }}")
    tokens = (f"--ink: {conv['ink']}; --muted: {conv['muted']}; --grid: {conv['grid']}; "
              f"--paper: {conv['paper']}; --unresolved: {conv['unresolved']}; "
              f"--removed: {conv['edit']['removed']}; --added: {conv['edit']['added']};")
    base = (MUSEUM / "style.css").read_text()
    return (f"/* Generated by museum/build.py from museum/style.css and research/figures/conventions.json. */\n"
            f":root {{ {tokens} }}\n{base}\n/* status badges (conventions.json) */\n" + "\n".join(rules) + "\n")


def build(out=SITE):
    out = pathlib.Path(out)
    conv = json.loads(CONVENTIONS.read_text())
    claims = ledger.parse(LEDGER)
    rooms = load_rooms()
    slugs = {r["slug"] for r in rooms} | {"claims"}

    errors = []
    for r in rooms:
        for cid, want in r["expect"].items():
            have = claims.get(cid, {}).get("status")
            if have != want:
                errors.append(f"{r['file']}: text assumes {cid} is {want}, ledger has {have}")
    if errors:
        raise MuseumBuildError("research/claims.md no longer matches what these rooms say:\n  "
                               + "\n  ".join(errors) + "\nRewrite the room, then update its 'expect'.")

    ledger_sha = sha256(LEDGER)
    stamp = (f"Claim statuses read from <code>research/claims.md</code> "
             f"(sha256 <code>{ledger_sha[:12]}</code>) when this page was built.")

    cited, sources, pages = {}, {}, {}
    tour = [r for r in rooms if r.get("tour", True)]
    for r in rooms:
        src = set()
        body = render_body(r, claims, conv, slugs, cited, src)
        if not src and r.get("needs_sources", True):
            raise MuseumBuildError(f"{r['file']}: a room must link at least one scientific source")
        unused = set(r["expect"]) - {c for c, s in cited.items() if r["slug"] in s}
        if unused:
            raise MuseumBuildError(f"{r['file']}: declares but never cites {sorted(unused)}")
        sources[r["slug"]] = sorted(src)
        i = tour.index(r) if r in tour else None
        pn = ((tour[i - 1] if i and i > 0 else None), (tour[i + 1] if i is not None and i + 1 < len(tour) else None))
        pages[f"{r['slug']}.html"] = page(rooms, r, body, stamp, pn)
    pages["claims.html"] = claims_page(rooms, claims, conv, cited, stamp)

    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.html"):
        if old.name not in pages:
            old.unlink()
    for name, text in pages.items():
        (out / name).write_text(text)
    (out / "museum.css").write_text(css(conv))
    snapshot = {
        "ledger": "research/claims.md",
        "ledger_sha256": ledger_sha,
        "ledger_commit": git_last_commit(LEDGER),
        "conventions_sha256": sha256(CONVENTIONS),
        "claims": {cid: {"status": claims[cid]["status"], "status_text": claims[cid]["status_text"],
                         "rooms": sorted(cited[cid])} for cid in sorted(cited)},
        "sources": sources,
    }
    (out / "ledger-snapshot.json").write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
    return snapshot


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(SITE))
    args = ap.parse_args()
    try:
        snap = build(args.out)
    except MuseumBuildError as e:
        sys.exit(f"museum build failed: {e}")
    print(f"built {len(list(pathlib.Path(args.out).glob('*.html')))} pages into "
          f"{os.path.relpath(args.out)}; {len(snap['claims'])} claims on display")


if __name__ == "__main__":
    main()
