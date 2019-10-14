Writing plugins and services
============================

There is little difference in writing a plugin or a service.

Accessing model related data
----------------------------

The datamodel classes are located in the `gaphor.UML` module. Data objects can
be accessed through the ElementFactory. This is a special class for creating
and managing data objects. Items can be queried using this element factory.
It's registered in the application as `element_factory`. When writing a service
or plugin the element factory can be injected into the service like this::

  class MyThing:


      def do_something(self):
          element_factory = Application.get_service('element_factory')
	        items = element_factory.select()

.. note::

    In the console window services can be retrieved by using the `service()` function. E.g.::

        ef = service('element_factory')

Querying the data model
-----------------------

Two methods are used for querying:

* `select(query=None)` -> returns an iterator
* `lselect(query=None)` -> returns a list

query is a lambda function with the element as parameter. E.g.::

  element_factory.select(lambda e: e.isKindOf(UML.Class))


will fetch all Class instances from the element factory.

Traversing data instances
-------------------------

Once some classes are obtained It's common to traverse through a few related
objects in order to obtain the required information. For example: to iterate
through all parameters related to class' operations, one can write::

  for o in classes.ownedOperation:
      for p in o.ownedParameter:
          do_something(p)

Using the ``[:]`` operator items can be traversed more easily:

  for o in classes.ownedOperation[:].ownedParameter:
      do_something(p)



It's also possible to provide a query as part of the selection::

  for o in classes.ownedOperation['it.returnParameter'].ownedParameter:
      do_something(p)

The variable ``it`` in the query refers to the evaluated object (in this case
all operations with a return parameter are taken into account).

