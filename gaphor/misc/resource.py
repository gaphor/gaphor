#!/usr/bin/env python
# vim:sw=4
"""
"""

import types

_no_default = object()

class Resource(object):
    """The Resource class holds a collection of application wide resources.
    """
    _resources = {}

    def __init__(self, initial_resources={}):
	self._resources.update(initial_resources)

    def __call__(self, r, default=_no_default):
	return self.resource(r, default)

    def resource(self, r, default=_no_default):
	"""Locate a resource.

	Resource should be the class of the resource to look for or a string. In
	case of a string the resource will be looked up in the GConf configuration.

	example: Get the element factory:
		factory = gaphor.resource(gaphor.UML.ElementFactory)

	Also builtin resources are 'Name', 'Version' and 'DataDir'. In case main()
	is run, 'MainWindow' points to the main window of the application.

	If a class name is given as a resource, the resource is created if not
	yet available. If the resource is a string, KeyError is issued if the
	resource could not be localed, unless a default value was set.
	"""
	_resources = self._resources

	# Return the existing resource
	try:
	    return _resources[r]
	except KeyError:
	    pass

	# Handle string-like resources 
	if isinstance (r, types.StringType):
	    # TODO: It might be a GConf resource string

	    if default is not _no_default:
		return default
	    raise KeyError, 'No resource with name "%s"' % r
	# Instantiate the resource and return it
	i = r()
	_resources[r] = i
	_resources[r.__name__] = i
	return i

