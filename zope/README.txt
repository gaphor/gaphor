=====================
Zope Project Packages
=====================

The ``zope`` package is a pure namespace package holding packages
developed as part of the Zope 3 project.

Generally, the immediate subpackages of the ``zope`` package should be
useful and usable outside of the Zope application server.  Subpackages
of the ``zope`` package should have minimal interdependencies,
although most depend on ``zope.interface``.

The one subpackage that's not usable outside the application server is
the ``app`` subpackage, ``zope.app``, which *is* the application
server.  Sub-packages of ``zope.app`` are not usable outside of the
application server.  If there's something in ``zope.app`` you want to
use elsewhere, let us know and we can talk about abstracting some of
it up out of ``zope.app``.
