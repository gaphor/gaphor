"""The diagram package contains items (to be drawn on the diagram), tools (used
for interacting with the diagram) and interfaces (used for adapting the
diagram)."""

# ruff: noqa: E402,F401

import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")

import gaphor.diagram._connector
import gaphor.diagram.segment
