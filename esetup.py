
import sys
sys.path.insert(0, '.')

from ez_setup import use_setuptools

use_setuptools()

from setuptools import setup, find_packages

from utils.command.build_mo import build_mo
from utils.command.build_pot import build_pot
from utils.command.install_mo import install_mo
from utils.command.build_uml import build_uml
from utils.command.build_version import build_version
from utils.command.install_version import install_version
from utils.command.run import run

LINGUAS = [ 'ca', 'es', 'nl', 'sv' ]

from glob import glob
def plugin_data(name):
    return 'plugins/%s' % name, glob('data/plugins/%s/*.*' % name)

setup(
    name='gaphor',
    version='0.9.2',
    url='http://gaphor.sourceforge.net',
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

    keywords = 'model modeling modelling uml diagram python',

    packages = find_packages(exclude=['ez_setup', 'gaphas', 'utils*', 'zope_old*']),

    package_data = {
        'data': [ 'icons.xml' ],
        'data/pixmaps': [ '*.png' ],
        'data/plugins': [ '*/plugin.xml', '*/*.txt', '*/*.py' ]
    },
    data_files=[('', ['data/icons.xml']),
                ('pixmaps', glob('data/pixmaps/*.png')),
                plugin_data('plugineditor'),
                plugin_data('alignment'),
                plugin_data('checkmetamodel'),
                plugin_data('diagramlayout'),
                plugin_data('liveobjectbrowser'),
                plugin_data('pngexport'),
                plugin_data('pynsource'),
                plugin_data('svgexport'),
                plugin_data('pdfexport'),
                plugin_data('xmiexport')
    ],

    install_requires = [
        # 'PyGTK >= 2.8.0', - Exclude, since it will not build anyway
        'gaphas >= 0.1.0',
        'zope.component >= 3.3.0', # - won't compile on windows.
    ],

    zip_safe = False,

    #test_suite = 'nose.collector',

    entry_points = {
#        'distutils.commands': [
#            'build_uml = utils.command.build_uml:build_uml',
#            'build_pot = utils.command.build_pot:build_pot',
#            'build_mo = utils.command.build_mo:build_mo',
#            'install_mo = utils.command.install_mo:install_mo',
#            'build_version = utils.command.build_version:build_version',
#            'install_version = utils.command.install_version:install_version',
#            'run  = utils.command.run :run ',
#        ],
        'console_scripts': [
            'gaphor = gaphor:main',
        ],
    },

    cmdclass = {
              'build_uml': build_uml,
              'build_version': build_version,
              'install_version': install_version,
              'build_mo': build_mo,
              'build_pot': build_pot,
              'install_mo': install_mo,
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
      
