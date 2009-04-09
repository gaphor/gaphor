
from gaphor.ui.infowindow import InfoWindow
import unittest

class InfoWindowTestCase(unittest.TestCase):

    def test1(self):
        import gtk
        ui_manager = gtk.UIManager()
        window = InfoWindow()
        window.ui_manager = ui_manager
        assert len(window.action_group.list_actions()) == 1, window.action_group.list_actions()
        window.construct()
        window.close()

