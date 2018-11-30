"""Provides a get_user_data_dir() function for retrieving the user's data
directory."""

import os


def get_user_data_dir():

    """Return the directory where the user's data is stored.  This varies
    depending on platform."""

    if os.name == "nt":
        home = "USERPROFILE"
    else:
        home = "HOME"

    return os.path.join(os.getenv(home), ".gaphor")
