try:
    import gi

    gi.require_version("GtkosxApplication", "1.0")
except ValueError:
    macos_init = None
else:
    from gi.repository import Gio, GtkosxApplication

    macos_app = GtkosxApplication.Application.get()

    def open_file(macos_app, path, gtk_app):
        if path == __file__:
            return False

        gtk_app.open([Gio.File.new_for_path(path)], "")

        return True

    def block_termination(macos_app, application):
        quit = application.quit()
        return not quit

    def macos_init(application, gtk_app):
        macos_app.connect("NSApplicationOpenFile", open_file, gtk_app)
        macos_app.connect(
            "NSApplicationBlockTermination", block_termination, application
        )
