#!/usr/bin/env python
#
# setup.py for Gaphor
#
# vim:sw=4:et
"""Gaphor
"""

MAJOR_VERSION = 0
MINOR_VERSION = 6
MICRO_VERSION = 0

VERSION = '%d.%d.%d' % ( MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION )

GCONF_DOMAIN='/apps/gaphor/' # don't forget trailing slash

import sys, os
from glob import glob
from commands import getoutput, getstatus, getstatusoutput
from distutils.core import setup, Command
from distutils.command.build_py import build_py
from distutils.command.install_lib import install_lib
from distutils.dep_util import newer
from utils.build_mo import build, build_mo
from utils.build_pot import build_pot
from utils.install_mo import install, install_mo
from utils.dist_mo import Distribution

str_version = sys.version[:3]
version = map(int, str_version.split('.'))
if version < [2, 2]:
    raise SystemExit, \
        "Python 2.2 or higher is required, %s found" % str_version


class config_Gaphor(Command):
    description="Configure Gaphor"

    user_options = [
        #('pkg-config=', None, 'Path to pkg-config'),
    ]

    #pkg_config_checked=False
    config_failed=[]

    def initialize_options(self):
        #self.pkg_config = 'pkg-config'
        pass

    def finalize_options(self):
        # Check for existence of pkg-config
        #status, output = getstatusoutput('%s --version' % self.pkg_config)
        #if status != 0:
        #    print 'pkg-config not found.'
        #    raise SystemExit
        #print 'Found pkg-config version %s' % output
        pass

    def run(self):
        import pygtk
        pygtk.require('2.0')

        #self.pkg_config_check('gobject-2.0', '2.0.0')
        #self.pkg_config_check('gtk+-2.0', '2.0.0')
        #self.pkg_config_check('pygtk-2.0', '1.99.15')
        #self.pkg_config_check('gconf-2.0', '2.0.0')
        #self.pkg_config_check('libbonobo-2.0', '2.0.0')
        #self.pkg_config_check('libbonoboui-2.0', '2.0.0')
        #self.pkg_config_check('diacanvas2', '0.9.1')

        self.module_check('xml.parsers.expat')
        #self.module_check('gobject', 'glib_version', (2, 0))
        self.module_check('gtk', ('gtk_version', (2, 0)),
                                 ('pygtk_version', (2, 0)))
        self.module_check('gnome')
        self.module_check('gnome.canvas')
        #self.module_check('gconf')
        self.module_check('diacanvas', ('diacanvas_version', (0, 13, 0)))

        print ''
        if self.config_failed:
            print 'Config failed.'
            print 'The following modules can not be found or are to old:'
            print ' ', str(self.config_failed)[1:-1]
            print ''
            raise SystemExit
        else:
            print 'Config succeeded.'

    def pkg_config_check(self, package, version):
        """Check for availability of a package via pkg-config."""
        retval = os.system('%s --exists %s' % (self.pkg_config, package))
        if retval:
            print '!!! Required package %s not found.' % package
            self.config_failed.append(package)
            return
        pkg_version_str = getoutput('%s --modversion %s' % (self.pkg_config, package))
        pkg_version = map(int, pkg_version_str.split('.'))
        req_version = map(int, version.split('.'))
        if pkg_version >= req_version:
            print "Found '%s', version %s." % (package, pkg_version_str)
        else:
            print "!!! Package '%s' has version %s, should have at least version %s." % ( package, pkg_version_str, version )
            self.config_failed.append(package)

    def module_check(self, module, *version_checks):
        """Check for the availability of a module.

        version_checks is a set of ket/version pairs that should be true.
        """
        import string
        try:
            mod = __import__(module)
        except ImportError:
            print "!!! Required module '%s' not found." % module
            self.config_failed.append(module)
        else:
            print "Module '%s' found." % module
            for key, ver in version_checks:
                s_ver = string.join(map(str, ver), '.')
                print "  Checking key '%s.%s' >= %s..." % (module, key, s_ver),
                try:
                    modver = getattr(mod, key)
                except:
                    print "Not found." % key
                    self.config_failed.append(module)
                else:
                    s_modver = string.join(map(str, modver), '.')
                    if modver >= ver:
                        print "Okay (%s)." % s_modver
                    else:
                        print "Failed (%s)" % s_modver
                        self.config_failed.append(module)


class build_Gaphor(build):

    def run(self):
        self.run_command('config')
        build.run(self)


