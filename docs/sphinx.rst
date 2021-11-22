Sphinx extension
================

What's more awesome than to use Gaphor diagrams directly in your `Sphinx`_ documentation.

In case you use multiple Gaphor source files, you need to define a ``:model:`` attribute.

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
       "gaphor.extensions.sphinx",
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


Read the Docs
~~~~~~~~~~~~~

The diagram directive plays nice with `Read the docs`_.
To make diagrams render, it's best to use a `.readthedocs.yaml`_ file in your project.
Make sure to include the extra ``apt_packages`` as shown below.

This is the ``.readthedocs.yaml`` file we use for Gaphor:

.. literalinclude :: ../.readthedocs.yaml
   :language: yaml

* ``libgirepository1.0-dev`` is required to build PyGObject.
* ``gir1.2-pango-1.0`` is required for text rendering.
* ``gir1.2-gtk-3.0`` and ``gir1.2-gtksource-4`` are needed, although we do not use the GUI.


Errors
------

Errors are shown on the console when the documentation is built and in the document.

The model cannot be found:

.. diagram:: Wrong name
   :model: not-a-model

The model can be found, but the diagram cannot be found:

.. diagram:: Wrong name
   :model: example


.. _Sphinx: https://sphinx-doc.org
.. _Image properties: https://docutils.sourceforge.io/docs/ref/rst/directives.html#image
.. _Read the Docs: https://readthedocs.org
.. _.readthedocs.yaml: https://docs.readthedocs.io/en/stable/config-file/v2.html