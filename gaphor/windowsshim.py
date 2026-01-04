import importlib.resources
import logging
import os
import sys
from pathlib import Path


def gi_init():
    """Workaround for https://gitlab.gnome.org/GNOME/pygobject/-/issues/545."""
    if sys.platform != "win32":
        import gi

        return gi
    env_path = os.environ.get("PATH", "").split(os.pathsep)
    if first_gtk_path := next(
        filter(
            lambda path: path is not None
            and Path.is_file(Path(path) / "girepository-2.0-0.dll"),
            env_path,
        ),
        None,
    ):
        with os.add_dll_directory(first_gtk_path):
            import gi

            return gi
    return None


def register_fonts_windows() -> None:
    """Register fonts with Windows GDI."""
    if sys.platform != "win32":
        return

    import ctypes
    from ctypes import wintypes

    gdi32 = ctypes.windll.gdi32

    # int AddFontResourceExW(LPCWSTR name, DWORD fl, PVOID res);
    AddFontResourceExW = gdi32.AddFontResourceExW
    AddFontResourceExW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.LPVOID]
    AddFontResourceExW.restype = ctypes.c_int

    FR_PRIVATE = 0x10  # Font is private to the process

    for font_file in importlib.resources.files("gaphor.fonts").iterdir():
        if isinstance(font_file, Path) and font_file.suffix == ".ttf":
            result = AddFontResourceExW(str(font_file), FR_PRIVATE, None)
            if result == 0:
                logging.getLogger(__name__).warning(f"Failed to load font: {font_file}")