class version_py:

    def generate_version(self, dir, data_dir):
        """Create a file gaphor/version.py which contains the current version.
        """
        outfile = os.path.join(dir, 'gaphor', 'version.py')
        print 'generating %s' % outfile, dir, data_dir
        self.mkpath(os.path.dirname(outfile))
        f = open(outfile, 'w')
        f.write('import os\n')
        f.write('VERSION=\'%s\'\n' % VERSION)
        # expand backspaces
        f.write('DATA_DIR=\'%s\'\n' % data_dir.replace('\\', '\\\\'))
        if os.name == 'nt':
            home = 'USERPROFILE'
        else:
            home = 'USER'
        f.write('DATA_DIR=\'%s\'\n' % data_dir)
        f.write('import os\n')
        f.write('USER_DATA_DIR=os.path.join(os.getenv(\'%s\'), \'.gaphor\')\n' % home)
        f.write('del os\n')
        f.close()
        self.byte_compile([outfile])


class build_py_Gaphor(build_py, version_py):

    description = "build_py and generate gaphor/UML/uml2.py."

    def run(self):
        build_py.run(self)
        sys.path.insert(0, self.build_lib)
        # All data is stored in the local data directory
        data_dir = os.path.join(os.getcwd(), 'data')
        #data_dir = "os.path.join(os.getcwd(), 'data')"
        self.generate_version(self.build_lib, data_dir)
        self.generate_uml2()

    def generate_uml2(self):
        """Generate gaphor/UML/uml2.py in the build directory."""
        import utils.genUML2
        gen = os.path.join('utils', 'genUML2.py')
        overrides = os.path.join('gaphor', 'UML', 'uml2.override')
        model = os.path.join('gaphor', 'UML', 'uml2.gaphor')
        py_model = os.path.join('gaphor', 'UML', 'uml2.py')
        outfile = os.path.join(self.build_lib, py_model)
        self.mkpath(os.path.dirname(outfile))
        if self.force or newer(model, outfile) \
                      or newer(overrides, outfile) \
                      or newer(gen, outfile):
            print 'generating %s from %s...' % (py_model, model)
            print '  (warnings can be ignored)'
            utils.genUML2.generate(model, outfile, overrides)
        else:
            print 'not generating %s (up-to-date)' % py_model
        self.byte_compile([outfile])


class install_lib_Gaphor(install_lib, version_py):

    def initialize_options(self):
        install_lib.initialize_options(self)
        self.install_data= None

    def finalize_options(self):
        install_lib.finalize_options(self)
        self.set_undefined_options('install_data',
                                   ('install_dir', 'install_data'))

    def run(self):
        # Install a new version.py with install_data as data_dir:
        self.generate_version(self.install_dir, self.install_data)
        install_lib.run(self)


class install_schemas(Command):
    """Do something like this:

        GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source` \
            gconftool --makefile-install-rule data/gaphor.schemas

    in a pythonic way.
    """

    description = "Install a configuration (using GConf)."

    user_options = [
        ('install-data=', None, 'installation directory for data files'),
        ('gconftool', None, 'The gconftool to use for installation'),
        ('gconf-config-source', None, 'Overrule the GConf config source'),
        ('force', 'f', 'force installation (overwrite existing keys)')
    ]

    boolean_options = ['force']

    def initialize_options(self):
        self.install_data = None
        self.gconftool = 'gconftool-2'
        self.gconf_config_source = ''
        self.force = None
        self.schemas_file = 'data/gaphor.schemas'

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('force', 'force'),
                                   ('install_data', 'install_data'))

    def run(self):
        getstatus('GCONF_CONFIG_SOURCE="%s" %s --makefile-install-rule %s' % (self.gconf_config_source, self.gconftool, self.schemas_file))

        self._set_value('/schemas/apps/gaphor/data_dir', self.install_data, 'string')

    def _set_value(self, key, value, type):
        print "setting gconf value '%s' to '%s'" % (key, value)
        #apply(getattr(self.gconf_client, 'set_' + type),
        #      (GCONF_DOMAIN + key, value))
        getstatus('%s --type=%s --set %s %s' % (self.gconftool, type, key, value))

#install.sub_commands.append(('install_schemas', None))


