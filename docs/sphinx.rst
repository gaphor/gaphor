Sphinx support
==============

What's more awesome than to use Gaphor diagrams directly in your `Sphinx`_ documentation.

In case you use multiple Gaphor source files, you need to define a ``:model:`` attribute.

Diagrams can be referenced by their name, or by their fully qualified name.

.. code:: rst

   .. diagram:: main
      :model: example

.. diagram:: main
   :model: example

Diagrams can be referenced by their name, or by their fully qualified name.

.. code:: rst

   .. diagram:: New model.main
      :model: example

`Image properties`_ can also be applied:

.. code:: rst

   .. diagram:: main
      :model: example
      :width: 50%
      :align: right
      :alt: A description suitable for an example

.. diagram:: main
   :model: example
   :width: 50%
   :align: center
   :alt: A description suitable for an example


Configuration
-------------

To add Gaphor diagram support to Sphinx, make sure Gaphor is listed as a dependency.

Secondly, add the following to your ``conf.py`` file:

Step 1: Add gaphor as extension.

.. code:: python

   extensions = [
       "gaphor.sphinx",
   ]

Step 2: Add references to models

.. code:: python

   # A single model
   gaphor_models = "../examples/sequence-diagram.gaphor"

   # Or multiple models
   gaphor_models = {
       "connect": "connect.gaphor", 
       "example": "../examples/sequence-diagram.gaphor"
   }

Now include ``diagram`` directives in your documents.

Errors
------

Errors are shown on the console when the documentation is built and in the document.

The model can not be found:

.. diagram:: Wrong name
   :model: not-a-model

The model can be found, but the diagram can notnot be found:

.. diagram:: Wrong name
   :model: connect


.. _Sphinx: https://sphinx-doc.org
.. _Image properties: https://docutils.sourceforge.io/docs/ref/rst/directives.html#image