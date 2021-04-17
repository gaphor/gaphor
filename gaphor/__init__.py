"""Gaphor is the simple modeling tool written in Python."""

import gi

gtk_version = "3.0"

gi.require_version("PangoCairo", "1.0")
gi.require_version("Gtk", gtk_version)
gi.require_version("Gdk", gtk_version)
