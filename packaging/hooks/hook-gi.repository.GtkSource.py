"""Import hook for PyGObject https://wiki.gnome.org/PyGObject.

This hook file can be removed once PyInstaller with
https://github.com/pyinstaller/pyinstaller/pull/6267 is merged.
"""

from PyInstaller.utils.hooks.gi import (collect_glib_share_files, get_gi_typelibs)
from PyInstaller.utils.hooks import (get_hook_config, logger)


def hook(hook_api):
    module_versions = get_hook_config(hook_api, 'gi', 'module-versions')
    if module_versions:
        version = module_versions.get('GtkSource', '3.0')
    else:
        version = '3.0'
    logger.info(f'GtkSource version is {version}')

    binaries, datas, hiddenimports = get_gi_typelibs('GtkSource', version)

    datas += collect_glib_share_files(f'gtksourceview-{version}')
    hook_api.add_datas(datas)
    hook_api.add_binaries(binaries)
    hook_api.add_imports(*hiddenimports)
