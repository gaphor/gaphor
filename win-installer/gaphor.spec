# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata


block_cipher = None

a = Analysis(['gaphor-script.py'],
             pathex=['C:/tools/msys64/home/DYEAW/gaphor'],
             binaries=[],
             datas=[
	     	('../gaphor/ui/layout.xml', 'gaphor/ui'),
		('../gaphor/ui/layout.css', 'gaphor/ui'),
		('../gaphor/ui/pixmaps/*.png', 'gaphor/ui/pixmaps'),
		('../LICENSE.txt', 'gaphor')
		]+copy_metadata('gaphor'),
             hiddenimports=[],
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
          icon='misc/gaphor.ico',
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='gaphor')
