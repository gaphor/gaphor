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
