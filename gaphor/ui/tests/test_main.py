import sys

import pytest
from gi.repository import GLib, Gtk

import gaphor.main

APP_NAME = sys.argv[0]


@pytest.fixture(autouse=True)
def custom_application_id():
    orig_app_id = gaphor.ui.APPLICATION_ID
    gaphor.ui.APPLICATION_ID = "org.gaphor.TestMain"
    yield
    gaphor.ui.APPLICATION_ID = orig_app_id


def fake_run(monkeypatch):
    run = []

    def fake_run(self, args):
        run.extend(args)
        # NB. Priority used to be GLib.PRIORITY_LOW + GLib.PRIORITY_LOW,
        # but that makes the tests hang. Is an idle loop blocking us?
        GLib.idle_add(self.quit, priority=GLib.PRIORITY_LOW)
        app_run(self, args)

    app_run = Gtk.Application.run
    monkeypatch.setattr(Gtk.Application, "run", fake_run)

    return run


def test_application_startup(monkeypatch):
    run = fake_run(monkeypatch)

    gaphor.main.main([APP_NAME])

    assert run == [APP_NAME]


def test_application_startup_with_model(monkeypatch):
    run = fake_run(monkeypatch)

    gaphor.main.main([APP_NAME, "test-models/all-elements.gaphor"])

    assert run == [APP_NAME, "test-models/all-elements.gaphor"]
