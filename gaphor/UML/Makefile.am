
GEN_UML=$(top_srcdir)/utils/genUML.py
METAMODEL_XMI=$(top_srcdir)/doc/UmlMetaModel.xmi

all-local: UML_MetaModel.py

UML_MetaModel.py: $(GEN_UML) $(METAMODEL_XMI)
	$(GEN_UML) $(METAMODEL_XMI) 2>&1 > UML_MetaModel.py

EXTRA_DIST=Element.py __init__.py UML_MetaModel.py
