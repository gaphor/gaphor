##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Component Architecture Interfaces kept for Backward-Compatibility.

$Id$
"""
__docformat__ = "reStructuredText"

from zope.interface import Interface, Attribute


class IBBBComponentArchitecture(Interface):
    """The Component Architecture is defined by six key services,
    all of which are managed by service managers.
    """

    # basic service manager tools

    def getGlobalServices():
        """Get the global service manager."""

    def getGlobalService(name):
        """Get a global service."""

    def getServices(context=None):
        """Get the service manager

        If context is None, an application-defined policy is used to choose
        an appropriate service manager.

        If 'context' is not None, context is adapted to IServiceService, and
        this adapter is returned.
        """

    def getService(name, context=None):
        """Get a named service.

        Returns the service defined by 'name' from the service manager.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager.

        If 'context' is not None, context is adapted to IServiceService, and
        this adapter is returned.
        """

    def getServiceDefinitions(context=None):
        """Get service definitions

        Returns a dictionary of the service definitions from the service
        manager in the format {nameString: serviceInterface}.

        The default behavior of placeful service managers is to include
        service definitions above them, but this can be overridden.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager.

        If 'context' is not None, context is adapted to IServiceService, and
        this adapter is returned.
        """

    # Presentation service

    def getView(object, name, request, providing=Interface, context=None):
        """Get a named view for a given object.

        The request must implement IPresentationRequest: it provides
        the view type and the skin name.  The nearest one to the
        object is found. If a matching view cannot be found, raises
        ComponentLookupError.
        """

    def queryView(object, name, request,
                  default=None, providing=Interface, context=None):
        """Look for a named view for a given object.

        The request must implement IPresentationRequest: it provides
        the view type and the skin name.  The nearest one to the
        object is found.  If a matching view cannot be found, returns
        default.

        If context is not specified, attempts to use object to specify
        a context.
        """

    def getMultiView(objects, request, providing=Interface, name='',
                     context=None):
        """Look for a multi-view for given objects

        The request must implement IPresentationRequest: it provides
        the view type and the skin name.  The nearest one to the
        object is found.  If a matching view cannot be found, raises
        ComponentLookupError.

        If context is not specified, attempts to use the first object
        to specify a context.
        """

    def queryMultiView(objects, request, providing=Interface, name='',
                       default=None, context=None):
        """Look for a multi-view for given objects

        The request must implement IPresentationRequest: it provides
        the view type and the skin name.  The nearest one to the
        object is found.  If a matching view cannot be found, returns
        default.

        If context is not specified, attempts to use the first object
        to specify a context.
        """

    def getViewProviding(object, providing, request, context=None):
        """Look for a view based on the interface it provides.

        A call to this method is equivalent to:

            getView(object, '', request, context, providing)
        """

    def queryViewProviding(object, providing, request,
                           default=None, context=None):
        """Look for a view that provides the specified interface.

        A call to this method is equivalent to:

            queryView(object, '', request, default, context, providing)
        """

    def getDefaultViewName(object, request, context=None):
        """Get the name of the default view for the object and request.

        The request must implement IPresentationRequest, and provides the
        desired view type.  The nearest one to the object is found.
        If a matching default view name cannot be found, raises
        ComponentLookupError.

        If context is not specified, attempts to use
        object to specify a context.
        """

    def queryDefaultViewName(object, request, default=None, context=None):
        """Look for the name of the default view for the object and request.

        The request must implement IPresentationRequest, and provides
        the desired view type.  The nearest one to the object is
        found.  If a matching default view name cannot be found,
        returns the default.

        If context is not specified, attempts to use object to specify
        a context.
        """

    def getResource(name, request, providing=Interface, context=None):
        """Get a named resource for a given request

        The request must implement IPresentationRequest.

        The context provides a place to look for placeful resources.

        A ComponentLookupError will be raised if the component can't
        be found.
        """

    def queryResource(name, request, default=None, providing=Interface,
                      context=None):
        """Get a named resource for a given request

        The request must implement IPresentationRequest.

        The context provides a place to look for placeful resources.

        If the component can't be found, the default is returned.
        """


class IServiceService(Interface):
    """A service to manage Services."""

    def getServiceDefinitions():
        """Retrieve all Service Definitions

        Should return a list of tuples (name, interface)
        """

    def getInterfaceFor(name):
        """Retrieve the service interface for the given name
        """

    def getService(name):
        """Retrieve a service implementation

        Raises ComponentLookupError if the service can't be found.
        """


class IUtilityService(Interface):
    """A service to manage Utilities."""

    def getUtility(interface, name=''):
        """Look up a utility that provides an interface.

        If one is not found, raises ComponentLookupError.
        """

    def queryUtility(interface, name='', default=None):
        """Look up a utility that provides an interface.

        If one is not found, returns default.
        """

    def getUtilitiesFor(interface):
        """Look up the registered utilities that provide an interface.

        Returns an iterable of name-utility pairs.
        """

    def getAllUtilitiesRegisteredFor(interface):
        """Return all registered utilities for an interface

        This includes overwridden utilities.

        An iterable of utility instances is returned.  No names are
        returned.
        """

class IAdapterService(Interface):
    """A service to manage Adapters."""

    def queryAdapter(object, interface, name, default=None):
        """Look for a named adapter to an interface for an object

        If a matching adapter cannot be found, returns the default.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def queryMultiAdapter(objects, interface, name, default=None):
        """Look for a multi-adapter to an interface for an object

        If a matching adapter cannot be found, returns the default.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def subscribers(required, provided):
        """Get subscribers

        Subscribers are returned that provide the provided interface
        and that depend on and are comuted from the sequence of
        required objects.
        """


class IContextDependent(Interface):
    """Components implementing this interface must have a context component.

    Usually the context must be one of the arguments of the
    constructor. Adapters and views are a primary example of context-dependent
    components.
    """

    context = Attribute(
        """The context of the object

        This is the object being adapted, viewed, extended, etc.
        """)


class IPresentation(Interface):
    """Presentation components provide interfaces to external actors

    The are created for requests, which encapsulate external actors,
    connections, etc.
    """

    request = Attribute(
        """The request

        The request is a surrogate for the user. It also provides the
        presentation type and skin. It is of type
        IPresentationRequest.
        """)


class IPresentationRequest(Interface):
    """An IPresentationRequest provides methods for getting view meta data."""


class IResource(IPresentation):
    """Resources provide data to be used for presentation."""


class IResourceFactory(Interface):
    """A factory to create factories using the request."""

    def __call__(request):
        """Create a resource for a request

        The request must be an IPresentationRequest.
        """


class IView(IPresentation, IContextDependent):
    """Views provide a connection between an external actor and an object"""


class IViewFactory(Interface):
    """Objects for creating views"""

    def __call__(context, request):
        """Create an view (IView) object

        The context aregument is the object displayed by the view. The
        request argument is an object, such as a web request, that
        "stands in" for the user.
        """


class IDefaultViewName(Interface):
    """A string that contains the default view name

    A default view name is used to select a view when a user hasn't
    specified one.
    """
