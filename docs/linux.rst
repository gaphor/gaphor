Gaphor on Linux
===============

Examples of Gaphor and Gaphas RPM spec files can be found in `PLD Linux <http://www.pld-linux.org/ PLD Linux>`_
`repository <http://cvs.pld-linux.org/cgi-bin/cvsweb/SPECS/>`_:

 * http://cvs.pld-linux.org/cgi-bin/cvsweb/SPECS/python-gaphas.spec
 * http://cvs.pld-linux.org/cgi-bin/cvsweb/SPECS/gaphor.spec

Please, do not hesitate to contact us if you need help to create a Linux package
for Gaphor or Gaphas.

Dependencies
------------

Gaphor depends on Zope libraries:
 * component
 * interface
and:
 * gaphas (of course :)
 * pygtk

Above Zope modules require
 * deferredimport
 * deprecation
 * event
 * proxy
 * testing
