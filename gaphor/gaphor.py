#!/usr/bin/env python
# vim:sw=4
"""
This is the main package for Gaphor, a Python based UML editor.

An extra function is installed in the builtin namespace: gaphorResource().
This function can be used to locate application wide resources, such as
object factories.
"""

from misc.singleton import Singleton
import config
import types

class GaphorError(Exception):
    """
    Gaphor specific exception class
    """
    def __init__(self, args=None):
            self.args = args



class Gaphor(Singleton):
    """
    Gaphor main app. This is a Singleton object that is used as a access point
    to unique resources within Gaphor. The method main() is called once to
    start an interactive instance of Gaphor. If an application wants to use
    Gaphor's functionallity, but not the GUI, that application should not call
    main().

    Resources can be accessed through the get() method. Resources can be
    Python classes or strings. In case of classes, get() will try to find an
    existing class, if none is found, it will create one. No parameters will
    be passed to that class.

    In case of a string resource, a lookup will be done in the GConf
    configuration tree. This is currently not implemented though...
    """

    NAME='gaphor'
    VERSION=config.VERSION
    TITLE='Gaphor v' + VERSION

    __resources = { }

    def init(self, install=1):
	self.__main_window = None
	if install:
	    self.install_gettext()

    def install_gettext(self):
	import gettext
	gettext.install(config.GETTEXT_PACKAGE, unicode=1)

    def main(self):
	from gtk import main as _main
	from gnome import program_init
	from ui import MainWindow
	program_init(Gaphor.NAME, Gaphor.VERSION)
	# should we set a default icon here or something?
	self.__main_window = MainWindow(Gaphor.NAME, Gaphor.TITLE)
	_main()

    def get_main_window(self):
	"""Return the main window, if any."""
        return self.__main_window

    def getResource(resource):
	"""
	*Static method*
	Locate a resource. Resource should be the class of the resource to
	look for or a string. In case of a string the resource will be looked
	up in the GConf configuration.

	example: Get the element factory:
		elemfact = Gaphor.get(gaphor.UML.ElementFactory)

	or (with Gaphor installed in the builtin namespace):
		elemfact = gaphorResource(gaphor.UML.ElementFactory)
	"""
	if isinstance (resource, types.StringType):
	    assert 0, 'Gaphor::get() No string resources are implemented'
	else:
	    hash = Gaphor.__resources
	    if hash.has_key(resource):
		return hash[resource]
	    try:
		r = resource()
		hash[resource] = r
		return r
	    except Exception, e:
		raise GaphorError, 'Could not create resource %s (%s)' % (str(resource), str(e))

    getResource = staticmethod(getResource)


import __builtin__
__builtin__.__dict__['GaphorError'] = GaphorError
__builtin__.__dict__['gaphorResource'] = Gaphor.getResource

