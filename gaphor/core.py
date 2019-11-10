"""
The Core module provides an entry point for Gaphor's core constructs.

An average module should only need to import this module.
"""

from gaphor.action import action, primary
from gaphor.application import Application
from gaphor.i18n import translate
from gaphor.services.eventmanager import event_handler
from gaphor.transaction import Transaction, transactional
