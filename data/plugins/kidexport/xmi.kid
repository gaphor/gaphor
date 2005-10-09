<?xml version = '1.0' encoding = 'UTF-8' ?>

<?python
import gaphor
import time


elements = gaphor.resource('ElementFactory').select()

topLevelPackage = [element for element in elements if not getattr(element, 'package', True)][0]

def modelProcessNode(node):
    className = type(node).__name__
    try:
        return eval("process%s(node)"%className, globals(), locals())
    except NameError:
        return ''
    
def getPackageChildNodes(package):
    return [node for node in gaphor.resource('ElementFactory').select() if 
            hasattr(node, 'package') and node.package==package]
            
def getLowerAndUpperValuesFromAssociationEnd(end):
    values=('lower','upper')
    attributes = {}
    for value in values:
        try:
            data=getattr(end, '%sValue'%value).value
        except AttributeError:
            data='1' # FIXME!
        if str(data)=='*':
            attributes['lower']='0'
            attributes['upper']='-1'
            return attributes
        elif data is None:
            data='1'
        attributes[value]=data
    return attributes
?>

<XMI
  xmlns:py="http://purl.org/kid/ns#"
  xmi.version = '1.2' xmlns:UML = 'org.omg.xmi.namespace.UML' xmlns:UML2 = 'org.omg.xmi.namespace.UML2'
  timestamp = 'Sun Oct 09 09:01:33 CEST 2005' py:attrs="timestamp=time.strftime('%a %b %d %H:%M:%S %Z %Y')">
  
  <XMI.header><XMI.documentation>
    <XMI.exporter>Gaphor Kid XMI Writer</XMI.exporter>
    <XMI.exporterVersion>0.1</XMI.exporterVersion>
    <XMI.metaModelVersion>1.4.2</XMI.metaModelVersion></XMI.documentation>
  </XMI.header>
  <XMI.content>
  
    <UML:Model 
      xmi.id = 'I48de81cbm106d41f950cmm7f54' name = 'topModel' isSpecification = 'false'
      isRoot = 'false' isLeaf = 'false' isAbstract = 'false'
      py:attrs="{'xmi.id':topLevelPackage.id, 'name':topLevelPackage.name}">
      
      <UML:Classifier.feature py:def="processClassifierFeature(item)">

        <UML:Attribute xmi.id = 'I48de81cbm106d41f950cmm7f35' name = 'someAttribute'
          visibility = 'private' isSpecification = 'false' ownerScope = 'instance'
          changeability = 'changeable'
          py:for="attribute in [a for a in item.ownedAttribute if a.typeValue]"
          py:attrs="{'xmi.id':attribute.id, 'name':attribute.name}">
          <UML:StructuralFeature.type>
            <UML:Class xmi.idref = 'I48de81cbm106d41f950cmm7f24'
              py:attrs="{'xmi.id':attribute.typeValue.id}"/>
          </UML:StructuralFeature.type>
        </UML:Attribute>
        
        <UML:Operation xmi.id = 'I48de81cbm106d41f950cmm7f11' name = 'someMethod'
          visibility = 'public' isSpecification = 'false' ownerScope = 'instance'
          isQuery = 'false' concurrency = 'sequential' isRoot = 'false' isLeaf = 'false'
          isAbstract = 'false'
          py:for="operation in item.ownedOperation"
          py:attrs="{'xmi.id':operation.id, 'name':operation.name}">
          <UML:BehavioralFeature.parameter>
            <UML:Parameter xmi.id = 'I48de81cbm106d41f950cmm7ee1' name = 'return' isSpecification = 'false'
              kind = 'return'
              py:for="parameter in operation.formalParameter"
              py:attrs="{'xmi.id':parameter.id, 'name':parameter.name, 'kind':parameter.kind}">
              <UML:Parameter.type>
                <UML:DataType xmi.idref = 'I48de81cbm106d41f950cmm7f36'
                  py:attrs="{'xmi.idref':parameter.typeValue.id}"/>
              </UML:Parameter.type>
            </UML:Parameter>
          </UML:BehavioralFeature.parameter>
        </UML:Operation>
        
        <UML:Method xmi.id = 'I48de81cbm106d41f950cmm7f0f' isSpecification = 'false'
          isQuery = 'false'>
          <UML:Method.body>
            <UML:ProcedureExpression xmi.id = 'I48de81cbm106d41f950cmm7f10' language = 'java'
              body = ''/>
          </UML:Method.body>
          <UML:Method.specification>
            <UML:Operation xmi.idref = 'I48de81cbm106d41f950cmm7f11'/>
          </UML:Method.specification>
        </UML:Method>
        
      </UML:Classifier.feature>

      <UML:Abstraction py:def="processImplementation(abstraction)"
        xmi.id = 'I48de81cbm106d41f950cmm7e5d' isSpecification = 'false'
        py:attrs="{'xmi.id':abstraction.id}">
          <UML:Dependency.client>
            <UML:Class xmi.idref = 'I48de81cbm106d41f950cmm7ead'
              py:for="client in abstraction.client"
              py:attrs="{'xmi.idref':client.id}"/>
          </UML:Dependency.client>
          <UML:Dependency.supplier>
            <UML:Interface xmi.idref = 'I48de81cbm106d41f950cmm7e73'
              py:for="supplier in abstraction.supplier"
              py:attrs="{'xmi.idref':supplier.id}"/>
          </UML:Dependency.supplier>
        </UML:Abstraction>

      <UML:Generalization py:def="processGeneralization(generalization)"
        xmi.id = 'I48de81cbm106d41f950cmm7eb4' isSpecification = 'false'
        py:attrs="{'xmi.id':generalization.id}">
        <UML:Generalization.child>
          <UML:Class xmi.idref = 'I48de81cbm106d41f950cmm7ec7' 
            py:attrs="{'xmi.idref':generalization.specific.id}"/>
        </UML:Generalization.child>
        <UML:Generalization.parent>
          <UML:Class xmi.idref = 'I48de81cbm106d41f950cmm7f4c'
            py:attrs="{'xmi.idref':generalization.general.id}"/>
        </UML:Generalization.parent>
      </UML:Generalization>
      
      <UML:Interface py:def="processInterface(interface)"
        xmi.id = 'I48de81cbm106d41f950cmm7e73' name = 'SomeInterface'
        visibility = 'public' isSpecification = 'false' isRoot = 'false' isLeaf = 'false'
        isAbstract = 'false'
        py:attrs="{'xmi.id':interface.id, 'name':interface.name}">
        <UML:Classifier.feature py:replace="processClassifierFeature(interface)"/>
      </UML:Interface>
    
      <UML:Class py:def="processClass(cls)"
        py:if="cls.name not in ('Class','Interface','Package')"
        xmi.id = 'I48de81cbm106d41f950cmm7f4c' name = 'AbstractBaseClass'
        visibility = 'public' isSpecification = 'false' isRoot = 'false' isLeaf = 'false'
        isAbstract = 'true' isActive = 'false'
        py:attrs="{'xmi.id':cls.id, 'name':cls.name, 
                   'isAbstract':cls.isAbstract and 'true' or 'false'}">

        <UML:ModelElement.stereotype py:if="cls.appliedStereotype">
          <UML:Stereotype xmi.idref = 'I48de81cbm106d41f950cmm7e0c'
            py:for="stereotype in cls.appliedStereotype"/>
        </UML:ModelElement.stereotype>

        <UML:ModelElement.clientDependency py:if="cls.supplierDependency">
            <UML:Abstraction xmi.idref = 'I48de81cbm106d41f950cmm7e5d'
              py:for="interface in cls.supplierDependency"
              py:attrs="{'xmi.idref':interface.id}"/>
        </UML:ModelElement.clientDependency>

        <UML:GeneralizableElement.generalization py:if="cls.generalization">
          <UML:Generalization xmi.idref = 'I48de81cbm106d41f950cmm7eb4'
            py:for="generalization in cls.generalization"
            py:attrs="{'xmi.idref':generalization.id}"/>
        </UML:GeneralizableElement.generalization>

        <UML:Classifier.feature py:replace="processClassifierFeature(cls)"/>
      </UML:Class>

      <UML:Stereotype py:def="processStereotype(stereotype)"
        xmi.id = 'I48de81cbm106d41f950cmm7e0c' name = 'stereotypeTest'
          visibility = 'public' isSpecification = 'false' isRoot = 'false' isLeaf = 'false'
          isAbstract = 'false'
          py:attrs="{'xml.id':stereotype.id, 'name':stereotype.name}">
        <UML:Stereotype.baseClass py:content="stereotype.ownedAttribute.type.name">Class</UML:Stereotype.baseClass>
      </UML:Stereotype>
      
      <UML:Package py:def="processPackage(package)"
        xmi.id = 'I48de81cbm106d41f950cmm7e01' name = 'aPackage' visibility = 'public'
          isSpecification = 'false' isRoot = 'false' isLeaf = 'false' isAbstract = 'false'
          py:attrs="{'xmi.idref':package.id, 'name':package.name}">
        <UML:Namespace.ownedElement>
          <packageContent py:for="item in getPackageChildNodes(package=package)" 
            py:replace="modelProcessNode(item)"/>
        </UML:Namespace.ownedElement>
      </UML:Package>
      

      <UML:Association py:def="processAssociation(association)" 
        py:if="len(association.memberEnd)==2"
        xmi.id = 'I48de81cbm106d41f950cmm7d2f' isSpecification = 'false'
        isRoot = 'false' isLeaf = 'false' isAbstract = 'false'
        py:attrs="{'xmi.id':association.id, 'name':association.name}">
        <UML:Association.connection>
          <UML:AssociationEnd xmi.id = 'I48de81cbm106d41f950cmm7d35' visibility = 'public'
            isSpecification = 'false' isNavigable = 'false' ordering = 'unordered' aggregation = 'none'
            targetScope = 'instance' changeability = 'changeable'
            py:for="(i,end) in enumerate(association.memberEnd)"
            py:attrs="{'xmi.id':end.id, 'isNavigable': end.class_ and 'true' or 'false',
                       'aggregation':association.memberEnd[1-i]}">
            <UML:AssociationEnd.multiplicity>
              <UML:Multiplicity xmi.id = 'I48de81cbm106d41f950cmm7d33'
                py:attrs="{'xmi.id':end.id+'_%s'%i}">
                <UML:Multiplicity.range>
                  <UML:MultiplicityRange xmi.id = 'I48de81cbm106d41f950cmm7d34' lower = '1'
                    upper = '1'
                    py:attrs="{'xmi.id':end.id+'_range_%s'%i,
                               'lower':getLowerAndUpperValuesFromAssociationEnd(end)['lower'],
                               'upper':getLowerAndUpperValuesFromAssociationEnd(end)['upper']}"/>
                </UML:Multiplicity.range>
              </UML:Multiplicity>
            </UML:AssociationEnd.multiplicity>
            <UML:AssociationEnd.participant>
              <UML:Class xmi.idref = 'I48de81cbm106d41f950cmm7ddb'
                py:attrs="{'xmi.idref':end.type.id}"/>
            </UML:AssociationEnd.participant>
          </UML:AssociationEnd>
        </UML:Association.connection>
      </UML:Association>
    
      <UML:Namespace.ownedElement>
        <packageContent py:for="item in getPackageChildNodes(package=topLevelPackage)" 
          py:replace="modelProcessNode(item)"/>  
        
        
      
        <UML:Class xmi.id = 'I48de81cbm106d41f950cmm7cb9' name = 'ClassWithWorkflow'
          visibility = 'public' isSpecification = 'false' isRoot = 'false' isLeaf = 'false'
          isAbstract = 'false' isActive = 'false'>
          <UML2:BehavioredClassifier.ownedBehavior>
            <UML2:StateMachine xmi.id = 'I48de81cbm106d41f950cmm7ca6' name = 'State_Machine_1'
              visibility = 'public' isSpecification = 'false' isRoot = 'false' isLeaf = 'false'
              isAbstract = 'false' isActive = 'false'>
              <UML2:StateMachine.region>
                <UML2:Region xmi.id = 'I48de81cbm106d41f950cmm7ca5' name = 'TopRegion_1'
                  visibility = 'public' isSpecification = 'false'>
                  <UML2:Region.subvertex>
                    <UML2:Pseudostate xmi.id = 'I48de81cbm106d41f950cmm7c9d' name = 'start'
                      visibility = 'public' isSpecification = 'false' kind = 'initial'>
                      <UML2:Vertex.outgoing>
                        <UML2:Transition xmi.idref = 'I48de81cbm106d41f950cmm7c8d'/>
                      </UML2:Vertex.outgoing>
                    </UML2:Pseudostate>
                    <UML2:State xmi.id = 'I48de81cbm106d41f950cmm7c98' name = 'middle' visibility = 'public'
                      isSpecification = 'false'>
                      <UML2:Vertex.incoming>
                        <UML2:Transition xmi.idref = 'I48de81cbm106d41f950cmm7c8d'/>
                      </UML2:Vertex.incoming>
                    </UML2:State>
                  </UML2:Region.subvertex>
                  <UML2:Region.transition>
                    <UML2:Transition xmi.id = 'I48de81cbm106d41f950cmm7c8d' name = 'gotoMiddle'
                      visibility = 'public' isSpecification = 'false' kind = 'external'>
                      <UML2:Transition.source>
                        <UML2:Pseudostate xmi.idref = 'I48de81cbm106d41f950cmm7c9d'/>
                      </UML2:Transition.source>
                      <UML2:Transition.target>
                        <UML2:State xmi.idref = 'I48de81cbm106d41f950cmm7c98'/>
                      </UML2:Transition.target>
                    </UML2:Transition>
                  </UML2:Region.transition>
                </UML2:Region>
              </UML2:StateMachine.region>
            </UML2:StateMachine>
          </UML2:BehavioredClassifier.ownedBehavior>
        </UML:Class>
      </UML:Namespace.ownedElement>
    </UML:Model>
  </XMI.content>
</XMI>