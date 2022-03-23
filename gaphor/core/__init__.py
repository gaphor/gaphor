"""The Core module provides an entry point for Gaphor's core constructs."""

from gaphor.action import action
from gaphor.core.eventmanager import event_handler
from gaphor.i18n import gettext
from gaphor.transaction import Transaction, transactional
