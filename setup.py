"""
Setup script for Gaphor.

Run 'python setup.py develop' to set up a development environment, including
dependencies.

Run 'python setup.py run' to start Gaphor directly (without install).
"""

VERSION = '0.10.5'

import sys
sys.path.insert(0, '.')

from ez_setup import use_setuptools

use_setuptools()

from setuptools import setup, find_packages

from utils.command.build_mo import build_mo
from utils.command.build_pot import build_pot
from utils.command.build_uml import build_uml
from utils.command.install_lib import install_lib
from utils.command.run import run

LINGUAS = [ 'ca', 'es', 'nl', 'sv' ]


setup(
    name='gaphor',
    version=VERSION,
    url='http://gaphor.devjavu.com',
    author='Arjan J. Molenaar',
    author_email='arjanmol@users.sourceforge.net',
    license='GNU General Public License',
    description='Gaphor is a UML modeling tool',
    long_description="Gaphor is a UML modeling tool written in Python. "
                     "It uses the GTK+ environment for user interaction.",
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
        'decorator >= 2.0.1',
        'gaphas >= 0.1.5',
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
            'properties = gaphor.services.properties:Properties',
            'undo_manager = gaphor.services.undomanager:UndoManager',
            'plugin_manager = gaphor.services.pluginmanager:PluginManager',
            'action_manager = gaphor.services.actionmanager:ActionManager',
            'gui_manager = gaphor.services.guimanager:GUIManager',
            'adapter_loader = gaphor.services.adapterloader:AdapterLoader',
            'element_factory = gaphor.UML.elementfactory:ElementFactory',
        ],
        'gaphor.adapters': [
            'connectors = gaphor.adapters.connectors',
            'editors = gaphor.adapters.editors',
        ],
    },

    cmdclass = {
              'build_uml': build_uml,
              'build_mo': build_mo,
              'build_pot': build_pot,
	      'install_lib': install_lib,
              'run': run,
    },
    options = dict(
        py2app = dict(
            includes=['atk', 'pango', 'cairo', 'pangocairo'],
#             CFBundleDisplayName='Gaphor',
#             CFBundleIdentifier='net.sourceforge.gaphor'
        ),
        build_pot = dict(
            all_linguas = ','.join(LINGUAS),
        ),
        build_mo = dict(
            all_linguas = ','.join(LINGUAS),
        ),
        install_mo = dict(
            all_linguas = ','.join(LINGUAS),
        ),
    )
)
      
