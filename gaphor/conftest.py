"""Basic test case for Gaphor tests.

Everything is about services so the Case can define it's required
services and start off.
"""
from __future__ import annotations

# isort: skip_file

import logging
from io import StringIO
from pathlib import Path
from typing import TypeVar

import pytest

# Load gaphor.ui first, so GTK library versions are set corrently
import gaphor.ui


@pytest.fixture
def test_models():
    """The folder where test models can be found."""
    return Path(__file__).parent.parent / "test-models"


@pytest.fixture
def models():
    """The folder where test models can be found."""
    return Path(__file__).parent.parent / "models"