class run_Gaphor(Command):

    description = 'Launch Gaphor from the local directory'

    user_options = [
        ('build-dir=', None, ''),
        ('command=', 'c', 'execute command'),
        ('file=', 'f', 'execute file'),
        ('testfile=', 't', 'execute unittest file'),
    ]

    def initialize_options(self):
        self.build_lib = None
        self.command = None
        self.file = None
        self.testfile = None
        self.verbosity = 2

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'))

    def run(self):
        print 'Starting gaphor...'
        self.run_command('build')

        import os.path
        import gaphor
        #os.environ['GAPHOR_DATADIR'] = os.path.abspath('data')
        if self.command:
            print 'Executing command: %s...' % self.command
            exec self.command
        elif self.testfile:
            # Running a unit test is done by opening the unit test file
            # as a module and running the tests within that module.
            print 'Running test cases in unittest file: %s...' % self.testfile
            import imp, unittest
            fp = open(self.testfile)
            test_module = imp.load_source('gaphor_test', self.testfile, fp)
            test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
            test_runner = unittest.TextTestRunner(verbosity=self.verbosity)
            result = test_runner.run(test_suite)
            sys.exit(not result.wasSuccessful())
        elif self.file:
            print 'Executing file: %s...' % self.file
            dir, f = os.path.split(self.file)
            print 'Extending PYTHONPATH with %s' % dir
            sys.path.append(dir)
            execfile(self.file, {})
        else:
            print 'Launching Gaphor...'
            gaphor.main()

#try:
#    from dsextras import TemplateExtension, BuildExt, GLOBAL_INC
#except ImportError:
#    import pygtk
#    pygtk.require('2.0')
#    from gtk.dsextras import TemplateExtension, BuildExt, GLOBAL_INC

#pygtkincludedir = getoutput('pkg-config --variable pygtkincludedir pygtk-2.0')
#codegendir = getoutput('pkg-config --variable codegendir pygtk-2.0')
#defsdir = getoutput('pkg-config --variable defsdir pygtk-2.0')

#sys.path.append(codegendir)

#GLOBAL_INC.append(pygtkincludedir)
#GLOBAL_INC.append('.')
#GTKDEFS = [os.path.join(defsdir, 'gtk-types.defs')]

#ext_modules = []
#gtkwrapbox = TemplateExtension(name='wrapbox',
#                               pkc_name='gtk+-2.0',
#                               pkc_version='2.0.0',
#                               output='gaphor.misc.wrapbox',
#                               defs='src/wrapbox.defs',
#                               sources=['src/gtkwrapbox.c',
#                                        'src/gtkhwrapbox.c',
#                                        'src/gtkvwrapbox.c',
#                                        'src/wrapbox.c',
#                                        'src/wrapboxmodule.c'],
#                               register=GTKDEFS,
#                               override='src/wrapbox.override')

#if gtkwrapbox.can_build():
#    ext_modules.append(gtkwrapbox)
#else:
#    pass

def plugin_data(name):
    return 'plugins/%s' % name, glob('data/plugins/%s/*.*' % name)

setup(name='gaphor',
      version=VERSION,
      description="Gaphor is a UML modeling tool",
      url='http://gaphor.sourceforge.net',
      author='Arjan J. Molenaar',
      author_email='arjanmol@users.sourceforge.net',
      license="GNU General Public License (GPL, see COPYING)",
      long_description="Gaphor is a UML modeling tool written in Python. "
      "It uses the GNOME2 environment for user interaction.",
      platforms=['GNOME2'],
      all_linguas=['nl'],
      packages=['gaphor',
                'gaphor.UML',
                'gaphor.diagram',
                'gaphor.ui',
                'gaphor.misc'
      ],
#      ext_modules=ext_modules,
      # data files are relative to <prefix>/share/gaphor (see setup.cfg)
      data_files=[('', ['data/icons.xml']),
                  ('pixmaps', glob('data/pixmaps/*.png')),
                  plugin_data('plugineditor'),
                  plugin_data('checkmetamodel'),
                  plugin_data('diagramlayout'),
                  plugin_data('liveobjectbrowser'),
                  plugin_data('pynsource')
      ],
      scripts=['bin/gaphor'],

      distclass=Distribution,
      cmdclass={'config': config_Gaphor,
                'build_py': build_py_Gaphor,
                #'install_schemas': install_schemas,
                'build': build_Gaphor,
#                'build_ext': BuildExt,
                'build_mo': build_mo,
                'build_pot': build_pot,
                'install': install,
                'install_lib': install_lib_Gaphor,
                'install_mo': install_mo,
                'run': run_Gaphor
      }
)

