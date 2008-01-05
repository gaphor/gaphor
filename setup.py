"""
Setup script for Gaphor.

Run 'python setup.py develop' to set up a development environment, including
dependencies.

Run 'python setup.py run' to start Gaphor directly (without install).
"""

VERSION = '0.12.5'

import os
import sys
sys.path.insert(0, '.')

from ez_setup import use_setuptools

use_setuptools()

from setuptools import setup, find_packages
from distutils.cmd import Command

from utils.command.build_mo import build_mo
from utils.command.build_pot import build_pot
from utils.command.build_uml import build_uml
from utils.command.install_lib import install_lib
from utils.command.run import run

LINGUAS = [ 'ca', 'es', 'nl', 'sv' ]

from setuptools.command.build_py import build_py

class build_py_with_sub_commands(build_py):

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        build_py.run(self)

build_py_with_sub_commands.sub_commands.append(('build_uml', None))


class build_doc(Command):
    description = 'Builds the documentation'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
#        from docutils.core import publish_cmdline
#        docutils_conf = os.path.join('doc', 'docutils.conf')
        epydoc_conf = os.path.join('doc', 'epydoc.conf')

#        for source in glob('doc/*.txt'):
#            dest = os.path.splitext(source)[0] + '.html'
#            if not os.path.exists(dest) or \
#                   os.path.getmtime(dest) < os.path.getmtime(source):
#                print 'building documentation file %s' % dest
#                publish_cmdline(writer_name='html',
#                                argv=['--config=%s' % docutils_conf, source,
#                                      dest])

        try:
            from epydoc import cli
            old_argv = sys.argv[1:]
            sys.argv[1:] = [
                '--config=%s' % epydoc_conf,
                '--no-private', # epydoc bug, not read from config
                '--simple-term',
                '--verbose'
            ]
            cli.cli()
            sys.argv[1:] = old_argv

        except ImportError:
            print 'epydoc not installed, skipping API documentation.'


#if sys.platform == 'darwin':
#    # Mac OS X
#    import pkg_resources
#    pkg_resources.require('zope.component')
#    platform_setup_requires=['py2app']
#    platform_setup = dict(
#        app=['gaphor-osx.py'],
#        )
#else:
platform_setup_requires = []
platform_setup = dict()


setup(
    name='gaphor',
    version=VERSION,
    url='http://gaphor.devjavu.com',
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
        'gaphas >= 0.3.0',
        'zope.component >= 3.3.0', # - won't compile on windows.
        # Add dependency on zope.testing to work around bug in zope.component
        'zope.testing >= 3.3.0',
    ],

    zip_safe = False,

    #test_suite = 'nose.collector',

    entry_points = {
        'console_scripts': [
            'gaphor = gaphor:main',
        ],
        'gaphor.services': [
            'adapter_loader = gaphor.services.adapterloader:AdapterLoader',
            'properties = gaphor.services.properties:Properties',
            'undo_manager = gaphor.services.undomanager:UndoManager',
            'element_factory = gaphor.UML.elementfactory:ElementFactory',
            'file_manager = gaphor.services.filemanager:FileManager',
            'diagram_export_manager = gaphor.services.diagramexportmanager:DiagramExportManager',
            'action_manager = gaphor.services.actionmanager:ActionManager',
            'gui_manager = gaphor.services.guimanager:GUIManager',
            'copy = gaphor.services.copyservice:CopyService',
            'xmi_export = gaphor.plugins.xmiexport:XMIExport',
            'diagram_layout = gaphor.plugins.diagramlayout:DiagramLayout',
            'pynsource = gaphor.plugins.pynsource:PyNSource',
            'check_metamodel = gaphor.plugins.checkmetamodel:CheckModelWindow',
            'live_object_browser = gaphor.plugins.liveobjectbrowser:LiveObjectBrowser',
            'alignment = gaphor.plugins.alignment:Alignment',
            'help = gaphor.services.helpservice:HelpService',
        ],
        'gaphor.uicomponents': [
            'mainwindow = gaphor.ui.mainwindow:MainWindow',
            'consolewindow = gaphor.ui.consolewindow:ConsoleWindow',
        ],
        'distutils.commands': [
            'nosetests = nose.commands:nosetests',
        ],
    },

    cmdclass = {
              'build_py': build_py_with_sub_commands,
              'build_uml': build_uml,
              'build_mo': build_mo,
              'build_pot': build_pot,
              'build_doc': build_doc,
              'install_lib': install_lib,
              'run': run,
    },

    setup_requires = ['nose >= 0.9.2'] + platform_setup_requires,

    test_suite = 'nose.collector',

    options = dict(
        py2app = dict(
            argv_emulation=True,
            semi_standalone=True, # Depend on installed Python 2.4 Framework
            includes=['atk', 'pango', 'cairo', 'pangocairo'], #'zope.defferedimport', 'zope.component', 'zope.deprecation', 'zope.interface', 'zope.event', 'zope.testing', 'zope.proxy'],
            packages=['gaphor', 'zope'],
            plist=dict(
                CFBundleGetInfoString='Gaphor',
                CFBundleIdentifier='com.devjavu.gaphor'
                )
        ),
        build_pot = dict(
            all_linguas = ','.join(LINGUAS),
        ),
        build_mo = dict(
            all_linguas = ','.join(LINGUAS),
        ),

    ),

    **platform_setup

)
 
# vim:sw=4:et:ai
