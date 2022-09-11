import os
from pathlib import Path


def windows_init():
    """Workaround for https://gitlab.gnome.org/GNOME/pygobject/-/issues/545."""
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
            import gi  # noqa F401
