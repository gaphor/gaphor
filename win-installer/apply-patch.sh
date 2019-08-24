patch -u -b ../.venv/lib/python3.7/site-packages/importlib_metadata/__init__.py -i fix-pyinstaller-issue-4258.patch
patch -u -b ../.venv/lib/python3.7/site-packages/PyInstaller/building/build_main.py -i fix-pyinstaller-issue-4263.patch

