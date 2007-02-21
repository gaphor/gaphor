
import sys
sys.path.insert(0, '.')

from ez_setup import use_setuptools

use_setuptools()

from setuptools import setup, find_packages


setup(
    name='gaphor',
    version='0.9.0',
    url='http://gaphor.sourceforge.net',
    author='Arjan J. Molenaar',
    author_email='arjanmol@users.sourceforge.net',
    license='GNU General Public License',
    description='Gaphor is a UML modeling tool',
    long_description="Gaphor is a UML modeling tool written in Python. "
                     "It uses the GTK+ environment for user interaction.",
    classifiers=[
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

    keywords='',

    packages=find_packages(exclude=['ez_setup', 'utils']),

    install_requires=[
        # 'PyGTK >= 2.8.0', - Exclude, since it will not build anyway
        'gaphas >= 0.1.0',
        'zope.interface >= 3.3.0', # - won't compile on windows.
    ],

    zip_safe=False,

    package_data={
        'data': [ 'icons.xml' ],
        'data/pixmaps': [ '*.png' ],
        'data/plugins': [ '*/plugin.xml', '*/*.txt', '*/*.py' ]
    },

    #test_suite = 'nose.collector',

    entry_points = {
        'distutils.commands': [
            #'build_pot = utils.build_pot:build_pot',
            'build_mo = utils.build_mo:build_mo',
            #'install_mo = utils.install_mo:install_mo',
        ],
        'console_scripts': [
            'gaphor = gaphor:main',
        ],
    }
)
      
