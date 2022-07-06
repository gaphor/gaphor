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

    file_manager.save(filename=str(out_file))

    assert out_file.exists()


def test_model_is_saved_with_utf8_encoding(
    element_factory, file_manager: FileManager, tmp_path
):
    class_ = element_factory.create(UML.Class)
    class_.name = "üëïèàòù"
    package = element_factory.create(UML.Package)
    package.name = "안녕하세요 세계"

    model_file = tmp_path / "model.gaphor"
    file_manager.save(str(model_file))

    with open(model_file, encoding="utf-8") as f:
        f.read()  # raises exception if characters can't be decoded
