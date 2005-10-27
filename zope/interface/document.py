##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Pretty-Print an Interface object as structured text (Yum)

This module provides a function, asStructuredText, for rendering an
interface as structured text.

$Id$
"""
from string import maketrans
import zope.interface

def asStructuredText(I, munge=0):
    """ Output structured text format.  Note, this will wack any existing
    'structured' format of the text.  """


    r = ["%s\n\n" % I.getName()]
    outp = r.append
    level = 1

    if I.getDoc():
        outp(_justify_and_indent(_trim_doc_string(I.getDoc()), level)+ "\n\n")

    bases = [base
             for base in I.__bases__
             if base is not zope.interface.Interface
             ]
    if bases:
        outp((" " * level) + "This interface extends:\n\n")
        level = level + 1
        for b in bases:
            item = "o %s" % b.getName()
            outp(_justify_and_indent(_trim_doc_string(item), level, munge)
                 + "\n\n")

        level = level - 1

    outp(_justify_and_indent("Attributes:", level, munge)+'\n\n')
    level = level + 1

    namesAndDescriptions = I.namesAndDescriptions()
    namesAndDescriptions.sort()

    for name, desc in namesAndDescriptions:
        if not hasattr(desc, 'getSignatureString'):   # ugh...
            item = "%s -- %s" % (desc.getName(),
                                 desc.getDoc() or 'no documentation')
            outp(_justify_and_indent(_trim_doc_string(item), level, munge)
                 + "\n\n")
    level = level - 1

    outp(_justify_and_indent("Methods:", level, munge)+'\n\n')
    level = level + 1
    for name, desc in namesAndDescriptions:
        if hasattr(desc, 'getSignatureString'):   # ugh...
            item = "%s%s -- %s" % (desc.getName(),
                                   desc.getSignatureString(),
                                   desc.getDoc() or 'no documentation')
            outp(_justify_and_indent(_trim_doc_string(item), level, munge)
                 + "\n\n")

    return "".join(r)

def _trim_doc_string(text):
    """
    Trims a doc string to make it format
    correctly with structured text.
    """
    text = text.strip().replace('\r\n', '\n')
    lines = text.split('\n')
    nlines = [lines[0]]
    if len(lines) > 1:
        min_indent=None
        for line in lines[1:]:
            indent=len(line) - len(line.lstrip())
            if indent < min_indent or min_indent is None:
                min_indent=indent
        for line in lines[1:]:
            nlines.append(line[min_indent:])
    return '\n'.join(nlines)


_trans = maketrans("\r\n", "  ")
def _justify_and_indent(text, level, munge=0, width=72):
    """ indent and justify text, rejustify (munge) if specified """

    lines = []

    if munge:
        line = " " * level
        text = text.translate(text, _trans).strip().split()

        for word in text:
            line = ' '.join([line, word])
            if len(line) > width:
                lines.append(line)
                line = " " * level
        else:
            lines.append(line)

        return "\n".join(lines)

    else:
        text = text.replace("\r\n", "\n").split("\n")

        for line in text:
            lines.append((" " * level) + line)

        return '\n'.join(lines)
