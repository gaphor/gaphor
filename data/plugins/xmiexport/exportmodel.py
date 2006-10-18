# vim:sw=4:et

#from xml.sax.saxutils import XMLGenerator
import time
import gaphor
from gaphor import UML
from gaphor.misc.xmlwriter import XMLWriter

class XMLAttributes(dict):
    def getLength(self):
        """ Return the number of attributes. """
        return len(self.keys())

    def getNames(self):
        """ Return the names of the attributes. """
        return self.keys()
        
    def getType(self, name):
        """ Returns the type of the attribute name, which is normally 'CDATA'. """
        return 'CDATA'

    def getValue(name):
        """ Return the value of attribute name. """ 
        return self[name]


class XMIExport(object):
    
    # State diagram specific
    # ======================
    def handleInitialNode(self, xmi, node):
        attributes = XMLAttributes()
        attributes['xmi.id']=node.id
        attributes['name']="start" # Gaphor doens't have name support 
                                   # for start actions.
        attributes['visibility'] = 'public'
        attributes['isSpecification'] = 'false'
        attributes['kind'] = 'initial'
        xmi.startElement('UML2:Pseudostate', attrs=attributes)
        xmi.startElement('UML2:Vertex.outgoing')
        
                         
        
    def handleAction(self, xmi, node):
        attributes = XMLAttributes()
        attributes['xmi.id']=node.id
        attributes['name']=node.name
        attributes['visibility'] = 'public'
        attributes['isSpecification'] = 'false'
    
    def handleControlFlow(self, xmi, node):
        pass
    
    
    # Class diagram specific
    #=========================

    def handlePackage(self, xmi, node):
        if node.package != None: return
        self.writePackage(xmi, node)

    def writePackage(self, xmi, node):
        attributes=XMLAttributes()
        attributes['xmi.id']=node.id
        attributes['name']=node.name
        attributes['visibility']='public' # TODO
        attributes['isSpecification']='false'
        attributes['isRoot']='false'
        attributes['isLeaf']='false'
        attributes['isAbstract']='false' #node.isAbstract and 'true' or 'false'
        attributes['isActive']='false'
        xmi.startElement('UML:Package', attrs=attributes)
        xmi.startElement('UML:Namespace.ownedElement', attrs=XMLAttributes())
        classes = [element for element in gaphor.resource('ElementFactory').select()]
        for item in classes:
            try:
                package = item.package==node
            except AttributeError:
                continue
            if package:
                try:
                    handler=getattr(self, 'write%s'%item.__class__.__name__)
                except AttributeError:
                    continue
                handler(xmi, item)
        xmi.endElement('UML:Namespace.ownedElement')
        xmi.endElement('UML:Package')


    def handleClass(self, xmi, node):
        """ """ 
        # Check for packages, classes will be serialized through the package
        if node.package != None: return
        
        self.writeClass(xmi, node)

    def writeClass(self, xmi, node):
        # Check for stereotype definition classes
        if node.name in ('Class', 'Interface', 'Package'): return
        
        attributes=XMLAttributes()
        attributes['xmi.id']=node.id
        attributes['name']=node.name
        attributes['visibility']='public' # TODO
        attributes['isSpecification']='false'
        attributes['isRoot']='false'
        attributes['isLeaf']='false'
        attributes['isAbstract']=node.isAbstract and 'true' or 'false'
        attributes['isActive']='false'
        xmi.startElement('UML:Class', attrs=attributes)
        
        # Generalization stuff
        generalizations = node.generalization
        if generalizations:
            xmi.startElement('UML:GeneralizableElement.generalization', attrs=XMLAttributes())
            for item in generalizations:
                attributes=XMLAttributes()
                attributes['xmi.idref']=item.id
                xmi.startElement('UML:Generalization', attrs=attributes)
                xmi.endElement('UML:Generalization')
            xmi.endElement('UML:GeneralizableElement.generalization')
    
        # Stereotypes
        stereotypes = node.appliedStereotype
        if stereotypes:
            xmi.startElement('UML:ModelElement.stereotype', attrs=XMLAttributes())
            for stereotype in stereotypes:
                attributes = XMLAttributes({'xmi.idref': stereotype.id})
                xmi.startElement('UML:Stereotype', attrs=attributes)
                xmi.endElement('UML:Stereotype')
            xmi.endElement('UML:ModelElement.stereotype')
        
        # Generate the field type classes
        xmi.startElement('UML:Namespace.ownedElement', attrs=XMLAttributes())
        for attribute in node.ownedAttribute:
            try:
                attribute.name
                attribute.typeValue.value
            except AttributeError:
                continue
                
            attributes=XMLAttributes()
            attributes['xmi.id']=attribute.typeValue.id
            typeName = attribute.typeValue.value
            if not typeName:
                print "Warning, no type name given for attribute (so no export for this one)"
                continue
            attributes['name']=typeName
            attributes['visibility']='public'
            attributes['isSpecification']='false'
            attributes['isRoot']='false'
            attributes['isLeaf']='false'
            attributes['isAbstract']='false'
            attributes['isActive']='false'
            xmi.startElement('UML:Class', attrs=attributes)
            xmi.endElement('UML:Class')
        xmi.endElement('UML:Namespace.ownedElement')
 
        xmi.startElement('UML:Classifier.feature', attrs=XMLAttributes())
        
        # Now generate the XML for the attribute itself
        for attribute in node.ownedAttribute:
            try:
                attribute.name
                attribute.typeValue.value
            except AttributeError:
                continue
 
            attributes=XMLAttributes()
            attributes['xmi.id']=attribute.id
            attributes['name']=attribute.name or ''
            attributes['visibility']='public'
            attributes['isSpecification']='false'
            attributes['ownerScope']='instance'
            attributes['changeability']='changeable'
            xmi.startElement('UML:Attribute', attrs=attributes)
            
            xmi.startElement('UML:StructuralFeature.type', XMLAttributes())
            xmi.startElement('UML:Class', XMLAttributes({'xmi.idref': attribute.typeValue.id}))
            xmi.endElement('UML:Class')
            xmi.endElement('UML:StructuralFeature.type')
                           
            xmi.endElement('UML:Attribute')
        
        # Generate all methods
        for operation in node.ownedOperation:
            attributes=XMLAttributes()
            attributes['xmi.id']=operation.id
            attributes['name']=operation.name or ''
            attributes['visibility']='public'
            attributes['isSpecification']='false'
            attributes['ownerScope']='instance'
            attributes['isQuery']='false'
            attributes['concurrency']='sequential'
            attributes['isRoot']='false'
            attributes['isLeaf']='false'
            attributes['isAbstract']='false'
            xmi.startElement('UML:Operation', attrs=attributes)
            
            xmi.startElement('UML:BehavioralFeature.parameters', XMLAttributes())
            #self.writeParameters(operation.returnResult, operation, xmi, kind='return')
            self.writeParameters(operation.formalParameter, operation, xmi, kind='in')

            xmi.endElement('UML:BehavioralFeature.parameters')

            xmi.endElement('UML:Operation')

        
        xmi.endElement('UML:Classifier.feature')
        xmi.endElement('UML:Class')

    def writeParameters(self, parameters, operation, xmi, kind='in'):
        for parameter in parameters:
            attributes=XMLAttributes()
            attributes['xmi.id']=parameter.id
            attributes['name']=parameter.name or ''
            attributes['kind']=kind
            attributes['isSpecification']='false'
            xmi.startElement('UML:Parameter', attrs=attributes)
            xmi.startElement('UML:Parameter.type', attrs=XMLAttributes())
            xmi.startElement('UML:DataType', XMLAttributes({'xmi.idref': parameter.typeValue.id}))
            xmi.endElement('UML:DataType')
            xmi.endElement('UML:Parameter.type')
            xmi.endElement('UML:Parameter')


    def handleGeneralization(self, xmi, node):
        # Write out the generalization specifications
        attributes=XMLAttributes()
        attributes['xmi.id']=node.id
        attributes['isSpecification']='false'
        xmi.startElement('UML:Generalization', attrs=attributes)
        xmi.startElement('UML:Generalization.child', attrs=XMLAttributes())
        attributes=XMLAttributes()
        attributes['xmi.idref']=node.specific.id
        xmi.startElement('UML:Class', attrs=attributes)
        xmi.endElement('UML:Class')
        xmi.endElement('UML:Generalization.child')
        xmi.startElement('UML:Generalization.parent', attrs=XMLAttributes())
        attributes=XMLAttributes()
        attributes['xmi.idref']=node.general.id
        xmi.startElement('UML:Class', attrs=attributes)
        xmi.endElement('UML:Class')
        xmi.endElement('UML:Generalization.parent')
        xmi.endElement('UML:Generalization')
        
    def handleStereotype(self, xmi, node):
        attributes=XMLAttributes()
        attributes['xmi.id']=node.id
        attributes['name']=node.name
        attributes['visibility']='public'
        attributes['isSpecification']='false'
        attributes['isRoot']='false'
        attributes['isAbstract']='false'
        xmi.startElement('UML:Stereotype', attributes)
        xmi.startElement('UML:Stereotype.baseClass', attrs=XMLAttributes())
        xmi.characters('Classifier')
        xmi.endElement('UML:Stereotype.baseClass')
        xmi.endElement('UML:Stereotype')
        
    def handleAssociation(self, xmi, node):
        """
        """
        ends=node.memberEnd
        if len(ends)!=2:
            return
        
        """
        No longer in use as Gaphor is updated
        # Temp fix for line direction
        end_sequence = [0,1]
        if ends[1].aggregation=='composite':
            end_sequence = [0,1]
        else:
            end_sequence = [1,0]
        if ends[1].class_:
            end_sequence.reverse()
        """
        end_sequence = [0,1]

        attributes=XMLAttributes()
        attributes['xmi.id']=node.id
        attributes['isSpecification']='false'
        attributes['isRoot']='false'
        attributes['isLeaf']='false'
        attributes['isAbstract']='false'
        name = node.name
        if name:
            attributes['name']=name
        xmi.startElement('UML:Association', attrs=attributes)
        xmi.startElement('UML:Association.connection', attrs=XMLAttributes())

        for i in end_sequence: # Need an index for class lookup
            end=ends[i]
            attributes=XMLAttributes()
            attributes['xmi.id']=end.id
            attributes['visibility']='public'
            attributes['isSpecification']='false'
            attributes['isNavigable']=end.class_ and 'true' or 'false'
            attributes['ordering']='unordered'
            attributes['aggregation']=ends[1-i].aggregation # TODO: Handle None?
            attributes['targetScope']='instance' 
            attributes['changeability']='changeable'
            
            name = end.name
            if name:
                attributes['name']=name 

            xmi.startElement('UML:AssociationEnd', attrs=attributes)
            xmi.startElement('UML:AssociationEnd.multiplicity', attrs=XMLAttributes())
            attributes=XMLAttributes()
            attributes['xmi.id']=end.id+':%s'%i # Fabricate and id
            xmi.startElement('UML:Multiplicity', attrs=attributes)
            xmi.startElement('UML:Multiplicity.range', attrs=XMLAttributes())
            attributes=XMLAttributes()
            attributes['xmi.id']=str(id(attributes)) # No id in Gaphor for this
            values=('lower','upper')
            for value in values:
                try:
                    data=getattr(end, '%sValue'%value).value
                except AttributeError:
                    data='1' # FIXME!
                if str(data)=='*':
                    attributes['lower']='0'
                    attributes['upper']='-1'
                    break
                elif data is None:
                    data='1'
                attributes[value]=data
                
            xmi.startElement('UML:MultiplicityRange', attrs=attributes)
            xmi.endElement('UML:MultiplicityRange')
            xmi.endElement('UML:Multiplicity.range')
            xmi.endElement('UML:Multiplicity')
            xmi.endElement('UML:AssociationEnd.multiplicity')
            xmi.startElement('UML:AssociationEnd.participant', attrs=XMLAttributes())
            attributes=XMLAttributes()
            attributes['xmi.idref']=end.type.id 
            xmi.startElement('UML:Class', attrs=attributes)
            xmi.endElement('UML:Class')
            xmi.endElement('UML:AssociationEnd.participant')
            xmi.endElement('UML:AssociationEnd')
        xmi.endElement('UML:Association.connection')
        xmi.endElement('UML:Association')
            
            
    def export(self, filename):
        #out=open('/Users/vloothuis/test.xmi','w')
        out=open(filename,'w')

        xmi=XMLWriter(out)
        
        # Start XML generation
        attributes=XMLAttributes()
        attributes['xmi.version']='1.2'
        attributes['xmlns:UML']='org.omg.xmi.namespace.UML'
        attributes['timestamp'] = time.strftime('%a %b %d %H:%M:%S %Z %Y')
        xmi.startElement('XMI', attrs=attributes)
        
        self.writeHeader(xmi)
        
        # TODO: Add diagram stuff here
        
        self.writeModel(xmi, attributes)
        
        xmi.endElement('XMI')
        
        handlers={}

    def writeHeader(self, xmi):
        # Write out the XMI header
        xmi.startElement('XMI.header', attrs=XMLAttributes())
        xmi.startElement('XMI.documentation', attrs=XMLAttributes())
        xmi.startElement('XMI.exporter', attrs=XMLAttributes())
        xmi.characters('Gaphor XMI Export plugin')
        xmi.endElement('XMI.exporter')
        xmi.startElement('XMI.exporterVersion', attrs=XMLAttributes())
        xmi.characters('1.0') # TODO!
        xmi.endElement('XMI.exporterVersion')
        xmi.endElement('XMI.documentation')
        xmi.endElement('XMI.header')


    def writeModel(self, xmi, attributes):
        # Generator the model
        xmi.startElement('XMI.content', attrs=XMLAttributes())
        # Now write out the model
        attributes=XMLAttributes()
        attributes['xmi.id']='sm$f14318:ff442f5793:-7f6e'
        attributes['name'] = 'model 1'
        attributes['isSpecification'] = 'false'
        attributes['isRoot'] = 'false'
        attributes['isLeaf'] = 'false'
        attributes['isAbstract'] = 'false'
        xmi.startElement('UML:Model', attrs=attributes)
        xmi.startElement('UML:Namespace.ownedElement', attrs=XMLAttributes())
        for element in gaphor.resource('ElementFactory').select():
            #print element.__class__.__name__
            try:
                handler=getattr(self, 'handle%s'%element.__class__.__name__)
            except AttributeError:
                print element.__class__.__name__
                continue
            handler(xmi, element)
        xmi.endElement('UML:Namespace.ownedElement')    
        xmi.endElement('UML:Model')
        xmi.endElement('XMI.content')

