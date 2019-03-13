"""
Setup script for Gaphor.

Run 'python setup.py develop' to set up a development environment, including
dependencies.
"""

import sys

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

from utils.command.build_mo import build_mo
from utils.command.build_pot import build_pot
from utils.command.build_uml import build_uml
from utils.command.install_lib import install_lib

VERSION = "1.0.0rc1"
LINGUAS = ["ca", "es", "fr", "nl", "sv"]

sys.path.insert(0, ".")


class BuildPyWithSubCommands(build_py):
    """Wraps setuptools build_py.

    Ensure that build_uml is performed before build_py is run
    """

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        build_py.run(self)


BuildPyWithSubCommands.sub_commands.append(("build_uml", None))

setup(
    name="gaphor",
    version=VERSION,
    url="https://github.org/gaphor/gaphor",
    author="Arjan J. Molenaar",
    author_email="gaphor@gmail.com",
    license="GNU Lesser General Public License",
    description="Gaphor is a UML modeling tool",
    long_description="""
Gaphor is a simple modeling tool written in Python.

It uses the GTK+ environment for user interaction.
""",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
        "Topic :: Software Development :: Documentation",
    ],
    keywords="model modeling modelling uml diagram python tool",
    packages=find_packages(exclude=["utils"]),
    package_data={"": ["LICENSE.txt", "*.xml", "*.png"]},
    include_package_data=True,
    install_requires=[
        "pycairo >= 1.16.3",
        "PyGObject >= 3.30.0",
        "gaphas >= 1.0.0",
        "zope.component >= 3.4.0",
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "gaphor = gaphor:main",
            "gaphorconvert = gaphor.tools.gaphorconvert:main",
        ],
        "gaphor.services": [
            "component_registry = gaphor.services.componentregistry:ZopeComponentRegistry",
            # 'event_dispatcher = gaphor.services.eventdispatcher:EventDispatcher',
            "adapter_loader = gaphor.services.adapterloader:AdapterLoader",
            "properties = gaphor.services.properties:Properties",
            "undo_manager = gaphor.services.undomanager:UndoManager",
            "element_factory = gaphor.UML.elementfactory:ElementFactoryService",
            "file_manager = gaphor.services.filemanager:FileManager",
            "diagram_export_manager = gaphor.services.diagramexportmanager:DiagramExportManager",
            "action_manager = gaphor.services.actionmanager:ActionManager",
            "ui_manager = gaphor.services.actionmanager:UIManager",
            "main_window = gaphor.ui.mainwindow:MainWindow",
            "copy = gaphor.services.copyservice:CopyService",
            "sanitizer = gaphor.services.sanitizerservice:SanitizerService",
            "element_dispatcher = gaphor.services.elementdispatcher:ElementDispatcher",
            # 'property_dispatcher = gaphor.services.propertydispatcher:PropertyDispatcher',
            "xmi_export = gaphor.plugins.xmiexport:XMIExport",
            "diagram_layout = gaphor.plugins.diagramlayout:DiagramLayout",
            "pynsource = gaphor.plugins.pynsource:PyNSource",
            # 'check_metamodel = gaphor.plugins.checkmetamodel:CheckModelWindow',
            # 'live_object_browser = gaphor.plugins.liveobjectbrowser:LiveObjectBrowser',
            "alignment = gaphor.plugins.alignment:Alignment",
            "help = gaphor.services.helpservice:HelpService",
        ],
        "gaphor.uicomponents": [
            # 'mainwindow = gaphor.ui.mainwindow:MainWindow',
            "namespace = gaphor.ui.mainwindow:Namespace",
            "toolbox = gaphor.ui.mainwindow:Toolbox",
            "diagrams = gaphor.ui.mainwindow:Diagrams",
            "consolewindow = gaphor.ui.consolewindow:ConsoleWindow",
            "elementeditor = gaphor.ui.elementeditor:ElementEditor",
        ],
    },
    cmdclass={
        "build_py": BuildPyWithSubCommands,
        "build_uml": build_uml,
        "build_mo": build_mo,
        "build_pot": build_pot,
        "install_lib": install_lib,
    },
    tests_require=["pytest"],
    options=dict(
        build_pot=dict(all_linguas=",".join(LINGUAS)),
        build_mo=dict(all_linguas=",".join(LINGUAS)),
    ),
)
