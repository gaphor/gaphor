"""Gaphor is the simple modeling tool written in Python."""

import os

import gi

gtk_version = "4.0" if os.getenv("GAPHOR_USE_GTK") == "4" else "3.0"

gi.require_version("PangoCairo", "1.0")
gi.require_version("Gtk", gtk_version)
gi.require_version("Gdk", gtk_version)
