import sys
import textwrap
import time

import pytest
from dulwich.repo import Repo
from gi.repository import GLib

from gaphor import UML
from gaphor.core import event_handler
from gaphor.event import ModelChangedOnDisk
from gaphor.storage.tests.fixtures import create_merge_conflict
from gaphor.ui.filemanager import FileManager


def iteration(sentinel):
    ctx = GLib.main_context_default()
    while ctx.pending():
        ctx.iteration(False)
        if not sentinel():
            time.sleep(0.1)


@pytest.fixture
def file_manager(event_manager, element_factory, modeling_language):
    main_window = None
    return FileManager(event_manager, element_factory, modeling_language, main_window)


def test_save(element_factory, file_manager: FileManager, tmp_path):
    element_factory.create(UML.Class)
    out_file = tmp_path / "out.gaphor"

    file_manager.save(filename=out_file)

    assert out_file.exists()


def test_model_is_saved_with_utf8_encoding(
    element_factory, file_manager: FileManager, tmp_path
):
    class_ = element_factory.create(UML.Class)
    class_.name = "üëïèàòù"
    package = element_factory.create(UML.Package)
    package.name = "안녕하세요 세계"

    model_file = tmp_path / "model.gaphor"
    file_manager.save(model_file)

    with open(model_file, encoding="utf-8") as f:
        f.read()  # raises exception if characters can't be decoded


def test_model_is_loaded_with_utf8_encoding(
    element_factory, file_manager: FileManager, tmp_path
):
    class_name = "üëïèàòù"
    package_name = "안녕하세요 세계"

    class_ = element_factory.create(UML.Class)
    class_.name = class_name
    package = element_factory.create(UML.Package)
    package.name = package_name

    model_file = tmp_path / "model.gaphor"
    file_manager.save(model_file)

    element_factory.flush()

    file_manager.load(model_file)
    new_class = next(element_factory.select(UML.Class))
    new_package = next(element_factory.select(UML.Package))

    assert new_class.name == class_name
    assert new_package.name == package_name


def test_notify_changes(
    event_manager, element_factory, file_manager: FileManager, tmp_path
):
    @event_handler(ModelChangedOnDisk)
    def on_changed_on_disk(_event):
        nonlocal notified
        notified = True

    element_factory.create(UML.Class)
    out_file = tmp_path / "out.gaphor"
    file_manager.save(filename=out_file)
    notified = False
    event_manager.subscribe(on_changed_on_disk)

    out_file.write_text("a", encoding="utf-8")
    iteration(lambda: notified)

    assert notified


@pytest.mark.skipif(
    sys.platform != "win32", reason="Standard encoding on Windows is not UTF-8"
)
def test_old_model_is_loaded_without_utf8_encoding(
    file_manager: FileManager, test_models
):
    model_file = test_models / "wrong-encoding.gaphor"
    file_manager.load(model_file)


@pytest.mark.parametrize("resolution", ["current", "incoming"])
@pytest.mark.filterwarnings("ignore:use .* Repo._get_user_identity:DeprecationWarning")
def test_load_model_with_merge_conflict(
    file_manager: FileManager, element_factory, merge_conflict, monkeypatch, resolution
):
    replace_merge_conflict_dialog(monkeypatch, resolution)

    file_manager.resolve_merge_conflict(merge_conflict)

    assert element_factory.size() > 0


@pytest.mark.filterwarnings("ignore:use .* Repo._get_user_identity:DeprecationWarning")
def test_load_model_merge_conflict_and_manual_resolution(
    file_manager: FileManager, element_factory, merge_conflict, monkeypatch
):
    replace_merge_conflict_dialog(monkeypatch, "manual")

    file_manager.resolve_merge_conflict(merge_conflict)

    from gaphor.core.modeling import PendingChange

    assert element_factory.lselect(PendingChange)


@pytest.mark.filterwarnings("ignore:use .* Repo._get_user_identity:DeprecationWarning")
def test_load_model_with_merge_conflict_and_unknown_resolution(
    file_manager: FileManager, merge_conflict, monkeypatch
):
    replace_merge_conflict_dialog(monkeypatch, "nonsense")

    with pytest.raises(ValueError):
        file_manager.resolve_merge_conflict(merge_conflict)


def replace_merge_conflict_dialog(monkeypatch, resolution):
    def mock_merge_conflict_dialog(_window, handler):
        handler(resolution)

    monkeypatch.setattr(
        "gaphor.ui.filemanager.resolve_merge_conflict_dialog",
        mock_merge_conflict_dialog,
    )


@pytest.fixture
def merge_conflict(tmp_path):
    initial_model = textwrap.dedent(
        """\
        <?xml version="1.0" encoding="utf-8"?>
        <gaphor xmlns="http://gaphor.sourceforge.net/model" version="3.0" gaphor-version="2.12.1">
        <StyleSheet id="58d6989a-66f8-11ec-b4c8-0456e5e540ed"/>
        <Package id="58d6c2e8-66f8-11ec-b4c8-0456e5e540ed">
        <name>
        <val>current</val>
        </name>
        </Package>
        </gaphor>
        """
    )

    current_model = textwrap.dedent(
        """\
        <?xml version="1.0" encoding="utf-8"?>
        <gaphor xmlns="http://gaphor.sourceforge.net/model" version="3.0" gaphor-version="2.12.1">
        <StyleSheet id="58d6989a-66f8-11ec-b4c8-0456e5e540ed"/>
        <Package id="58d6c2e8-66f8-11ec-b4c8-0456e5e540ed">
        <name>
        <val>current</val>
        </name>
        <ownedDiagram>
        <reflist>
        <ref refid="58d6c536-66f8-11ec-b4c8-0456e5e540ed"/>
        </reflist>
        </ownedDiagram>
        </Package>
        <Diagram id="58d6c536-66f8-11ec-b4c8-0456e5e540ed">
        <element>
        <ref refid="58d6c2e8-66f8-11ec-b4c8-0456e5e540ed"/>
        </element>
        <name>
        <val>diagram</val>
        </name>
        </Diagram>
        </gaphor>"""
    )

    incoming_model = textwrap.dedent(
        """\
        <?xml version="1.0" encoding="utf-8"?>
        <gaphor xmlns="http://gaphor.sourceforge.net/model" version="3.0" gaphor-version="2.12.1">
        <StyleSheet id="58d6989a-66f8-11ec-b4c8-0456e5e540ed"/>
        <Package id="58d6c2e8-66f8-11ec-b4c8-0456e5e540ed">
        <name>
        <val>incoming</val>
        </name>
        </Package>
        </gaphor>"""
    )

    model = tmp_path / "model.gaphor"
    repo = Repo.init(tmp_path)

    create_merge_conflict(repo, model, initial_model, current_model, incoming_model)

    return model
