"""
Test GitHub issue #4. Diagram could not be loaded due to JuggleError
(presumed cyclic resolving of diagram items).
"""

from gi.repository import GLib, Gtk

from gaphor.application import distribution
from gaphor.storage.storage import load
from gaphor.tests import TestCase


class CyclicDiagramTestCase(TestCase):

    # services = TestCase.services + ['undo_manager']

    def setUp(self):
        super().setUp()

    def test_bug(self):
        """
        Load file.

        This does not nearly resemble the error, since the model should
        be loaded from within the mainloop (which will delay all updates).
        """
        path = distribution().locate_file("models/test-models/diagram-#4.gaphor")
        load(path, self.element_factory)

    def test_bug_idle(self):
        """
        Load file in gtk main loop.

        This does not nearly resemble the error, since the model should
        be loaded from within the mainloop (which will delay all updates).
        """

        def handler():
            try:
                path = distribution().locate_file(
                    "models/test-models/diagram-#4.gaphor"
                )
                load(path, self.element_factory)
            finally:
                Gtk.main_quit()

        assert GLib.timeout_add(1, handler) > 0
        Gtk.main()


# vi:sw=4:et:ai
