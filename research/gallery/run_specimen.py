"""``python -m alm.run`` with the gallery's vendored specimens (S101-S103) and interventions registered.

    .venv/bin/python research/gallery/run_specimen.py --specimen S102 --steps 3000 --every 10

Takes exactly the arguments of ``python -m alm.run``, plus the ``gallery_port_injury``
intervention (``galintervene.py``) for ``--intervene``.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import galintervene  # noqa: E402,F401  (registers gallery_port_injury)
import galspec  # noqa: E402
from alm import run  # noqa: E402

if __name__ == "__main__":
    galspec.ensure_registered()
    sys.exit(run.main())
