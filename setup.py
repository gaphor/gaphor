#!/usr/bin/env python

# Copyright (C) 2003-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#                         slmm <noreply@example.com>
#                         wrobell <wrobell@pld-linux.org>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Setup script for Gaphor.

Run 'python setup.py develop' to set up a development environment, including
dependencies.
"""

from __future__ import absolute_import

VERSION = '0.17.2'

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# try:
# from sphinx.setup_command import BuildDoc
# except ImportError, e:
#    print 'No Sphynx found'

from utils.command.build_mo import build_mo
from utils.command.build_pot import build_pot
from utils.command.build_uml import build_uml
from utils.command.install_lib import install_lib
from utils.command.run import run

LINGUAS = ['ca', 'es', 'fr', 'nl', 'sv']

# Wrap setuptools' build_py command, so we're sure build_uml is performed
# before the build_py code.

from setuptools.command.build_py import build_py


class build_py_with_sub_commands(build_py):
    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        build_py.run(self)


build_py_with_sub_commands.sub_commands.append(('build_uml', None))

setup(
    name='gaphor',
    version=VERSION,
    url='http://mbse.gitlab.io/gaphor',
    author='Dan Yeaw',
    author_email='dan@yeaw.me',
    license='GNU General Public License',
    description='Gaphor is a UML modeling tool',
    long_description="""
Gaphor is a UML modeling tool written in Python.

It uses the GTK+ environment for user interaction.
""",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Environment :: X11 Applications :: Gnome',
        'Environment :: X11 Applications :: GTK',
        'Environment :: Win32 (MS Windows)',
        'Environment :: MacOS X',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Graphics :: Editors :: Vector-Based',
        'Topic :: Software Development :: Documentation',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Zope3',
    ],

    keywords='model modeling modelling uml SysML diagram python tool',

    packages=find_packages(exclude=['utils*']),

    include_package_data=True,

    install_requires=[
        # 'PyGTK >= 2.8.0', - Exclude, since it will not build anyway
        'gaphas >= 0.7.2',
        'etk.docking >= 0.2',
        'zope.component >= 3.4.0',  # - won't compile on windows.
        'six > 1.9.0',
    ],

    zip_safe=False,

    # test_suite = 'nose.collector',

    entry_points={
        'console_scripts': [
            'gaphor = gaphor:main',
            'gaphorconvert = gaphor.tools.gaphorconvert:main',
        ],
        'gaphor.services': [
            'component_registry = gaphor.services.componentregistry:ZopeComponentRegistry',
            # 'event_dispatcher = gaphor.services.eventdispatcher:EventDispatcher',
            'adapter_loader = gaphor.services.adapterloader:AdapterLoader',
            'properties = gaphor.services.properties:Properties',
            'undo_manager = gaphor.services.undomanager:UndoManager',
            'element_factory = gaphor.UML.elementfactory:ElementFactoryService',
            'file_manager = gaphor.services.filemanager:FileManager',
            # 'backup_service = gaphor.services.backupservice:BackupService',
            'diagram_export_manager = gaphor.services.diagramexportmanager:DiagramExportManager',
            'action_manager = gaphor.services.actionmanager:ActionManager',
            'ui_manager = gaphor.services.actionmanager:UIManager',
            'main_window = gaphor.ui.mainwindow:MainWindow',
            'copy = gaphor.services.copyservice:CopyService',
            'sanitizer = gaphor.services.sanitizerservice:SanitizerService',
            'element_dispatcher = gaphor.services.elementdispatcher:ElementDispatcher',
            # 'property_dispatcher = gaphor.services.propertydispatcher:PropertyDispatcher',
            'xmi_export = gaphor.plugins.xmiexport:XMIExport',
            'diagram_layout = gaphor.plugins.diagramlayout:DiagramLayout',
            'pynsource = gaphor.plugins.pynsource:PyNSource',
            # 'check_metamodel = gaphor.plugins.checkmetamodel:CheckModelWindow',
            # 'live_object_browser = gaphor.plugins.liveobjectbrowser:LiveObjectBrowser',
            'alignment = gaphor.plugins.alignment:Alignment',
            'help = gaphor.services.helpservice:HelpService',
        ],
        'gaphor.uicomponents': [
            # 'mainwindow = gaphor.ui.mainwindow:MainWindow',
            'namespace = gaphor.ui.mainwindow:Namespace',
            'toolbox = gaphor.ui.mainwindow:Toolbox',
            'consolewindow = gaphor.ui.consolewindow:ConsoleWindow',
            'elementeditor = gaphor.ui.elementeditor:ElementEditor',
        ],
    },

    cmdclass={
        'build_py': build_py_with_sub_commands,
        'build_uml': build_uml,
        # 'build_doc': BuildDoc,
        'build_mo': build_mo,
        'build_pot': build_pot,
        'install_lib': install_lib,
        'run': run,
    },

    setup_requires=[
        # 'Sphinx >= 1.0.6',
        'nose >= 0.10.4',
        'setuptools-git >= 0.3.4'
    ],

    test_suite='nose.collector',

    options=dict(
        build_pot=dict(
            all_linguas=','.join(LINGUAS),
        ),
        build_mo=dict(
            all_linguas=','.join(LINGUAS),
        ),
    ),
)

# vim:sw=4:et:ai
