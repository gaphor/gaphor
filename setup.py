"""Setup script for Gaphor.

Run './venv' to set up a development environment, including dependencies.
"""

import io
import os
import sys
import re

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

from utils.i18n.build_mo import build_mo
from utils.i18n.build_pot import build_pot
from utils.model.build_uml import build_uml
from utils.install_lib import install_lib

VERSION = "1.1.0"
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
with open(version_file, encoding="utf8") as version_file:
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M
    )
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

BuildPyWithSubCommands.sub_commands.append(("build_uml", None))

readme = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme, encoding="utf8") as readme:
    long_description = readme.read()

setup(
    name="gaphor",
    version=version,
    url="https://gaphor.readthedocs.io/",
    author="Arjan J. Molenaar",
    author_email="gaphor@gmail.com",
    description="Gaphor is the simple modeling tool",
    long_description=long_description,
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
    packages=find_packages(exclude=["utils*", "docs", "tests"]),
    include_package_data=True,
    install_requires=[
        "pycairo >= 1.17.0",
        "PyGObject >= 3.30.0",
        "gaphas >= 0.7.2",
        "importlib_metadata >= 0.17",
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "gaphor = gaphor:main",
            "gaphorconvert = gaphor.tools.gaphorconvert:main",
        ],
        "gaphor.services": [
            "component_registry = gaphor.services.componentregistry:ComponentRegistry",
            "event_manager = gaphor.services.eventmanager:EventManager",
            "properties = gaphor.services.properties:Properties",
            "undo_manager = gaphor.services.undomanager:UndoManager",
            "element_factory = gaphor.UML.elementfactory:ElementFactory",
            "file_manager = gaphor.ui.filemanager:FileManager",
            "recent_files = gaphor.ui.recentfiles:RecentFiles",
            "main_window = gaphor.ui.mainwindow:MainWindow",
            "preferences = gaphor.ui.preferences:Preferences",
            "export_menu = gaphor.ui.menufragment:MenuFragment",
            "tools_menu = gaphor.ui.menufragment:MenuFragment",
            "copy = gaphor.services.copyservice:CopyService",
            "sanitizer = gaphor.services.sanitizerservice:SanitizerService",
            "help = gaphor.services.helpservice:HelpService",
            "namespace = gaphor.ui.namespace:Namespace",
            "toolbox = gaphor.ui.toolbox:Toolbox",
            "diagrams = gaphor.ui.mainwindow:Diagrams",
            "consolewindow = gaphor.plugins.console:ConsoleWindow",
            "elementeditor = gaphor.ui.elementeditor:ElementEditor",
            "diagram_export = gaphor.plugins.diagramexport:DiagramExport",
            "xmi_export = gaphor.plugins.xmiexport:XMIExport",
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
        # Translations
        "build_pot": {"all_linguas": ",".join(LINGUAS)},
        "build_mo": {"all_linguas": ",".join(LINGUAS)},
    },
)
