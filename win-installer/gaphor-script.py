if __name__ == "__main__":
    import gaphor
    from gaphor import core
    from gaphor.services.componentregistry import ComponentRegistry
    from gaphor.ui.consolewindow import ConsoleWindow
    from gaphor.services.copyservice import CopyService
    from gaphor.plugins.diagramlayout import DiagramLayout
    from gaphor.ui.mainwindow import Diagrams
    from gaphor.UML.elementfactory import ElementFactory
    from gaphor.ui.elementeditor import ElementEditor
    from gaphor.services.eventmanager import EventManager
    from gaphor.services.helpservice import HelpService
    from gaphor.ui.mainwindow import MainWindow
    from gaphor.services.properties import Properties
    from gaphor.plugins.pynsource import PyNSource
    from gaphor.services.sanitizerservice import SanitizerService
    from gaphor.services.undomanager import UndoManager
    from gaphor.plugins.xmiexport import XMIExport

    gaphor.main()
