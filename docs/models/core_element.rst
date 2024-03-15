Core Modeling Classes
=====================

Here you can find a short description of the base classes in
a Gaphor model: :obj:`~gaphor.core.modeling.Element`,
:obj:`~gaphor.core.modeling.Presentation`, and :obj:`~gaphor.core.modeling.Diagram`.

The :obj:`~gaphor.core.modeling.element.RepositoryProtocol`, and
:obj:`~gaphor.core.modeling.element.EventWatcherProtocol`
protocols are important to connect the model to the repository and event handling
mechanisms.


The ``Element`` Class
---------------------

The class ``Element`` is the core of Gaphor's data model.

.. autoclass:: gaphor.core.modeling.Element


   .. autoproperty:: gaphor.core.modeling.Element.id

   .. autoproperty:: gaphor.core.modeling.Element.model

   .. automethod:: gaphor.core.modeling.Element.unlink

   Event handling
   --------------

   .. automethod:: gaphor.core.modeling.Element.handle

   .. automethod:: gaphor.core.modeling.Element.watcher


   Loading and saving
   ------------------

   .. automethod:: gaphor.core.modeling.Element.load

   .. automethod:: gaphor.core.modeling.Element.postload

   .. automethod:: gaphor.core.modeling.Element.save


   OCL-style methods
   -----------------

   .. automethod:: gaphor.core.modeling.Element.isKindOf

   .. automethod:: gaphor.core.modeling.Element.isTypeOf


The ``Presentation`` class
--------------------------

.. autoclass:: gaphor.core.modeling.Presentation

   .. automethod:: gaphor.core.modeling.Presentation.request_update

   .. automethod:: gaphor.core.modeling.Presentation.watch

   .. automethod:: gaphor.core.modeling.Presentation.change_parent


The ``Diagram`` class
--------------------------

.. autoclass:: gaphor.core.modeling.Diagram

   .. automethod:: gaphor.core.modeling.Diagram.create

   .. automethod:: gaphor.core.modeling.Diagram.lookup

   .. automethod:: gaphor.core.modeling.Diagram.select


Protocols
---------

.. autoclass:: gaphor.core.modeling.element.RepositoryProtocol

   .. automethod:: gaphor.core.modeling.element.RepositoryProtocol.create

      Create a new element in the repository.

   .. method:: select(self, expression: Callable[[Element], bool]) -> Iterator[Element]

      Select elements from the repository that fulfill ``expression``.

   .. method:: select(self, type_: type[T]) -> Iterator[T]
      :noindex:

      Select all elements from the repository of type ``type_``.

   .. method:: select(self, expression: None) -> Iterator[Element]
      :noindex:

      Select all elements from the repository.

   .. automethod:: gaphor.core.modeling.element.RepositoryProtocol.lookup

      Get an element by id from the repository.

      Returns :const:`None` if no such element exists.

.. autoclass:: gaphor.core.modeling.element.EventWatcherProtocol

   .. automethod:: gaphor.core.modeling.element.EventWatcherProtocol.watch

      Add a watch for a specific path. The path is relative to the element
      that created the watcher object.

      Returns ``self``, so watch operations can be chained.

   .. automethod:: gaphor.core.modeling.element.EventWatcherProtocol.unsubscribe_all

      Should be called before the watcher is disposed, to release all watched paths.
