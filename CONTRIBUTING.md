Feel free to hack Gaphor. Patches are welcome.

Fetching Development Dependencies
=================================

Gaphor uses pip to manage in easy way its dependencies.

To fetch and install dependencies as non-root user:
In Linux recommend using a virtual environment for installation. Since pyGTK doesn't work well with a virtualenv,
install it outside the virtual environment and then start your the virtualenv using the --system-site-packages option:
  $ virtualenv --system-site-packages venv
  $ source venv/bin/activate
  $ pip install gaphor

Running Tests
=============
To run tests on Unix machine

    Xvfb :2.0 &
    DISPLAY=:2.0 nosetests gaphor/ 2>&1 | tee tests.log


Structure
=========

Gaphor contains the following modules:

UML
---
The UML module contains the UML 2.0 data model. This part is
quite stable and it is unlikely that code has to be changed
here.

  NOTE:	The code is generated from a Gaphor model: uml2.gaphor. This
	file can be loaded in gaphor.

diagram
-------
The diagram module contains items that can be placed in diagrams.
In most cases the classes NamedItem and Relationship can serve
as bases for your class.

ui
--
The user interface. This is where most of the work is to be done.

misc
----
Some utility stuff, such as Actions and aspects are put in here.
