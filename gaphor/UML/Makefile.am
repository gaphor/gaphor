
GEN_UML=$(top_srcdir)/utils/genUML.py
METAMODEL_XMI=$(top_srcdir)/doc/UmlMetaModel.xmi

all-local: ModelElements.py

modelelements.py: $(GEN_UML) $(METAMODEL_XMI)
	$(GEN_UML) $(METAMODEL_XMI) 2>&1 > genmodelelements.py
	# We have our own presentation element class (diagra.Diagram)
	grep -v "PresentationElement" genmodelelements.py > modelelements.py
	rm -f genmodelelements.py

python_files = \
	__init__.py	\
	enumeration.py	\
	sequence.py	\
	element.py	\
	elementfactory.py \
	modelelements.py

EXTRA_DIST = $(python_files)

CLEANFILES = *.pyc *.pyo
