"""Setup script for Gaphor.

Run './venv' to set up a development environment, including dependencies.
"""

import io
import os
import sys
import re

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

from utils.command.build_mo import build_mo
from utils.command.build_pot import build_pot
from utils.command.build_uml import build_uml
from utils.command.install_lib import install_lib

VERSION = "1.0.0rc3"
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


version_file = os.path.join(os.path.dirname(__file__), "gaphor", "__init__.py")
with io.open(version_file, encoding="utf8") as version_file:
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M
    )
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

BuildPyWithSubCommands.sub_commands.append(("build_uml", None))

readme = os.path.join(os.path.dirname(__file__), "README.md")
with io.open(readme, encoding="utf8") as readme:
    long_description = readme.read()

setup(
    name="gaphor",
    version=version,
    url="https://gaphor.readthedocs.io/",
    author="Arjan J. Molenaar",
    author_email="gaphor@gmail.com",
    license="GNU Lesser General Public License",
    description="Gaphor is the simple modeling tool",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU Lesser General Public License (LGPL)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
        "Topic :: Software Development :: Documentation",
    ],
    keywords="model modeling modelling uml diagram python tool",
    packages=find_packages(
        exclude=[
            "utils*",
            "docs",
            "tests",
            "windows",
            "macOS",
            "linux",
            "iOS",
            "android",
            "django",
        ]
    ),
    include_package_data=True,
    install_requires=[
        "pycairo >= 1.17.0",
        "PyGObject >= 3.30.0",
        "gaphas >= 0.7.2",
        "zope.component >= 3.4.0",
        "zope.interface >= 4.6.0",
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "gaphor = gaphor:main",
            "gaphorconvert = gaphor.tools.gaphorconvert:main",
        ],
        "gaphor.services": [
            "component_registry = gaphor.services.componentregistry:ZopeComponentRegistry",
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
            "xmi_export = gaphor.plugins.xmiexport:XMIExport",
            "diagram_layout = gaphor.plugins.diagramlayout:DiagramLayout",
            "pynsource = gaphor.plugins.pynsource:PyNSource",
            "alignment = gaphor.plugins.alignment:Alignment",
            "help = gaphor.services.helpservice:HelpService",
        ],
        "gaphor.uicomponents": [
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
    options={
        "app": {"formal_name": "Gaphor", "bundle": "org.gaphor"},
        # Desktop/laptop deployments
        "macos": {"app_requires": [], "icon": "package/icons/gaphor"},
        "linux": {"app_requires": []},
        "windows": {"app_requires": []},
        # Mobile deployments
        "ios": {"app_requires": []},
        "android": {"app_requires": []},
        # Web deployments
        "django": {"app_requires": []},
        # Translations
        "build_pot": {"all_linguas": ",".join(LINGUAS)},
        "build_mo": {"all_linguas": ",".join(LINGUAS)},
    },
)
