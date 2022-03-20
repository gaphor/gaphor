Gaphor -- Technical Documentation
==================================

Gaphor is a UML and SysML modeling application written in Python.
It is designed to be easy to use, while still being powerful.
Gaphor implements a fully-compliant UML 2 data model,
so it is much more than a picture drawing tool.
You can use Gaphor to quickly visualize different aspects of a system
as well as create complete, highly complex models.

This documentation is aimed at those who would be interested in making
contributions to Gaphor. For download instructions, tutorials and how-to's, please visit the
`Gaphor Website <https://gaphor.org>`_.

If you're into writing plug-ins for Gaphor you should have a look at our
fabulous `Hello world <https://github.com/gaphor/gaphor.plugins.helloworld>`_
plug-in.


.. toctree::
   :caption: Installation
   :maxdepth: 1

   linux
   macos
   windows

.. toctree::
   :caption: Features
   :maxdepth: 1

   style_sheets
   stereotypes
   sphinx

.. toctree::
   :caption: Modeling languages
   :maxdepth: 1

   models/core
   models/uml
   models/sysml
   models/raaml
   models/c4model

.. toctree::
   :caption: Concepts
   :maxdepth: 1

   design_principles
   framework
   service_oriented
   event_system
   modeling_language

.. toctree::
   :caption: Internals
   :maxdepth: 1

   connect
   storage
   undo
   transaction


External links
--------------

* You should definitely check out `Agile Modeling <http://www.agilemodeling.com>`_ including these pages:

  1. `UML Diagrams <http://www.agilemodeling.com/essays/umlDiagrams.htm>`_ (although Gaphor does not see it that black-and-white).
  2. http://www.agilemodeling.com/essays/
* The `official UML specification <https://www.omg.org/spec/UML>`_. This ''is'' our data model.
