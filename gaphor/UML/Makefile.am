
GEN_UML=$(top_srcdir)/utils/genUML.py
METAMODEL_XMI=$(top_srcdir)/doc/UmlMetaModel.xmi

all-local: ModelElements.py

ModelElements.py: $(GEN_UML) $(METAMODEL_XMI)
	$(GEN_UML) $(METAMODEL_XMI) 2>&1 > genModelElements.py
	grep -v "PresentationElement" genModelElements.py > ModelElements.py
	rm -f genModelElements.py

EXTRA_DIST=Element.py ModelElements.py management.py __init__.py
