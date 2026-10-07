"""Smoke checks that the bootstrapped environment is usable."""

import importlib

import pytest


@pytest.mark.parametrize(
    "module", ["numpy", "scipy", "PIL", "matplotlib", "imageio", "alm"]
)
def test_imports(module):
    importlib.import_module(module)


def test_reference_sha_is_pinned():
    import alm

    assert len(alm.LENIA_REFERENCE_SHA) == 40
