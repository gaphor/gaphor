"""This hook can be removed onces integrated in PyInstaller"""

from PyInstaller.utils.hooks import collect_data_files


def hook(hook_api):
    hook_api.add_datas(collect_data_files(hook_api.__name__))

