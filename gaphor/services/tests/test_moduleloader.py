import sys

from gaphor.services.moduleloader import ModuleLoader


def test_module_loader():
    ModuleLoader()

    assert "gaphor.diagram.general.uicomponents" in sys.modules
    assert "gaphor.UML.uicomponents" in sys.modules
    assert "gaphor.SysML.propertypages" in sys.modules
    assert "gaphor.C4Model.propertypages" in sys.modules
