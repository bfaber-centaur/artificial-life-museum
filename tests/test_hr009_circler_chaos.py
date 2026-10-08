"""Lane 7 HR-009 test: S102's circling is chaotic, so its exact death step is not a property of the rule.

Two copies of the registered S102 start that differ by 1e-12 on the body's support separate to
O(0.1) within 250 time units (exponential growth at about 0.2 per tu; e1.csv in
research/experiments/HR009-l6-review). Replications of L6-f should therefore target the lifetime
distribution, not step 39 799.
"""
import numpy as np
from scipy import ndimage

from alm import specimens
from alm.lenia import Lenia


def test_circler_twins_separate_within_250_tu():
    S = specimens.load("S102")
    A0 = S.place(128)
    support = ndimage.binary_dilation(A0 > 0, iterations=3)
    xi = np.random.default_rng(9100).uniform(-1, 1, A0.shape)
    a = Lenia(S.rule, A0.copy())
    b = Lenia(S.rule, np.clip(A0 + 1e-12 * xi * support, 0, 1))
    seps = {}
    for t in range(1, 2501):
        a.step()
        b.step()
        if t in (500, 2500):
            seps[t] = np.sqrt(((a.A - b.A) ** 2).sum())
    assert seps[500] < 1e-6  # still a tiny difference after 50 tu
    assert seps[2500] > 1e-1  # but O(0.1) by 250 tu: about 25 e-folds
