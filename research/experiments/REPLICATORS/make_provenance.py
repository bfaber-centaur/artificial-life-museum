"""Write provenance.json for G029-G031 from the film records (run after the films are copied in)."""
import json
from pathlib import Path

from common import found_entry
from interp import mix

EX = Path(__file__).resolve().parents[2] / "gallery" / "exhibits"
ENGINE = "research/experiments/WINGS/nd_lenia.NDLenia (independent numpy port of upstream LeniaNDKC, pinned adfc542)"


def rule(stem, idx):
    p = found_entry(stem, idx)["params"]
    return p if isinstance(p, list) else [p]


t = json.loads((EX / "G029-family-tree" / "tree.json").read_text())
(EX / "G029-family-tree" / "provenance.json").write_text(json.dumps(dict(
    exhibit="G029", title="A family tree", claim="C072",
    media=["family-tree.mp4", "family-tree.gif", "family-tree-final.png", "tree.png", "tree.json"],
    engine=ENGINE,
    run=dict(specimen="found/213.json #84 'division well' (Chan)", rule=rule("213", 84), grid=[384, 384], boundary="periodic",
             time_units=2000, dt=0.1, initial_state_sha256_prefix=t["initial_sha"], final_state_sha256_prefix=t["final_sha"]),
    frames=dict(sampled_every_tu=1, video_every_tu=2, mp4_fps=30, gif="ffmpeg fps 8, 320 px, 96-colour palette"),
    tracker=t["params"],
    view="whole 384² torus at 2x; hue = inherited neutral marker (founder 0.55, +N(0, 0.08) per division, seed 2026); value = field",
    commands=["record.py 213 84 384 2000 states/well384.npz", "film_tree.py states/well384.npz OUT \"Division well (Chan's found/213 #84)\" 2 2"],
    caveats=["Cells are peaks of the blurred field; thresholds set on a 400-tu test run.",
             "The tracker cannot tell a merger from a cell that fades.", "Creature and name are Chan's."]), indent=1))

l = json.loads((EX / "G030-four-growth-rates" / "ladder.json").read_text())
(EX / "G030-four-growth-rates" / "provenance.json").write_text(json.dumps(dict(
    exhibit="G030", title="How fast one cell fills the world", claim="C073",
    media=["ladder.mp4", "ladder.gif", "ladder-final.png", "ladder.json"], engine=ENGINE,
    runs=[dict(lam=lam, rule=mix(lam), seed="found/213.json #84 cells, centred", grid=[256, 256], boundary="periodic", time_units=600,
               dt=0.1, initial_state_sha256_prefix=h0, final_state_sha256_prefix=h1)
          for lam, h0, h1 in zip(l["lams"], l["initial_sha"], l["final_sha"])],
    frames=dict(every_tu=2, mp4_fps=30, gif="ffmpeg fps 8, 384 px, 96-colour palette"),
    view="field on inferno, linear [0, 1]; bar = occupancy (blur 4 px > 0.05)",
    commands=["film_ladder.py 600 OUT"],
    caveats=["lam 0 and 1 are Chan's rules; lam 0.2 and 0.5 are interpolations of ours."]), indent=1))

f = json.loads((EX / "G031-replicating-in-3d" / "replicator3d.json").read_text())
(EX / "G031-replicating-in-3d" / "provenance.json").write_text(json.dumps(dict(
    exhibit="G031", title="A replicator in three dimensions", claim="C074",
    media=["replicator3d.mp4", "replicator3d.gif", "replicator3d-strip.png", "replicator3d.json"], engine=ENGINE,
    run=dict(specimen="found/312.json #21 'self-replicate... unstable' (Chan)", rule=rule("312", 21), grid=[96, 96, 96],
             boundary="periodic", time_units=f["tu"], dt=f["dt"], initial_state_sha256_prefix=f["initial_sha"],
             final_state_sha256_prefix=f["final_sha"]),
    frames=dict(every_tu=1, mp4_fps=30, gif="ffmpeg fps 15, 320 px, 128-colour palette"),
    view="box rotated 0.6 deg per tu about the vertical axis; first voxel > 0.25 along the line of sight, Lambert-lit; hue per body",
    commands=["film3d.py 312 21 96 320 OUT replicator3d"],
    caveats=["Periodic box: bodies leaving one side reappear on the other, and rotation shows wrapped copies at the edges.",
             "Chan named the creature unstable."]), indent=1))
print("ok")
