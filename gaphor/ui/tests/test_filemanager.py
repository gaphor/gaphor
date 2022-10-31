import sys

import pytest

from gaphor import UML
from gaphor.ui.filemanager import FileManager


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


@pytest.mark.skipif(
    sys.platform != "win32", reason="Standard encoding on Windows is not UTF-8"
)
def test_old_model_is_loaded_without_utf8_encoding(
    file_manager: FileManager, test_models
):
    model_file = test_models / "wrong-encoding.gaphor"
    file_manager.load(model_file)


@pytest.mark.parametrize("resolution", ["current", "incoming"])
def test_load_model_with_merge_conflict(
    file_manager: FileManager, test_models, resolution
):
    model_file = test_models / "merge-conflict.gaphor"

    file_manager.resolve_merge_conflict(model_file, resolution)


def test_load_model_with_merge_conflict_and_unknown_resolution(
    file_manager: FileManager, test_models
):
    model_file = test_models / "merge-conflict.gaphor"

    with pytest.raises(RuntimeError):
        file_manager.resolve_merge_conflict(model_file, "nonsense")
