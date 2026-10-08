# The ALM museum (Lane 10, Exhibition Designer)

A small static museum built from the project's specimen dossiers, Lane 8's gallery, Lane 9's
figures and the claims ledger. It is plain HTML and CSS with no JavaScript and no external
requests.

## Visit it

```bash
python3 -m http.server 8000        # from the repository root
# then open http://localhost:8000/museum/site/
```

Opening `museum/site/index.html` straight from disk works too. Pages load images and video from
`research/` by relative path, so serve the whole repository, not just `museum/site/`.

## The first visitor journey

| Page | Room | Built from |
| --- | --- | --- |
| `index.html` | Entrance: "The search for Mr Wobbles" | G001, charter discovery protocol |
| `orbium.html` | 1 · The ruler: Orbium | S001 dossier, G002, C001, C009–C011, C014, C020 |
| `wobbles.html` | 2 · The wobble that wasn't | Lane 2 baseline plot, H001 (Lane 7), C003–C006, C011, C013 |
| `edges.html` | 3 · How much can it take? | Figure A, L4-001, C023, C026–C029 |
| `one-rule.html` | 4 · Three animals, one rule | S101–S103 dossiers, G002, G003, C038–C044 |
| `how-we-know.html` | 5 · How we know | charter, ledger, hostile review, gallery and figure rules |
| `under-review.html` | 6 · Still being argued (provisional) | S102 lifetimes and S101 coupling: L6-007, L6-008, L3-003 and HR-009 on main, not yet ledgered; G002, G004, C038, C041, C047 |
| `collection.html` | Reference: the four specimens | dossiers, gallery runs |
| `claims.html` | Reference: every claim on display | generated from the ledger |

## Rules every page follows

1. **Statuses come from the ledger.** `build.py` reads `research/claims.md` with Lane 9's parser
   (`figlib.ledger`) and draws badges with the words and colours in
   `research/figures/conventions.json`. No page types a status.
2. **Rooms declare what their words assume.** Each room's header lists, under `expect`, the
   status its prose relies on for every claim it cites. If the ledger moves, the build stops, and
   the room is rewritten deliberately. A room cannot cite a claim it has not declared.
3. **Everything links to its evidence.** Images and video must be files in the repository, and
   every room ends with sources that must exist. The build fails on a missing file, an unknown
   claim or a broken internal link.
4. **Observation is kept apart from interpretation.** Wall labels have a "What you see" part
   and a "What the ledger says" part; caveats get their own box.
5. **Nothing is re-encoded.** Lane 8's photographs and Lane 9's figures are shown as committed,
   in their own colours. Specimen imagery sits in dark vitrines (`#0b0b0f`, matching Lane 8's
   frames); evidence figures sit on white paper, as Lane 9 draws them.
6. **Only what is on `main`, unless the room says otherwise.** A room marked provisional may
   describe work in open PRs, with a banner, attributing each finding to its lane and PR; it gets
   no badge until the ledger records it.
7. **No nicknames, no new species.** Registered names only, per the charter's discovery protocol.

## Build

```bash
.venv/bin/python museum/build.py        # writes museum/site/
.venv/bin/pytest tests/test_museum.py
```

The build writes the HTML pages, `museum.css` (from `style.css` plus the colour tokens and status
badges in `conventions.json`) and `ledger-snapshot.json`, which records the ledger's SHA-256 and
commit and the status of every claim on display. `tests/test_museum.py` rebuilds into a scratch
folder and fails if a committed page's statuses no longer match the ledger. When that happens,
re-run the build; if it then stops on an `expect` mismatch, rewrite that room.

## Adding a room

Create `museum/rooms/NN-slug.html`. It starts with a header comment:

```html
<!--meta {"slug": "my-room", "order": 60, "title": "Room title", "kicker": "Room 6 · ...",
          "summary": "One sentence.", "expect": {"C038": "REPRODUCED"}} -->
```

then an HTML fragment using these directives:

| Directive | Renders |
| --- | --- |
| `{{claim:C038}}` | claim chip with its status badge, linked to the claims page |
| `{{status:C038}}` | the ledger's full status text |
| `{{src:path\|label}}` | link to a repository file or folder on GitHub |
| `{{asset:path}}` | relative URL of a repository file, for `<img>` or `<video>` |
| `{{page:slug\|label}}` | link to another museum page |
| `{{pr:27\|label}}` | link to an open pull request; only in a room with `"provisional": true` that lists it in `"under_review"` |

`"tour": false` keeps a page out of the Back/Next walk; `order` sets its position.
