"""Proves the test runner and CI are wired up. Real tests arrive with real code."""

import app


def test_package_imports():
    assert app.__version__ == "0.1.0"
