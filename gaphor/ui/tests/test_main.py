from gi.repository import GLib, Gtk

from gaphor.ui import main


def fake_run(monkeypatch):
    run = []

    def fake_run(self, args):
        run.extend(args)
        idle = GLib.Idle(GLib.PRIORITY_LOW)
        idle.set_callback(lambda *a: self.quit())
        idle.attach()
        app_run(self, args)

    app_run = getattr(Gtk.Application, "run")
    monkeypatch.setattr(Gtk.Application, "run", fake_run)

    return run


def test_application_startup(monkeypatch):
    run = fake_run(monkeypatch)

    main(["gaphor"])

    assert run == ["gaphor"]


def test_application_startup_with_model(monkeypatch):
    run = fake_run(monkeypatch)

    main(["gaphor", "test-models/all-elements.gaphor"])

    assert run == ["gaphor", "test-models/all-elements.gaphor"]
