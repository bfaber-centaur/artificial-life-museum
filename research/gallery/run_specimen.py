"""``python -m alm.run`` with the gallery's vendored specimens (S101-S103) registered.

    .venv/bin/python research/gallery/run_specimen.py --specimen S102 --steps 3000 --every 10

Takes exactly the arguments of ``python -m alm.run``. Once PR #11 is merged, plain
``python -m alm.run`` gives the same run.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import galspec  # noqa: E402
from alm import run  # noqa: E402

if __name__ == "__main__":
    galspec.ensure_registered()
    sys.exit(run.main())
