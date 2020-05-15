The Gaphor Technical Documentation
==================================

This documentation is aimed at those who would be interested in making
contributions to Gaphor. For tutorials and how-to information, please visit the
`Gaphor Website <https://gaphor.org>`_.

In the future, we would like to split the documentation in to sections that
focus on **explanation** (understanding-oriented) and **reference**
(information-oriented). For now, this information is all together.

If you're into writing plug-ins for Gaphor you should have a look at our
fabulous `Hello world <https://github.com/gaphor/gaphor.plugins.helloworld>`_
plug-in.

Setting up a development environment, and packaging Gaphor on different
platforms:

.. toctree::
   :caption: Installation
   :maxdepth: 1

   linux
   macos
   windows

.. toctree::
   :caption: Concepts
   :maxdepth: 1

   framework
   service_oriented
   event_system
   modeling_language
   transaction
   items

.. toctree::
   :caption: UML and data model
   :maxdepth: 1

   model
   stereotypes
   datamodel
   connect

.. toctree::
   :caption: Storage
   :maxdepth: 1

   storage
   xml-format

.. toctree::
   :caption: Services
   :maxdepth: 1
   undo

External links
--------------

* You should definitely check out `Agile Modeling <http://www.agilemodeling.com>`_ including these pages:

  1. `UML Diagrams <http://www.agilemodeling.com/essays/umlDiagrams.htm>`_ (although Gaphor does not see it that black-and-white).
  2. http://www.agilemodeling.com/essays/
* The `official UML specification <https://www.omg.org/spec/UML>`_. This ''is'' our data model.
