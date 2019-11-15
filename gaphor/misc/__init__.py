import os

from gi.repository import GLib


def get_config_dir() -> str:
    """Return the directory where the user's config is stored. This varies
    depending on platform."""

    config_dir = os.path.join(GLib.get_user_config_dir(), "gaphor")
    os.makedirs(config_dir, exist_ok=True)

    return config_dir
