from builtins import object
from builtins import str
from logging import getLogger

from gaphor.misc.xmlwriter import XMLWriter


class XMIExport(object):

    XMI_VERSION = "2.1"
    XMI_NAMESPACE = "http://schema.omg.org/spec/XMI/2.1"
    UML_NAMESPACE = "http://schema.omg.org/spec/UML/2.1"
    XMI_PREFIX = "XMI"
    UML_PREFIX = "UML"

    logger = getLogger(__name__)

    def __init__(self, element_factory):
        self.element_factory = element_factory
        self.handled_ids = list()

    def handle(self, xmi, element):
        self.logger.debug("Handling %s" % element.__class__.__name__)
        try:
            handler_name = "handle%s" % element.__class__.__name__
            handler = getattr(self, handler_name)
            idref = element.id in self.handled_ids
            handler(xmi, element, idref=idref)
            if not idref:
                self.handled_ids.append(element.id)
        except AttributeError as e:
            self.logger.warning(
                "Missing handler for %s:%s" % (element.__class__.__name__, e)
            )
        except Exception as e:
            self.logger.error(
                "Failed to handle %s:%s" % (element.__class__.__name__, e)
            )

    def handlePackage(self, xmi, element, idref=False):

        attributes = dict()
        attributes["%s:id" % self.XMI_PREFIX] = element.id
        attributes["name"] = element.name
        attributes["visibility"] = element.visibility

        xmi.startElement("%s:Package" % self.UML_PREFIX, attrs=attributes)

        for ownedMember in element.ownedMember:
            xmi.startElement("ownedMember", attrs=dict())
            self.handle(xmi, ownedMember)
            xmi.endElement("ownedMember")

        xmi.endElement("%s:Package" % self.UML_PREFIX)

    def handleClass(self, xmi, element, idref=False):

        attributes = dict()

        if idref:
            attributes["%s:idref" % self.XMI_PREFIX] = element.id
        else:
            attributes["%s:id" % self.XMI_PREFIX] = element.id
            attributes["name"] = element.name
            attributes["isAbstract"] = str(element.isAbstract)

        xmi.startElement("%s:Class" % self.UML_PREFIX, attrs=attributes)

        if not idref:

            for ownedAttribute in element.ownedAttribute:
                xmi.startElement("ownedAttribute", attrs=dict())
                self.handle(xmi, ownedAttribute)
                xmi.endElement("ownedAttribute")

            for ownedOperation in element.ownedOperation:
                xmi.startElement("ownedOperation", attrs=dict())
                self.handle(xmi, ownedOperation)
                xmi.endElement("ownedOperation")

        xmi.endElement("%s:Class" % self.UML_PREFIX)

    def handleProperty(self, xmi, element, idref=False):

        attributes = dict()
        attributes["%s:id" % self.XMI_PREFIX] = element.id
        attributes["isStatic"] = str(element.isStatic)
        attributes["isOrdered"] = str(element.isOrdered)
        attributes["isUnique"] = str(element.isUnique)
        attributes["isDerived"] = str(element.isDerived)
        attributes["isDerivedUnion"] = str(element.isDerivedUnion)
        attributes["isReadOnly"] = str(element.isReadOnly)

        if element.name is not None:
            attributes["name"] = element.name

        xmi.startElement("%s:Property" % self.UML_PREFIX, attrs=attributes)

        # TODO: This should be type, not typeValue.
        if element.typeValue is not None:
            xmi.startElement("type", attrs=dict())
            self.handle(xmi, element.typeValue)
            xmi.endElement("type")

        xmi.endElement("%s:Property" % self.UML_PREFIX)

    def handleOperation(self, xmi, element, idref=False):

        attributes = dict()
        attributes["%s:id" % self.XMI_PREFIX] = element.id
        attributes["isStatic"] = str(element.isStatic)
        attributes["isQuery"] = str(element.isQuery)
        attributes["name"] = element.name

        xmi.startElement("%s:Operation" % self.XMI_PREFIX, attrs=attributes)

        for ownedParameter in element.parameter:
            xmi.startElement("ownedElement", attrs=dict())
            self.handle(xmi, ownedParameter)
            xmi.endElement("ownedElement")

        xmi.endElement("%s:Operation" % self.XMI_PREFIX)

    def handleParameter(self, xmi, element, idref=False):

        attributes = dict()
        attributes["%s:id" % self.XMI_PREFIX] = element.id
        attributes["isOrdered"] = str(element.isOrdered)
        attributes["isUnique"] = str(element.isUnique)

        attributes["direction"] = element.direction
        attributes["name"] = element.name

        xmi.startElement("%s:Parameter" % self.XMI_PREFIX, attrs=attributes)

        xmi.endElement("%s:Parameter" % self.XMI_PREFIX)

    def handleLiteralSpecification(self, xmi, element, idref=False):

        attributes = dict()
        attributes["%s:id" % self.XMI_PREFIX] = element.id
        attributes["value"] = element.value

        xmi.startElement("%s:LiteralSpecification" % self.UML_PREFIX, attrs=attributes)

        xmi.endElement("%s:LiteralSpecification" % self.UML_PREFIX)

    def handleAssociation(self, xmi, element, idref=False):

        attributes = dict()
        attributes["%s:id" % self.XMI_PREFIX] = element.id
        attributes["isDerived"] = str(element.isDerived)

        xmi.startElement("%s:Association" % self.UML_PREFIX, attrs=attributes)

        for memberEnd in element.memberEnd:
            xmi.startElement("memberEnd", attrs=dict())
            self.handle(xmi, memberEnd)
            xmi.endElement("memberEnd")

        for ownedEnd in element.ownedEnd:
            xmi.startElement("ownedEnd", attrs=dict())
            self.handle(xmi, ownedEnd)
            xmi.endElement("ownedEnd")

        xmi.endElement("%s:Association" % self.UML_PREFIX)

    def handleDependency(self, xmi, element, idref=False):

        attributes = dict()
        attributes["%s:id" % self.XMI_PREFIX] = element.id

        xmi.startElement("%s:Dependency" % self.UML_PREFIX, attrs=attributes)

        for client in element.client:
            xmi.startElement("client", attrs=dict())
            self.handle(xmi, client)
            xmi.endElement("client")

        for supplier in element.supplier:
            xmi.startElement("supplier", attrs=dict())
            self.handle(xmi, supplier)
            xmi.endElement("supplier")

        xmi.endElement("%s:Dependency" % self.UML_PREFIX)

    def handleGeneralization(self, xmi, element, idref=False):

        attributes = dict()
        attributes["%s:id" % self.XMI_PREFIX] = element.id
        attributes["isSubstitutable"] = str(element.isSubstitutable)

        xmi.startElement("%s:Generalization" % self.UML_PREFIX, attrs=attributes)

        if element.general:
            xmi.startElement("general", attrs=dict())
            self.handle(xmi, element.general)
            xmi.endElement("general")

        if element.specific:
            xmi.startElement("specific", attrs=dict())
            self.handle(xmi, element.specific)
            xmi.endElement("specific")

        xmi.endElement("%s:Generalization" % self.UML_PREFIX)

    def handleRealization(self, xmi, element, idref=False):

        attributes = dict()
        attributes["%s:id" % self.XMI_PREFIX] = element.id

        xmi.startElement("%s:Realization" % self.UML_PREFIX, attrs=attributes)

        for client in element.client:
            xmi.startElement("client", attrs=dict())
            self.handle(xmi, client)
            xmi.endElement("client")

        for supplier in element.supplier:
            xmi.startElement("supplier", attrs=dict())
            self.handle(xmi, supplier)
            xmi.endElement("supplier")

        xmi.endElement("%s:Realization" % self.UML_PREFIX)

    def handleInterface(self, xmi, element, idref=False):

        attributes = dict()
        attributes["%s:id" % self.XMI_PREFIX] = element.id

        xmi.startElement("%s:Interface" % self.UML_PREFIX, attrs=attributes)

        for ownedAttribute in element.ownedAttribute:
            xmi.startElement("ownedAttribute", attrs=dict())
            self.handle(ownedAttribute)
            xmi.endElement("ownedAttribute")

        for ownedOperation in element.ownedOperation:
            xmi.startElement("ownedOperation", attrs=dict())
            self.handle(ownedOperation)
            xmi.endElement("ownedOperation")

        xmi.endElement("%s:Interface" % self.UML_PREFIX)

    def export(self, filename):
        out = open(filename, "w")

        xmi = XMLWriter(out)

        attributes = dict()
        attributes["xmi.version"] = self.XMI_VERSION
        attributes["xmlns:xmi"] = self.XMI_NAMESPACE
        attributes["xmlns:UML"] = self.UML_NAMESPACE

        xmi.startElement("XMI", attrs=attributes)

        for package in self.element_factory.select(self.select_package):
            self.handle(xmi, package)

        for generalization in self.element_factory.select(self.select_generalization):
            self.handle(xmi, generalization)

        for realization in self.element_factory.select(self.select_realization):
            self.handle(xmi, realization)

        xmi.endElement("XMI")

        self.logger.debug(self.handled_ids)

    def select_package(self, element):
        return element.__class__.__name__ == "Package"

    def select_generalization(self, element):
        return element.__class__.__name__ == "Generalization"

    def select_realization(self, element):
        return element.__class__.name__ == "Implementation"
