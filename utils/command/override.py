# vim:sw=4:et
"""
This file contains code for loading up an override file.  The override file
provides implementations of functions where the code generator could not
do its job correctly.

This is a simple rip-off of the override script used in PyGTK.
"""


import sys, string

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
        fp = open(filename, 'r')
        # read all the components of the file ...
        # bufs contains a list of (lines, startline) pairs.
        bufs = []
        startline = 1
        lines = []
        line = fp.readline()
        linenum = 1
        while line:
            if line == '%%\n' or line == '%%':
                if lines:
                    bufs.append((string.join(lines, ''), startline))
                startline = linenum + 1
                lines = []
            else:
                lines.append(line)
            line = fp.readline()
            linenum = linenum + 1
        if lines:
            bufs.append((string.join(lines, ''), startline))

        if not bufs:
            return

        # Parse the parts of the file
        for buffer, startline in bufs:
            pos = string.find(buffer, '\n')
            if pos >= 0:
                line = buffer[:pos]
                rest = buffer[pos+1:]
            else:
                line = buffer ; rest = ''
            words = string.split(line)

            if words[0] == 'override':
                func = words[1]
                self.overrides[func] = rest
            elif words[0] == 'comment':
                pass # ignore comments
            else:
                print "Unknown word: '%s', line %d" (words[0], startline)
                raise SystemExit

    def has_override(self, key):
        return bool(self.overrides.get(key))

    def write_override(self, fp, key):
        """Write override data for 'key' to a file refered to by 'fp'."""
        data = self.overrides.get(key)
        if not data:
            return False

        fp.write(data)
        return True

