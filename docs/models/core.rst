Modeling Language Core
======================

The Core modeling language is the the basis for any other language.

The :obj:`~gaphor.core.modeling.Base` class acts as the root for all gaphor domain classes.
:obj:`~gaphor.core.modeling.Diagram` and :obj:`~gaphor.core.modeling.Presentation` form the basis for everything you see
in a diagram.

All data models in Gaphor are generated from actual Gaphor model files.
This allows us to provide you nice diagrams of Gaphor’s internal model.

.. diagram:: Presentations
   :model: core

   The core model with presentation classes

The ``Base`` Class
^^^^^^^^^^^^^^^^^^

The :obj:`~gaphor.core.modeling.Base` class provides event notification and integrates
with the model repository (internally known as :obj:`~gaphor.core.modeling.ElementFactory`).
All classes in a model should derive from this class. If a model does not show a base class
for an element, it will derive from :obj:`~gaphor.core.modeling.Base`.
Bi-directional relationships are also possible, as well as derived
relations.

The :obj:`~gaphor.core.modeling.base.RepositoryProtocol`, and
:obj:`~gaphor.core.modeling.base.EventWatcherProtocol`
protocols are important to connect the model to the repository and event handling
mechanisms.

The class ``Base`` is the core of Gaphor’s data model.

.. autoclass:: gaphor.core.modeling.Base


   .. autoproperty:: gaphor.core.modeling.Base.id

   .. autoproperty:: gaphor.core.modeling.Base.model

   .. automethod:: gaphor.core.modeling.Base.unlink

   Event handling
   --------------

   .. automethod:: gaphor.core.modeling.Base.handle

   .. automethod:: gaphor.core.modeling.Base.watcher


   Loading and saving
   ------------------

   .. automethod:: gaphor.core.modeling.Base.load

   .. automethod:: gaphor.core.modeling.Base.postload

   .. automethod:: gaphor.core.modeling.Base.save


   OCL-style methods
   -----------------

   .. automethod:: gaphor.core.modeling.Base.isKindOf

   .. automethod:: gaphor.core.modeling.Base.isTypeOf


The ``Presentation`` class
^^^^^^^^^^^^^^^^^^^^^^^^^^


.. autoclass:: gaphor.core.modeling.Presentation

   .. automethod:: gaphor.core.modeling.Presentation.request_update

   .. automethod:: gaphor.core.modeling.Presentation.watch

   .. automethod:: gaphor.core.modeling.Presentation.change_parent


The ``Diagram`` class
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: gaphor.core.modeling.Diagram

   .. automethod:: gaphor.core.modeling.Diagram.create

   .. automethod:: gaphor.core.modeling.Diagram.lookup

   .. automethod:: gaphor.core.modeling.Diagram.select

   .. automethod:: gaphor.core.modeling.Diagram.request_update

   .. automethod:: gaphor.core.modeling.Diagram.update

Protocols
---------

.. autoclass:: gaphor.core.modeling.base.RepositoryProtocol

   .. automethod:: gaphor.core.modeling.base.RepositoryProtocol.create

      Create a new element in the repository.

   .. method:: select(self, expression: Callable[[Base], bool]) -> Iterator[Base]

      Select elements from the repository that fulfill ``expression``.

   .. method:: select(self, type_: type[T]) -> Iterator[T]
      :noindex:

      Select all elements from the repository of type ``type_``.

   .. method:: select(self, expression: None) -> Iterator[Base]
      :noindex:

      Select all elements from the repository.

   .. automethod:: gaphor.core.modeling.base.RepositoryProtocol.lookup

      Get an element by id from the repository.

      Returns :const:`None` if no such element exists.

.. autoclass:: gaphor.core.modeling.base.EventWatcherProtocol

   .. automethod:: gaphor.core.modeling.base.EventWatcherProtocol.watch

      Add a watch for a specific path. The path is relative to the element
      that created the watcher object.

      Returns ``self``, so watch operations can be chained.

   .. automethod:: gaphor.core.modeling.base.EventWatcherProtocol.unsubscribe_all

      Should be called before the watcher is disposed, to release all watched paths.


.. toctree::
   :hidden:

   core_changeset
   core_services
