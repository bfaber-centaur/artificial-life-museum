"""Intervention hook (Lane 4 owns the actual disturbance battery).

An intervention is a small dataclass with a registered ``name`` and an
``apply(A, sim, rng)`` method returning the new state. The runner applies it
at a scheduled step (after that step's update), re-clips to [0, 1], logs mass
before/after, and snapshots the state on both sides. Every field of the
dataclass is recorded in the run manifest, so parameters must be plain values.

Add one with::

    @register
    @dataclass(frozen=True)
    class PatchDelete(Intervention):
        name: ClassVar[str] = "patch_delete"
        radius: float = 5.0
        def apply(self, A, sim, rng): ...

and schedule it from the CLI as ``--intervene 500:patch_delete:radius=4``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import ClassVar

import numpy as np

REGISTRY: dict[str, type["Intervention"]] = {}


@dataclass(frozen=True)
class Intervention:
    name: ClassVar[str] = "abstract"

    def apply(self, A: np.ndarray, sim, rng: np.random.Generator) -> np.ndarray:
        raise NotImplementedError

    def to_dict(self) -> dict:
        return {"name": self.name, "params": asdict(self)}


def register(cls: type[Intervention]) -> type[Intervention]:
    if cls.name in REGISTRY and REGISTRY[cls.name] is not cls:
        raise ValueError(f"intervention {cls.name!r} already registered")
    REGISTRY[cls.name] = cls
    return cls


def make(name: str, **params) -> Intervention:
    try:
        cls = REGISTRY[name]
    except KeyError:
        raise KeyError(f"unknown intervention {name!r}; known: {sorted(REGISTRY)}") from None
    types = {f.name: f.type for f in fields(cls)}
    coerced = {}
    for k, v in params.items():
        if k not in types:
            raise TypeError(f"{name} has no parameter {k!r}; has {sorted(types)}")
        coerced[k] = _coerce(v, types[k])
    return cls(**coerced)


def _coerce(value, annotation):
    if not isinstance(value, str):
        return value
    ann = str(annotation)
    if "int" in ann and "float" not in ann:
        return int(value)
    if "float" in ann:
        return float(value)
    if "bool" in ann:
        return value.lower() in ("1", "true", "yes")
    return value


def parse(spec: str) -> tuple[int, Intervention]:
    """Parse ``STEP:NAME[:k=v,k=v]`` into (step, intervention)."""
    parts = spec.split(":", 2)
    if len(parts) < 2:
        raise ValueError(f"intervention spec {spec!r} is not STEP:NAME[:k=v,...]")
    step, name = int(parts[0]), parts[1]
    params = {}
    if len(parts) == 3 and parts[2]:
        for kv in parts[2].split(","):
            k, v = kv.split("=", 1)
            params[k.strip()] = v.strip()
    return step, make(name, **params)


def to_spec(step: int, iv: Intervention) -> str:
    params = ",".join(f"{k}={v}" for k, v in asdict(iv).items())
    return f"{step}:{iv.name}" + (f":{params}" if params else "")


@register
@dataclass(frozen=True)
class MassScale(Intervention):
    """Multiply the whole state by ``factor`` (charter's 'mass attenuation').

    Included as the reference example of the hook; Lane 4 owns its use."""

    name: ClassVar[str] = "mass_scale"
    factor: float = 1.0

    def apply(self, A, sim, rng):
        return A * self.factor
