
GEN_UML = $(top_srcdir)/utils/genUML.py
METAMODEL_XMI = $(top_srcdir)/doc/UmlMetaModel.xmi

umldir = $(pythondir)/$(subdir)

uml_PYTHON = \
	__init__.py	\
	enumeration.py	\
	sequence.py	\
	element.py	\
	elementfactory.py \
	modelelements.py \
	diagram.py

all-local: modelelements.py

modelelements.py: $(GEN_UML) $(METAMODEL_XMI)
	$(GEN_UML) $(METAMODEL_XMI) 2>&1 > genmodelelements.py
	-echo We have our own presentation element class (diagra.Diagram)
	grep -v "PresentationElement" genmodelelements.py > modelelements.py
	rm -f genmodelelements.py

#EXTRA_DIST = $(python_files)

CLEANFILES = *.pyc *.pyo
