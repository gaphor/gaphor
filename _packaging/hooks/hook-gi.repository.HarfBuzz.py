"""Import hook for PyGObject https://wiki.gnome.org/PyGObject."""

from PyInstaller.utils.hooks.gi import get_gi_typelibs


def hook(hook_api):
    harf_binaries, harf_datas, harf_hiddenimports = get_gi_typelibs("HarfBuzz", "0.0")
    freetype_binaries, freetype_datas, freetype_hiddenimports = get_gi_typelibs(
        "freetype2", "2.0"
    )
    hook_api.add_datas(harf_datas + freetype_datas)
    hook_api.add_binaries(harf_binaries + freetype_binaries)
    hook_api.add_imports(*harf_hiddenimports + freetype_hiddenimports)
