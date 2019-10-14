Gaphor on Linux
===============

Examples of Gaphor and Gaphas RPM spec files can be found in `PLD Linux <https://www.pld-linux.org/>`_
`repository <https://github.com/pld-linux/>`_:

 * https://github.com/pld-linux/python-gaphas
 * https://github.com/pld-linux/gaphor

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
