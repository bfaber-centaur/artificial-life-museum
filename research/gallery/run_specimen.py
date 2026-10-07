"""``python -m alm.run`` with the gallery's interventions registered.

    .venv/bin/python research/gallery/run_specimen.py --specimen S101 --steps 5000 --every 10 \
        --intervene 3000:gallery_port_injury:s=0.25

Takes exactly the arguments of ``python -m alm.run``, plus the ``gallery_port_injury``
intervention (``galintervene.py``) for ``--intervene``.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import galintervene  # noqa: E402,F401  (registers gallery_port_injury)
from alm import run  # noqa: E402

if __name__ == "__main__":
    sys.exit(run.main())
