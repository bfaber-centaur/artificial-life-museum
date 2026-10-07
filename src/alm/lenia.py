"""Headless classic 2-D Lenia (single channel, single kernel).

Semantics follow upstream Chakazul/Lenia ``Python/LeniaND.py`` as executed at
the pinned commit (see research/reports/reference-dossier.md):

    U = K * A                      (periodic convolution, kernel normalised to sum 1)
    A <- clip(A + G(U) / T, 0, 1)  (plain Euler, hard clip)

Families are keyed by name, never by upstream index: catalog ``kn=1``/``gn=1``
execute the *polynomial* core and growth, whatever the upstream UI calls them.

This module is ALM's own implementation; it does not import upstream code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np

KERNEL_CORES = ("poly", "exp")
GROWTHS = ("poly", "exp")


def kernel_core(name: str, r: np.ndarray) -> np.ndarray:
    """Kernel core K_C(r) on r in [0, 1]; zero at both ends."""
    r = np.asarray(r, dtype=np.float64)
    inside = (r > 0) & (r < 1)
    q = np.where(inside, r * (1 - r), 0.25)  # placeholder keeps exp() finite off-support
    if name == "poly":
        out = (4 * q) ** 4
    elif name == "exp":
        out = np.exp(4 - 1 / q)
    else:
        raise ValueError(f"unknown kernel core {name!r}; expected one of {KERNEL_CORES}")
    return np.where(inside, out, 0.0)


def growth(name: str, u: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Growth mapping G(u) in [-1, 1]."""
    if name == "poly":
        return 2 * np.maximum(0.0, 1 - (u - mu) ** 2 / (9 * sigma**2)) ** 4 - 1
    if name == "exp":
        return 2 * np.exp(-((u - mu) ** 2) / (2 * sigma**2)) - 1
    raise ValueError(f"unknown growth {name!r}; expected one of {GROWTHS}")


@dataclass(frozen=True)
class Rule:
    """Classic Lenia rule parameters (upstream ``params`` names in comments)."""

    R: int = 13  # kernel radius in cells
    T: float = 10  # steps per unit time; dt = 1/T
    mu: float = 0.15  # m
    sigma: float = 0.015  # s
    beta: tuple[float, ...] = (1.0,)  # b, kernel shell peak heights
    kernel: str = "poly"
    growth: str = "poly"

    def __post_init__(self):
        if self.kernel not in KERNEL_CORES:
            raise ValueError(f"kernel must be one of {KERNEL_CORES}")
        if self.growth not in GROWTHS:
            raise ValueError(f"growth must be one of {GROWTHS}")
        object.__setattr__(self, "beta", tuple(float(b) for b in self.beta))

    @property
    def dt(self) -> float:
        return 1.0 / self.T

    def to_dict(self) -> dict:
        d = asdict(self)
        d["beta"] = list(self.beta)
        d["dt"] = self.dt
        return d


def kernel(shape: tuple[int, int], rule: Rule) -> np.ndarray:
    """Normalised kernel on the torus, centred at index (0, 0) (wrapped)."""
    ny, nx = shape
    y = np.fft.fftfreq(ny, 1.0 / ny)  # signed offsets 0, 1, ..., -1
    x = np.fft.fftfreq(nx, 1.0 / nx)
    D = np.hypot(y[:, None], x[None, :]) / rule.R
    B = len(rule.beta)
    Br = B * D
    shell = np.asarray(rule.beta)[np.minimum(np.floor(Br).astype(int), B - 1)]
    k = np.where(D < 1, kernel_core(rule.kernel, np.minimum(Br % 1, 1)) * shell, 0.0)
    return k / k.sum()


@dataclass
class Lenia:
    """A world on a periodic grid. ``A`` is the float64 state, ``t`` the step count."""

    rule: Rule
    A: np.ndarray
    t: int = 0
    _khat: np.ndarray = field(init=False, repr=False)

    def __post_init__(self):
        self.A = np.array(self.A, dtype=np.float64, copy=True)
        if self.A.ndim != 2:
            raise ValueError("state must be 2-D")
        self._khat = np.fft.rfft2(kernel(self.A.shape, self.rule))

    def potential(self, A: np.ndarray | None = None) -> np.ndarray:
        A = self.A if A is None else A
        return np.fft.irfft2(np.fft.rfft2(A) * self._khat, s=A.shape)

    def growth_field(self, A: np.ndarray | None = None) -> np.ndarray:
        r = self.rule
        return growth(r.growth, self.potential(A), r.mu, r.sigma)

    def step(self) -> np.ndarray:
        """Advance one Euler step; returns the growth field G used for it."""
        G = self.growth_field()
        self.A = np.clip(self.A + G * self.rule.dt, 0.0, 1.0)
        self.t += 1
        return G
