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
import os.path

class install(_install):

    def initialize_options(self):
        _install.initialize_options(self)
        self.install_locales = None

    def finalize_options(self):
        _install.finalize_options(self)
        if not self.install_locales:
            self.install_locales = os.path.join(self.install_base, 'share', 'locale')

install.sub_commands.append(('install_mo', None))

class install_mo(Command):

    description = 'Install .mo files'

    user_options = [('install-dir=', None,
                     'Directory to install locales into (default: <prefix>/share/locale/<lang>/LC_MESSAGES'),
    ]

    def initialize_options(self):
        self.install_dir = None
        self.build_dir = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_locales', 'build_dir'))
        self.set_undefined_options('install',
                                   ('install_locales', 'install_dir'))

        self.all_linguas = self.distribution.get_all_linguas()
        self.name = self.distribution.get_name()

    def run(self):
        if not self.all_linguas:
            return

        for lingua in self.all_linguas:
            mofile = os.path.join(self.build_dir, lingua + '.mo')
            path = os.path.join(self.install_dir, lingua, 'LC_MESSAGES')
            self.mkpath(path)
            outfile = os.path.join(path, self.name + '.mo')
            self.copy_file(mofile, outfile)

