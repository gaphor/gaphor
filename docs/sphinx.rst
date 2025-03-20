Sphinx Extension
================

What's more awesome than to use Gaphor diagrams directly in your `Sphinx`_ documentation.
Whether you write your docs in `reStructured Text`_ or `Markdown`_, we've got you covered.

.. tip::

   Here we cover the reStructured Text syntax. If you prefer markdown, we suggest you
   have a look at the `MyST-parser <https://myst-parser.readthedocs.io/>`_, as it
   `supports Sphinx directives <https://myst-parser.readthedocs.io/en/latest/syntax/roles-and-directives.html>`_.

It requires `minimal effort to set up <#configuration>`_. Adding a diagram is as simple as:

.. code:: rst

   .. diagram:: main

.. diagram:: main
   :model: example

In case you use multiple Gaphor source files, you need to define a ``:model:`` attribute
and add the model names to the Sphinx configuration file (``conf.py``).

.. code:: rst

   .. diagram:: main
      :model: example

Diagrams can be referenced by their name, or by their fully qualified name.

.. code:: rst

   .. diagram:: New model.main

`Figure`_, and `Image properties`_ can also be applied:

.. code:: rst

   .. diagram:: main
      :figwidth: image
      :align: center
      :alt: A description suitable for an example

      You can also add a caption, if you want.

.. diagram:: main
   :model: example
   :figwidth: image
   :align: center
   :alt: A description suitable for an example

   You can also add a caption, if you want.

Configuration
-------------

To add Gaphor diagram support to Sphinx, make sure Gaphor is listed as a dependency.

.. important::

   Gaphor requires at least Python 3.9.

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

* ``libgirepository-2.0-dev`` is required to build PyGObject.
* ``gir1.2-pango-1.0`` is required for text rendering.

.. note::

   For Gaphor 2.7.0, ``gir1.2-gtk-3.0`` and ``gir1.2-gtksource-4`` are required ``apt_packages``, although we do not use the GUI.
   From Gaphor 2.7.1 onwards all you need is GI-repository and Pango.


Errors
------

Errors are shown on the console when the documentation is built and in the document.

An error will appear in the documentation. Something like this:

.. error::

   No diagram ‘Wrong name’ in model ‘example’ (../examples/sequence-diagram.gaphor).


.. _Sphinx: https://www.sphinx-doc.org
.. _reStructured Text: https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html
.. _Markdown: https://myst-parser.readthedocs.io
.. _Figure: https://docutils.sourceforge.io/docs/ref/rst/directives.html#figure
.. _Image properties: https://docutils.sourceforge.io/docs/ref/rst/directives.html#image
.. _Read the Docs: https://readthedocs.org
.. _.readthedocs.yaml: https://docs.readthedocs.io/en/stable/config-file/v2.html
