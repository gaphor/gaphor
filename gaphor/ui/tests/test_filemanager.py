import sys
import textwrap

import pytest
from dulwich.repo import Repo

from gaphor import UML
from gaphor.storage.tests.fixtures import create_merge_conflict
from gaphor.ui.filemanager import FileManager


@pytest.fixture
def file_manager(event_manager, element_factory, modeling_language):
    main_window = None
    file_manager = FileManager(
        event_manager, element_factory, modeling_language, main_window
    )
    yield file_manager
    file_manager.shutdown()


@pytest.mark.asyncio
async def test_save(element_factory, file_manager: FileManager, tmp_path):
    element_factory.create(UML.Class)
    out_file = tmp_path / "out.gaphor"

    await file_manager.save(filename=out_file)

    assert out_file.exists()


@pytest.mark.asyncio
async def test_model_is_saved_with_utf8_encoding(
    element_factory, file_manager: FileManager, tmp_path
):
    class_ = element_factory.create(UML.Class)
    class_.name = "üëïèàòù"
    package = element_factory.create(UML.Package)
    package.name = "안녕하세요 세계"

    model_file = tmp_path / "model.gaphor"
    await file_manager.save(model_file)

    with open(model_file, encoding="utf-8") as f:
        f.read()  # raises exception if characters can't be decoded


@pytest.mark.asyncio
async def test_model_is_loaded_with_utf8_encoding(
    element_factory, file_manager: FileManager, tmp_path
):
    class_name = "üëïèàòù"
    package_name = "안녕하세요 세계"

    class_ = element_factory.create(UML.Class)
    class_.name = class_name
    package = element_factory.create(UML.Package)
    package.name = package_name

    model_file = tmp_path / "model.gaphor"
    await file_manager.save(model_file)

    element_factory.flush()

    await file_manager.load(model_file)
    new_class = next(element_factory.select(UML.Class))
    new_package = next(element_factory.select(UML.Package))

    assert new_class.name == class_name
    assert new_package.name == package_name


@pytest.mark.skipif(
    sys.platform != "win32", reason="Standard encoding on Windows is not UTF-8"
)
@pytest.mark.asyncio
async def test_old_model_is_loaded_without_utf8_encoding(
    file_manager: FileManager, test_models
):
    model_file = test_models / "wrong-encoding.gaphor"
    await file_manager.load(model_file)


@pytest.mark.asyncio
@pytest.mark.parametrize("resolution", ["current", "incoming"])
@pytest.mark.filterwarnings("ignore:use .* Repo._get_user_identity:DeprecationWarning")
async def test_load_model_with_merge_conflict(
    file_manager: FileManager, element_factory, merge_conflict, monkeypatch, resolution
):
    replace_merge_conflict_dialog(monkeypatch, resolution)

    await file_manager.resolve_merge_conflict(merge_conflict)

    assert element_factory.size() > 0


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore:use .* Repo._get_user_identity:DeprecationWarning")
async def test_load_model_merge_conflict_and_manual_resolution(
    file_manager: FileManager, element_factory, merge_conflict, monkeypatch
):
    replace_merge_conflict_dialog(monkeypatch, "manual")

    await file_manager.resolve_merge_conflict(merge_conflict)

    from gaphor.core.modeling import PendingChange

    assert element_factory.lselect(PendingChange)


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore:use .* Repo._get_user_identity:DeprecationWarning")
async def test_load_model_with_merge_conflict_and_unknown_resolution(
    file_manager: FileManager, merge_conflict, monkeypatch
):
    replace_merge_conflict_dialog(monkeypatch, "nonsense")

    with pytest.raises(ValueError):
        await file_manager.resolve_merge_conflict(merge_conflict)


def replace_merge_conflict_dialog(monkeypatch, resolution):
    async def mock_merge_conflict_dialog(_window):
        return resolution

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
