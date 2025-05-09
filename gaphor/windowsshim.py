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
