"""Visual conventions for ALM scientific figures (Lane 9).

The same values are written to ../conventions.json so other lanes (Lane 8's gallery)
can read them without importing matplotlib. Keep the two in sync with
`python -m figlib.style --write-json`.

Rules:
- Colours are Okabe-Ito (colour-blind safe). No meaning is carried by colour alone:
  every outcome also has a marker shape, every claim status also has a text badge.
- Outcome encoding is fixed across figures: RECOVERED = filled circle, DIED = cross.
- Claim statuses come from research/claims.md verbatim; a figure never upgrades one.
"""
import contextlib
import json
import pathlib
import sys

import matplotlib as mpl

OKABE_ITO = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
}
INK = "#222222"
MUTED = "#6b6b6b"
GRID = "#d9d9d9"
PAPER = "#ffffff"
UNRESOLVED = "#bdbdbd"  # gap between the last survivor and the first death

# Run outcomes (Lane 4 protocol classes).
OUTCOME = {
    "RECOVERED": dict(color=OKABE_ITO["green"], marker="o", fill=True, label="recovered"),
    "DIED": dict(color=OKABE_ITO["vermillion"], marker="x", fill=False, label="died"),
    "TRANSFORMED": dict(color=OKABE_ITO["purple"], marker="s", fill=False, label="transformed"),
    "EXPLODED": dict(color=OKABE_ITO["orange"], marker="^", fill=False, label="exploded"),
}

# Claim statuses (vocabulary of research/claims.md). Badge text is always printed.
STATUS = {
    "INDEPENDENTLY_CHECKED": dict(color=OKABE_ITO["blue"], hatch=None, badge="independently checked", short="indep. checked"),
    "REPRODUCED": dict(color=OKABE_ITO["sky"], hatch=None, badge="reproduced", short="reproduced"),
    "OBSERVED": dict(color=MUTED, hatch=None, badge="observed", short="observed"),
    "CONJECTURED": dict(color=MUTED, hatch="..", badge="conjectured", short="conjectured"),
    "NUMERICALLY_FRAGILE": dict(color=OKABE_ITO["orange"], hatch="////", badge="numerically fragile", short="num. fragile"),
    "REFUTED": dict(color=INK, hatch="xx", badge="refuted", short="refuted"),
}

# Phenotypes (Lane 6 motion classes). Distinct from run outcomes; marker shape always differs.
PHENOTYPE = {
    "GLIDER": dict(color=OKABE_ITO["blue"], marker="o", label="glider"),
    "CIRCLER": dict(color=OKABE_ITO["purple"], marker="D", label="circler"),
    "STATIC": dict(color=OKABE_ITO["orange"], marker="s", label="static"),
    "OTHER": dict(color=INK, marker="*", label="other"),
    "died": dict(color="#b8b8b8", marker=".", label="died"),
    "filled": dict(color="#7a7a7a", marker="s", label="filled the world", size=0.45),
}

# Edits applied to a field: mass removed vs mass added (diverging, colour + sign).
EDIT = {"removed": OKABE_ITO["vermillion"], "added": OKABE_ITO["blue"]}

# Lenia field shown in scientific panels: plain greyscale (Lane 8 owns the cinematic look).
FIELD_CMAP = "Greys"

RC = {
    "font.family": "DejaVu Sans",
    "font.size": 7.5,
    "axes.titlesize": 8,
    "axes.labelsize": 7.5,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": INK,
    "ytick.color": INK,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.fontsize": 6.5,
    "legend.frameon": False,
    "figure.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "svg.hashsalt": "alm-lane9",  # deterministic SVG ids
    "path.simplify": False,
}


@contextlib.contextmanager
def figure_style():
    with mpl.rc_context(RC):
        yield


def status_badge(ax, claim_id, status, x=1.0, y=1.02, ha="right", short=False, **kw):
    """Print '<claim> · <status>' in the status colour (text, so not colour-only)."""
    st = STATUS[status]
    return ax.text(x, y, f"{claim_id} · {st['short' if short else 'badge']}", transform=ax.transAxes, ha=ha, va="bottom",
                   fontsize=6.3, color=st["color"], fontweight="bold", **kw)


def as_json():
    return {
        "palette": OKABE_ITO, "ink": INK, "muted": MUTED, "grid": GRID, "paper": PAPER,
        "unresolved": UNRESOLVED,
        "outcome": {k: {kk: vv for kk, vv in v.items()} for k, v in OUTCOME.items()},
        "status": STATUS, "edit": EDIT, "field_cmap": FIELD_CMAP, "phenotype": PHENOTYPE,
    }


if __name__ == "__main__":
    if "--write-json" in sys.argv:
        out = pathlib.Path(__file__).resolve().parents[1] / "conventions.json"
        out.write_text(json.dumps(as_json(), indent=2) + "\n")
        print(out)
