Gaphor's Framework
==================

Gaphor is built in a light, service oriented fashion. The application is split
in a series of services, such as a file manager, undo manager and GUI manager.
Those services are loaded based on entry points defined in Python Eggs
(see :doc:`Service oriented design <so>`).

Objects communicate with each other through events. Whenever something of
importance happens (e.g. an attribute of a model element changes) an event is
sent. Whoever is interested (a diagram item for example) receive notification
once it has registered an event handler for that event type. Events are emitted
though a central broken (zope.component in our case), so you do not have to
register on every individual element that can send an event you're interested
in (so the diagram item should check if the element that sent the event is
actually the event the item is representing).


Gaphor is transactional. Transactions work simply by sending an event when a
transaction starts and sending another when a transaction ends. E.g. undo
management is transactional.

It all starts with an Application. Only one Application instance is permitted.
The Application will look for services defined as :doc:`gaphor.services 
<services>`. Those services are loaded and initialized.

The most notable services are:

gui_manager
  The GUI manager is one of the major services that have to be loaded. The 
  GUI manager is responsible for loading the main window and displaying it 
  on the screen.

  This by itself doesn't do a thing though. The Action manager 
  (`action_manager`) is required to maintain all actions users can perform.
  Actions will be shown as menu entries for example.

file_manager
  Loading and saving a model is done through this service. 

element_factory
  The :doc:`data model <datamodel>` itself is maintained in the element
  factory. This service is used to create model elements and can be used to
  lookup elements or query for a set of elements.

:doc:`undo_manager <undo>`
  One of the most appreciated services. It allows users to make a mistake
  every now and then!

  The undo manager is transactional. Actions performed by a user are only
  stored if a transaction is active. If a transaction is completed (committed)
  a new undo action is stored. Transactions can also be rolled back, in which
  case all changes are played back directly.

element_dispatcher
  Although Gaphor makes use of a central dispatch engine, this solution is not
  efficient when it comes to dispatching events of UML model elements. For
  this purpose the `element_dispatcher` can help out. It maintains a path of
  elements reaching from the root (e.g. from a diagram item) to the element of
  interest and will only signal in case this element changes.
  This makes complex dispatching very efficient.

.. autoclass:: gaphor.services.elementdispatcher.ElementDispatcher
