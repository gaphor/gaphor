import os
import sys
from pathlib import Path


def gi_init():
    """Workaround for https://gitlab.gnome.org/GNOME/pygobject/-/issues/545."""
    if sys.platform != "win32" or sys.version_info < (3, 8):
        import gi

        return gi
    env_path = os.environ.get("PATH", "").split(os.pathsep)
    if first_gtk_path := next(
        filter(
            lambda path: path is not None
            and Path.is_file(Path(path) / "girepository-1.0-1.dll"),
            env_path,
        ),
        None,
    ):
        with os.add_dll_directory(first_gtk_path):
            import gi

            return gi
