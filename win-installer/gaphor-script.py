if __name__ == "__main__":
    import gaphor
    from gaphor import core
    from gaphor.UML.elementfactory import ElementFactory
    from gaphor.plugins.console import ConsoleWindow
    from gaphor.plugins.diagramexport import DiagramExport
    from gaphor.plugins.xmiexport import XMIExport
    from gaphor.services.componentregistry import ComponentRegistry
    from gaphor.services.copyservice import CopyService
    from gaphor.services.eventmanager import EventManager
    from gaphor.services.helpservice import HelpService
    from gaphor.services.properties import Properties
    from gaphor.services.sanitizerservice import SanitizerService
    from gaphor.services.session import Session
    from gaphor.services.undomanager import UndoManager
    from gaphor.ui.elementeditor import ElementEditor
    from gaphor.ui.appfilemanager import AppFileManager
    from gaphor.ui.filemanager import FileManager
    from gaphor.ui.mainwindow import Diagrams
    from gaphor.ui.mainwindow import MainWindow
    from gaphor.ui.menufragment import MenuFragment
    from gaphor.ui.namespace import Namespace
    from gaphor.ui.preferences import Preferences
    from gaphor.ui.recentfiles import RecentFiles
    from gaphor.ui.toolbox import Toolbox
    from gaphor.ui import main
    import sys

    main(sys.argv)
