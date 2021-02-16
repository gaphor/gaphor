"""Test GitHub issue #4.

Diagram could not be loaded due to JuggleError (presumed cyclic
resolving of diagram items).
"""

from gi.repository import GLib, Gtk

from gaphor.application import distribution
from gaphor.storage.storage import load


class TestCyclicDiagram:
    def test_bug(self, case):
        """Load file.

        This does not nearly resemble the error, since the model should
        be loaded from within the mainloop (which will delay all
        updates).
        """
        path = distribution().locate_file("test-models/dbus.gaphor")
        load(path, case.element_factory, case.modeling_language)

    def test_bug_idle(self, case):
        """Load file in gtk main loop.

        This does not nearly resemble the error, since the model should
        be loaded from within the mainloop (which will delay all
        updates).
        """

        def handler():
            try:
                path = distribution().locate_file("test-models/dbus.gaphor")
                load(path, case.element_factory, case.modeling_language)
            finally:
                Gtk.main_quit()

        assert GLib.timeout_add(1, handler) > 0
        Gtk.main()
