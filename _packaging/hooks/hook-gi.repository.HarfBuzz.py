"""Import hook for PyGObject https://wiki.gnome.org/PyGObject."""

from PyInstaller.compat import is_win
from PyInstaller.utils.hooks.gi import get_gi_typelibs


def hook(hook_api):
    binaries, datas, hidden_imports = get_gi_typelibs("HarfBuzz", "0.0")
    # Fix a freetype2 typelib not found error in Windows
    if is_win:
        ft_binaries, ft_datas, ft_hidden_imports = get_gi_typelibs("freetype2", "2.0")
        binaries.extend(ft_binaries)
        datas.extend(ft_datas)
        hidden_imports.extend(ft_hidden_imports)
    hook_api.add_datas(datas)
    hook_api.add_binaries(binaries)
    for hidden_import in hidden_imports:
        # Prevent hidden import not found error
        if hidden_import != "gi.repository.freetype2":
            hook_api.add_imports(hidden_import)
