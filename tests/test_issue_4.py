"""
Test GitHub issue #4. Diagram could not be loaded due to JuggleError
(presumed cyclic resolving of diagram items).
"""
import os
import pkg_resources

from gaphor.tests import TestCase
from gaphor import UML
from gaphor.storage.storage import load


class CyclicDiagramTestCase(TestCase):

    #services = TestCase.services + ['undo_manager']

    def setUp(self):
        super(CyclicDiagramTestCase, self).setUp()

    def test_bug(self):
        """
        Load file.

        This does not nearly resemble the error, since the model should
        be loaded from within the mainloop (which will delay all updates).
        """
        dist = pkg_resources.get_distribution('gaphor')
        path = os.path.join(dist.location, 'test-diagrams/diagram-#4.gaphor')
        load(path, self.element_factory)

    def test_bug_idle(self):
        """
        Load file in gtk main loop.

        This does not nearly resemble the error, since the model should
        be loaded from within the mainloop (which will delay all updates).
        """
        import gobject, gtk
        def handler():
            try:
                dist = pkg_resources.get_distribution('gaphor')
                path = os.path.join(dist.location, 'test-diagrams/diagram-#4.gaphor')
                load(path, self.element_factory)
            finally:
                Gtk.main_quit()

        assert GObject.timeout_add(1, handler) > 0
        Gtk.main()


# vi:sw=4:et:ai
