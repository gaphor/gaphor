Core Services
=============

here you can find the API for services that are related to
model creation and model manipulation.


Element Repository (/Factory)
-----------------------------

.. autoclass:: gaphor.core.modeling.ElementFactory

   .. automethod:: gaphor.core.modeling.ElementFactory.select

   .. automethod:: gaphor.core.modeling.ElementFactory.lselect

   .. automethod:: gaphor.core.modeling.ElementFactory.lookup

   .. automethod:: gaphor.core.modeling.ElementFactory.keys

   .. automethod:: gaphor.core.modeling.ElementFactory.values

   .. automethod:: gaphor.core.modeling.ElementFactory.size

   .. automethod:: gaphor.core.modeling.ElementFactory.is_empty

   .. automethod:: gaphor.core.modeling.ElementFactory.create

   .. automethod:: gaphor.core.modeling.ElementFactory.flush


Modeling Language
-----------------

Information on how modeling languages are managed can be found :doc:`../modeling_language`.


Event Manager
-------------

The :doc:`../event_system` takes care of dispatches events throughout Gaphor.
