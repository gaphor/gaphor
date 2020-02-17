from PyInstaller.utils.hooks import copy_metadata, collect_submodules
    
block_cipher = None

a = Analysis(['gaphor-script.py'],
             pathex=['../'],
             binaries=[],
             datas=[
	     	    ('../gaphor/ui/layout.xml', 'gaphor/ui'),
		       ('../gaphor/ui/layout.css', 'gaphor/ui'),
		       ('../gaphor/ui/*.glade', 'gaphor/ui'),
		       ('../gaphor/services/helpservice/*.png', 'gaphor/services/helpservice'),
		       ('../gaphor/services/helpservice/*.glade', 'gaphor/services/helpservice'),
		       ('../gaphor/ui/icons/*.svg', 'gaphor/ui/icons'),
		       ('../LICENSE.txt', 'gaphor'),
		       ('../gaphor/locale/*', 'gaphor/locale')
		     ]+copy_metadata('gaphor'),
             hiddenimports=collect_submodules('packaging') + collect_submodules('pkg_resources') + collect_submodules('gaphas') + collect_submodules('importlib_metadata'),
             hookspath=[],
             runtime_hooks=[],
             excludes=['lib2to3', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          options=[],
          exclude_binaries=True,
          name='gaphor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          icon='misc/gaphor.ico',
          version='file_version_info.txt',
          console=False)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='gaphor')
