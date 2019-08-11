"""
This file contains code for loading up an override file.  The override file
provides implementations of functions where the code generator could not
do its job correctly.

This is a simple rip-off of the override script used in PyGTK.
"""

import re


OVERRIDE_RE = re.compile(
    r"^override\s+(?P<name>[\w.]+)(?:\((?P<derived>[^)]+)\))?\s*(?::\s*(?P<type_hint>[\w\s\[\],]+))?$"
)


class Overrides:
    def __init__(self, filename=None):
        self.overrides = {}
        if filename:
            with open(filename) as fp:
                self.read_overrides(fp)

    def read_overrides(self, fp):
        """Read a file and return a dictionary of overriden properties
        and their implementation.

        An override file ahs the form:
        override <property>
        <implementation>
        %%
        """
        # read all the components of the file ...
        # bufs contains a list of (lines, line_number) pairs.
        bufs = []
        line_number = 1
        lines = []
        line = fp.readline()
        linenum = 1
        while line:
            if line == "%%\n" or line == "%%":
                if lines:
                    bufs.append((list(lines), line_number))
                line_number = linenum + 1
                lines = []
            else:
                lines.append(line)
            line = fp.readline()
            linenum = linenum + 1
        if lines:
            bufs.append((list(lines), line_number))

        if not bufs:
            return

        # Parse the parts of the file
        for lines, line_number in bufs:
            line = lines[0]
            rest = lines[1:]
            words = line.split()

            # TODO: Create a mech to define dependencies
            if words[0] == "override":
                m = OVERRIDE_RE.match(line.strip())
                func = m.group("name")
                derived = m.group("derived")
                deps = tuple(map(str.strip, derived.split(","))) if derived else ()
                type_hint = m.group("type_hint") or "Any"
                self.overrides[func] = (
                    deps,
                    type_hint,
                    "".join(rest),
                    f"{line_number:d}: {line}",
                )
            elif words[0] == "comment":
                pass  # ignore comments
            else:
                print(f"Unknown word: '{words[0]}', line {line_number:d}")
                raise SystemExit

    def has_override(self, key):
        return bool(self.overrides.get(key))

    def get_override(self, key):
        """Write override data for 'key' to a file refered to by 'fp'."""
        _deps, _type_hint, data, line = self.overrides.get(key, ((), None, None, None))
        if not data:
            return None

        return f"# {line}{data}"

    def get_type(self, key):
        return self.overrides.get(key, (None, "Any"))[1]

    def derives(self, key):
        return self.overrides.get(key, ((),))[0]
