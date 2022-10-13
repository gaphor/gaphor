# A workaround for Pydot, to make sure it works
# in a PyInstaller setup.
# The application path is updated and the
# environment variable VGBINDIR is set to make sure plugins are found

import logging
import os
import subprocess
import sys

import pydot

log = logging.getLogger(__name__)


def graphviz_path():
    if hasattr(sys, "_MEIPASS"):
        # Use packaged `dot` (pyinstaller)
        if sys.platform == "win32":
            return os.path.join(sys._MEIPASS, "graphviz")
        else:
            return sys._MEIPASS  # type: ignore[attr-defined]
    return None


def graphviz_plugin_path():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "graphviz")  # type: ignore[attr-defined]
    return None


def have_graphviz(program):
    path = graphviz_path()
    if path:
        program = os.path.join(path, program + pydot.get_executable_extension())
    return os.system(f'"{program}" -V') == 0


def call_graphviz(program, arguments, working_dir, **kwargs):
    # explicitly inherit `$PATH`, on Windows too,
    # with `shell=False`

    path = graphviz_path()
    if path:
        program = os.path.join(path, program + pydot.get_executable_extension())

    if arguments is None:
        arguments = []

    plugin_path = graphviz_plugin_path()
    env = {
        "PATH": os.environ.get("PATH", ""),
        "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        **({"VGBINDIR": plugin_path} if plugin_path else {}),
    }

    program_with_args = [program] + arguments

    process = subprocess.Popen(
        program_with_args,
        env=env,
        cwd=working_dir,
        shell=False,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        **kwargs,
    )
    stdout_data, stderr_data = process.communicate()

    return stdout_data, stderr_data, process


pydot.call_graphviz = call_graphviz
