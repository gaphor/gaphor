try:
    import gi

    gi.require_version("GtkosxApplication", "1.0")
except ValueError:
    macos_init = None
else:
    from gi.repository import GtkosxApplication

    macos_app = GtkosxApplication.Application.get()

    def open_file(macos_app, path, application):
        if path == __file__:
            return False

        app_file_manager = application.get_service("app_file_manager")
        app_file_manager.load(path)

        return True

    def block_termination(macos_app, application):
        quit = application.quit()
        return not quit

    def macos_init(application):
        macos_app.connect("NSApplicationOpenFile", open_file, application)
        macos_app.connect(
            "NSApplicationBlockTermination", block_termination, application
        )
