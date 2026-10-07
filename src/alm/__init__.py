"""Artificial-Life Museum: headless classic 2-D Lenia experiments."""

__version__ = "0.1.0"

# Pinned upstream reference (Chakazul/Lenia), checked out under .refs/Lenia by
# scripts/bootstrap.sh. Reference only; ALM does not import it at runtime.
LENIA_REFERENCE_SHA = "adfc542939266de7f4bb7ebb552e8499701ee107"

from .lenia import Lenia, Rule, growth, kernel, kernel_core  # noqa: E402
