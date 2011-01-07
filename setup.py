"""
Setup script for Gaphor.

Run 'python setup.py develop' to set up a development environment, including
dependencies.
"""

VERSION = '0.16.0'

import os
import sys
sys.path.insert(0, '.')

from ez_setup import use_setuptools

use_setuptools()

from setuptools import setup, find_packages
from distutils.cmd import Command
#try:
from sphinx.setup_command import BuildDoc
#except ImportError, e:
#    print 'No Sphynx found'

from utils.command.build_mo import build_mo
from utils.command.build_pot import build_pot
from utils.command.build_uml import build_uml
from utils.command.install_lib import install_lib
from utils.command.run import run

LINGUAS = [ 'ca', 'es', 'fr', 'nl', 'sv' ]


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
    url='http://gaphor.sourceforge.net',
    author='Arjan J. Molenaar',
    author_email='arjanmol@users.sourceforge.net',
    license='GNU General Public License',
    description='Gaphor is a UML modeling tool',
    long_description="""
Gaphor is a UML modeling tool written in Python.

It uses the GTK+ environment for user interaction.
""",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Graphics :: Editors :: Vector-Based',
        'Topic :: Software Development :: Documentation',
    ],

    keywords = 'model modeling modelling uml diagram python tool',

    packages = find_packages(exclude=['ez_setup', 'utils*']),

    include_package_data = True,

    install_requires = [
        # 'PyGTK >= 2.8.0', - Exclude, since it will not build anyway
        'gaphas >= 0.7.0',
        'zope.component >= 3.4.0', # - won't compile on windows.
    ],

    zip_safe = False,

    #test_suite = 'nose.collector',

    entry_points = {
        'console_scripts': [
            'gaphor = gaphor:main',
            'gaphorconvert = gaphor.tools.gaphorconvert:main',
        ],
        'gaphor.services': [
            #'component_registry = gaphor.services.componentregistry:ZopeComponentRegistry',
            'event_dispatcher = gaphor.services.eventdispatcher:EventDispatcher',
            'adapter_loader = gaphor.services.adapterloader:AdapterLoader',
            'properties = gaphor.services.properties:Properties',
            'undo_manager = gaphor.services.undomanager:UndoManager',
            'element_factory = gaphor.UML.elementfactory:ElementFactory',
            'file_manager = gaphor.services.filemanager:FileManager',
            #'backup_service = gaphor.services.backupservice:BackupService',
            'diagram_export_manager = gaphor.services.diagramexportmanager:DiagramExportManager',
            'action_manager = gaphor.services.actionmanager:ActionManager',
            'gui_manager = gaphor.services.guimanager:GUIManager',
            'copy = gaphor.services.copyservice:CopyService',
            'sanitizer = gaphor.services.sanitizerservice:SanitizerService',
            'element_dispatcher = gaphor.services.elementdispatcher:ElementDispatcher',
            #'property_dispatcher = gaphor.services.propertydispatcher:PropertyDispatcher',
            'xmi_export = gaphor.plugins.xmiexport:XMIExport',
            'diagram_layout = gaphor.plugins.diagramlayout:DiagramLayout',
            'pynsource = gaphor.plugins.pynsource:PyNSource',
            #'check_metamodel = gaphor.plugins.checkmetamodel:CheckModelWindow',
            #'live_object_browser = gaphor.plugins.liveobjectbrowser:LiveObjectBrowser',
            'alignment = gaphor.plugins.alignment:Alignment',
            'help = gaphor.services.helpservice:HelpService',
        ],
        'gaphor.uicomponents': [
            'mainwindow = gaphor.ui.mainwindow:MainWindow',
            'consolewindow = gaphor.ui.consolewindow:ConsoleWindow',
            'elementeditor = gaphor.ui.elementeditor:ElementEditor',
        ],
    },

    cmdclass = {
              'build_py': build_py_with_sub_commands,
              'build_uml': build_uml,
              'build_doc': BuildDoc,
              'build_mo': build_mo,
              'build_pot': build_pot,
              'install_lib': install_lib,
              'run': run,
    },

    setup_requires = [
        'Sphinx >= 1.0.6',
        'nose >= 0.10.4',
        'setuptools-git >= 0.3.4'
    ],

    test_suite = 'nose.collector',

    options = dict(
        build_pot = dict(
            all_linguas = ','.join(LINGUAS),
        ),
        build_mo = dict(
            all_linguas = ','.join(LINGUAS),
        ),

    ),
)
 
# vim:sw=4:et:ai
