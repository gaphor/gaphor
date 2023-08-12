import sys

import pytest


@pytest.mark.skipif(sys.platform != "darwin", reason="Only load shim on macOS")
def test_macosshim_loaded():
    import gaphor.ui  # noqa: F401

    assert "gaphor.ui.macosshim" in sys.modules
