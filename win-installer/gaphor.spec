# -*- mode: python ; coding: utf-8 -*-
def Datafiles(*filenames, **kw):
    import os
    
    def datafile(path, strip_path=True):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)
        return name, path, 'DATA'

    strip_path = kw.get('strip_path', True)
    return TOC(
        datafile(filename, strip_path=strip_path)
        for filename in filenames
        if os.path.isfile(filename))

xmlfiles = Datafiles('gaphor/ui/layout.xml')
cssfiles = Datafiles('gaphor/ui/layout.css')
pngfiles = Datafiles('gaphor/ui/pixmaps/*.png')

block_cipher = None


a = Analysis(['gaphor.py'],
             pathex=['C:/tools/msys64/home/DYEAW/gaphor'],
             binaries=[],
             datas=[],
             hiddenimports=['_struct'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=True)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [('v', None, 'OPTION')],
          exclude_binaries=True,
          name='gaphor',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               xmlfiles,
               pngfiles,
               cssfiles,
               strip=False,
               upx=False,
               name='gaphor')
