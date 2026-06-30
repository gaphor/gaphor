from gi.repository import Gtk


def test_placement_cursor(view):
    window = Gtk.Window()
    window.set_child(view)
    window.present()
    assert view.get_cursor() is None

    view.set_placement_cursor("gaphor-box-symbolic")

    assert view.get_cursor()
