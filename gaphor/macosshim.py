import importlib.resources
import sys
from pathlib import Path


def register_fonts_coretext() -> None:
    """Register Adwaita (fallback) fonts with macOS CoreText."""
    if sys.platform != "darwin":
        return

    from CoreText import (
        CTFontManagerRegisterFontsForURL,
        kCTFontManagerScopeProcess,
    )
    from Foundation import NSURL

    # Register each font file
    for font_file in importlib.resources.files("gaphor.fonts").iterdir():
        if isinstance(font_file, Path) and font_file.suffix == ".ttf":
            font_url = NSURL.fileURLWithPath_(str(font_file))
            CTFontManagerRegisterFontsForURL(font_url, kCTFontManagerScopeProcess, None)
