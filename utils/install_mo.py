# vim:sw=4:et
"""install_mo

Install gettext packages.

Files will be installed as:
    <install_locales>/<lang>/LC_MESSAGES/<package>.mo
where install_locales should default to:
    <install_base>/share/locale
"""

from distutils.core import Command
from distutils.command.install import install as _install
from distutils.util import change_root
import os.path

class install(_install):

    def initialize_options(self):
        _install.initialize_options(self)
        self.install_locales = None

    def finalize_options(self):
        _install.finalize_options(self)
        #if not self.install_locales:
        self.install_locales = os.path.join(self.install_base, 'share', 'locale')

install.sub_commands.append(('install_mo', None))

class install_mo(Command):

    description = 'Install .mo files'

    user_options = [('install-dir=', None,
                     'Directory to install locales into (default: <prefix>/share/locale/<lang>/LC_MESSAGES'),
                    ('all-linguas', None, ''),
    ]

    def initialize_options(self):
        self.install_dir = None
        self.build_dir = None
        self.root = None
        self.all_linguas = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_locales', 'build_dir'))
        self.set_undefined_options('install',
                                   ('install_locales', 'install_dir'),
                                   ('root', 'root'))

        self.name = self.distribution.get_name()
        self.all_linguas = self.all_linguas.split(',')

        if self.root:
            self.install_dir = change_root(self.root, self.install_dir)

    def run(self):
        if not self.all_linguas:
            return

        for lingua in self.all_linguas:
            mofile = os.path.join(self.build_dir, '%s.mo' % lingua)
            path = os.path.join(self.install_dir, lingua, 'LC_MESSAGES')
            self.mkpath(path)
            outfile = os.path.join(path, '%s.mo' % self.name)
            self.copy_file(mofile, outfile)

