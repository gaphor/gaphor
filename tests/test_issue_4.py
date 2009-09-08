"""
Test GitHub issue #4. Diagram could not be loaded due to JuggleError
(presumed cyclic resolving of diagram items).
"""

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
        load('test-diagrams/diagram-#4.gaphor', self.element_factory)

    def test_bug_idle(self):
        """
        Load file in gtk main loop.

        This does not nearly resemble the error, since the model should
        be loaded from within the mainloop (which will delay all updates).
        """
        import gobject, gtk
        def handler():
            try:
                load('test-diagrams/diagram-#4.gaphor', self.element_factory)
            finally:
                gtk.main_quit()

        assert gobject.timeout_add(1, handler) > 0
        gtk.main()


# vi:sw=4:et:ai
