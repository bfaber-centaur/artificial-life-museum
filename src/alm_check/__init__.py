"""Lane 3 independent re-implementation of classic 2-D Lenia.

Written from upstream LeniaND.py semantics and the S001 dossier only, without
reading Lane 2's ``alm`` simulator. Agreement between this package and ``alm``
is evidence; shared code would not be.
"""

from .lenia import (  # noqa: F401
    Rule,
    World,
    decode_rle,
    growth,
    kernel_core,
    load_orbium,
    place,
    run,
)
