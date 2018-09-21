from setuptools.command.install_lib import install_lib as _install_lib


class install_lib(_install_lib):
    def build(self):
        _install_lib.build(self)
        self.run_command('build_uml')
        self.run_command('build_mo')

# vim:sw=4:et:ai
