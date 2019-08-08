"""
This file contains code for loading up an override file.  The override file
provides implementations of functions where the code generator could not
do its job correctly.

This is a simple rip-off of the override script used in PyGTK.
"""


class Overrides:
    def __init__(self, filename=None):
        self.overrides = {}
        if filename:
            self.read_overrides(filename)

    def read_overrides(self, filename):
        """Read a file and return a dictionary of overriden properties
        and their implementation.

        An override file ahs the form:
        override <property>
        <implementation>
        %%
        """
        fp = open(filename, "r")
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
                func = words[1]
                deps = ()
                if len(words) > 3 and words[2] == "derives":
                    deps = tuple(words[3:])
                self.overrides[func] = (deps, "".join(rest), f"{line_number:d}: {line}")
            elif words[0] == "comment":
                pass  # ignore comments
            else:
                print(f"Unknown word: '{words[0]}', line {line_number:d}")
                raise SystemExit

    def has_override(self, key):
        return bool(self.overrides.get(key))

    def get_override(self, key):
        """Write override data for 'key' to a file refered to by 'fp'."""
        deps, data, line = self.overrides.get(key, ((), None, None))
        if not data:
            return None

        return f"# {line}{data}"

    def get_type(self, key):
        return "Any"

    def derives(self, key):
        return self.overrides.get(key, ((), None))[0]
