from gaphor.abc import Service


class SelfTest(Service):
    def __init__(self):
        pass

    def shutdown(self):
        pass

    def init(self, gtk_app):
        print("Performing self test")
        gtk_app.quit()
