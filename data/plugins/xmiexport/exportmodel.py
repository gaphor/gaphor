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
        attributes['name']='XMLTool' # TODO
        attributes['visibility']='public' # TODO
        attributes['isSpecification']='false'
        attributes['isRoot']='false'
        attributes['isLeaf']='false'
        attributes['isAbstract']='false'
        attributes['isActive']='false'
        xmi.startElement('UML:Class', attrs=attributes)
        for attribute in node.:
            xmi.startElement('UML:Classifier.feature', attrs=XMLAttributes())
            attributes=XMLAttributes()
            attributes['xmi.id']=attribute.id
            attributes['name']=
            attributes['visibility']=
            attributes['isSpecification']='false'
            attributes['ownerScope']='instance'
            attributes['changeability']='changeable'
            xmi.startElement('UML:Attribute', attrs=attributes)
            
            xmi.startElement('UML:StructuralFeature.type', XMLAttributes())
            xmi.startElement('UML:Class', XMLAttributes({'xmi.idref': 'bla'}))
            xmi.endElement('UML:Class')
            xmi.endElement('UML:StructuralFeature.type')
                        
            xmi.endElement('UML:Attribute')
            
            xmi.endElement('UML:Classifier.feature')
        xmi.endElement('UML:Class')
        
    def handleAssociation(self, xmi, node):
        """
        """
        ends=node.memberEnd
        
        attributes=XMLAttributes()
        attributes['xmi.id']=node.id
        attributes['isSpecification']='false'
        attributes['isRoot']='false'
        attributes['isLeaf']='false'
        attributes['isAbstract']='false'
        xmi.startElement('UML:Association', attrs=attributes)
        xmi.startElement('UML:Association.connection', attrs=XMLAttributes())
        for end in node.memberEnd:
            attributes=XMLAttributes()
            attributes['xmi.id']=end.id
            attributes['visibility']='public'
            attributes['isSpecification']='false'
            attributes['isNavigable']='true'
            attributes['ordering']='unordered'
            attributes['aggregation']=end.aggregation # TODO: Handle None?
            attributes['targetScope']='instance' 
            attributes['changeability']='changeable'
            xmi.startElement('UML:AssociationEnd', attrs=attributes)
            xmi.startElement('UML:AssociationEnd.multiplicity', attrs=XMLAttributes())
            attributes=XMLAttributes()
            attributes['xmi.id']='sm$f14318:ff442f5793:-7f6d'
            xmi.startElement('UML:Multiplicity', attrs=attributes)
            xmi.startElement('UML:Multiplicity.range', attrs=XMLAttributes())
            attributes=XMLAttributes()
            attributes['xmi.id']='bla'
            values=('lower','upper')
            for value in values:
                try:
                    data=getattr(end, '%sValue'%value).value
                except AttributeError:
                    data='1' # FIXME!
                if data is None:
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
            
            
    def exportModel(self):
        out=open('/Users/vloothuis/test.xmi','w')
        xmi=XMLGenerator(out)
        
        # Start XML generation
        attributes=XMLAttributes()
        attributes['xmi.version']='1.2'
        attributes['xmlns:UML']='org.omg.xmi.namespace.UML'
        attributes['timestamp']='Tue Sep 28 10:48:06 CEST 2004' # TODO!
        xmi.startElement('XMI', attrs=attributes)
        
        # Writer XMI header section
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
        
        
        # Now generator the model
        xmi.startElement('XMI.content', attrs=XMLAttributes())
        # TODO: Add diagram stuff here
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
            print element.__class__.__name__
            try:
                handler=getattr(self, 'handle%s'%element.__class__.__name__)
            except AttributeError:
                continue
            handler(xmi, element)
        xmi.endElement('UML:Namespace.ownedElement')    
        xmi.endElement('UML:Model')
        xmi.endElement('XMI.content')
        
        xmi.endElement('XMI')
        
        handlers={}

    def execute(self):
        self.exportModel()
    