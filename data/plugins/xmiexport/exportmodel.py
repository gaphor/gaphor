# vim:sw=4:et

from xml.sax.saxutils import XMLGenerator
import gaphor
from gaphor import UML
from gaphor.plugin import Action

try:
    dict()
except:
    from UserDict import UserDict as dict
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

class XMIExport(Action):

    def handleClass(self, xmi, node):
        """ """    
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
        try:
            node.generalization
            hasGeneralization=True
        except AttributeError:
            hasGeneralization=False

        if hasGeneralization:
            xmi.startElement('UML:GeneralizableElement.generalization', attrs=XMLAttributes())
            for item in node.generalization:
                attributes=XMLAttributes()
                attributes['xmi.idref']=item.id
                xmi.startElement('UML:Generalization', attrs=attributes)
                xmi.endElement('UML:Generalization')
            xmi.endElement('UML:GeneralizableElement.generalization')
        
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

        # Now generate the XML for the attribute itself
        for attribute in node.ownedAttribute:
            try:
                attribute.name
                attribute.typeValue.value
            except AttributeError:
                continue

            xmi.startElement('UML:Classifier.feature', attrs=XMLAttributes())
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
            
            xmi.endElement('UML:Classifier.feature')
        xmi.endElement('UML:Class')


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
        
    def handleLiteralSpecification(self, xmi, node):
        pass
        
    def handleAssociation(self, xmi, node):
        """
        """
        ends=node.memberEnd
        if len(ends)!=2:
            return
        
        # Temp fix for line direction
        end_sequence = [0,1]
        if ends[1].aggregation=='composite':
            end_sequence = [0,1]
        else:
            end_sequence = [1,0]
        if ends[1].class_:
            end_sequence.reverse()

        attributes=XMLAttributes()
        attributes['xmi.id']=node.id
        attributes['isSpecification']='false'
        attributes['isRoot']='false'
        attributes['isLeaf']='false'
        attributes['isAbstract']='false'
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
            
            
    def export(self):
        out=open('/Users/vloothuis/test.xmi','w')
        xmi=XMLGenerator(out)
        
        # Start XML generation
        attributes=XMLAttributes()
        attributes['xmi.version']='1.2'
        attributes['xmlns:UML']='org.omg.xmi.namespace.UML'
        attributes['timestamp']='Tue Sep 28 10:48:06 CEST 2004' # TODO!
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
                continue
            handler(xmi, element)
        xmi.endElement('UML:Namespace.ownedElement')    
        xmi.endElement('UML:Model')
        xmi.endElement('XMI.content')

    def execute(self):
        self.export()
    
