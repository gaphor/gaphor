"""Hook for tinycsss2.

This can be removed once tinycss2 1.1.0 is released or
we upgrade to using PyInstaller 4.0 since this is also included
in the pyinstaller-hooks-contrib package.

"""
from PyInstaller.utils.hooks import collect_data_files


def hook(hook_api):
    hook_api.add_datas(collect_data_files(hook_api.__name__))

