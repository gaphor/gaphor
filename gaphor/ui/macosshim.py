try:
    import gi
    from gi.repository import Gtk

    if Gtk.get_major_version() == 3:
        gi.require_version("GtkosxApplication", "1.0")
    else:
        raise ValueError()
except ValueError:
    macos_init = None
else:
    from gi.repository import GtkosxApplication

    macos_app = GtkosxApplication.Application.get()

    def open_file(macos_app, path, application):
        if path == __file__:
            return False

        application.new_session(filename=path)

        return True

    def block_termination(macos_app, application):
        quit = application.quit()
        return not quit

    def macos_init(application):
        macos_app.connect("NSApplicationOpenFile", open_file, application)
        macos_app.connect(
            "NSApplicationBlockTermination", block_termination, application
        )
