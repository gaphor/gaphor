"""
The Core module provides an entry point for Gaphor's core constructs.

An average module should only need to import this module.
"""

from gaphor.application import inject, Application
from gaphor.transaction import Transaction, transactional
from gaphor.action import (
    action,
    toggle_action,
    radio_action,
    open_action,
    build_action_group,
)
from gaphor.i18n import _
