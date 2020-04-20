from gaphor.core.modeling.properties import association, attribute
from gaphor.UML import (
    Abstraction,
    AcceptEventAction,
    ActivityEdge,
    ActivityPartition,
    Behavior,
    Class,
    Classifier,
    Comment,
    Connector,
    ConnectorEnd,
    DataType,
    Dependency,
    DirectedRelationship,
    Element,
    Feature,
    Generalization,
    InstanceSpecification,
    InvocationAction,
    NamedElement,
    ObjectNode,
    Operation,
    Optional,
    Parameter,
    Port,
    Property,
    StructuralFeature,
    Trigger,
)


class AbstractRequirement:
    derived: attribute[AbstractRequirement]
    tracedTo: attribute[NamedElement]
    id: attribute[str]
    verifiedBy: attribute[NamedElement]
    master: attribute[AbstractRequirement]
    refinedBy: attribute[NamedElement]
    base_NamedElement: attribute[NamedElement]
    satisfiedBy: attribute[NamedElement]
    text: attribute[str]
    baseClass: association


class TestCase:
    baseClass: association


class Block:
    isEncapsulated: attribute[int]
    baseClass: association


class ConnectorProperty:
    connector: attribute[Connector]
    baseClass: association


class ParticipantProperty:
    end: attribute[Property]
    baseClass: association


class DistributedProperty:
    baseClass: association


class ValueType:
    baseClass: association
    unit: association


class ElementPropertyPath:
    baseClass: association
    propertyPath: association


class DirectedRelationshipPropertyPath:
    baseClass: association
    targetContext: association
    sourceContext: association


class BindingConnector:
    baseClass: association


class PropertySpecificType:
    baseClass: association


class EndPathMultiplicity:
    upper: attribute[int]
    lower: attribute[int]
    baseClass: association


class AdjuntProperty:
    baseClass: association
    principal: association


class ClassifierBehaviorProperty:
    pass


class ProxyPort:
    baseClass: association


class FullPort:
    baseClass: association


class FlowProperty:
    direction: attribute
    baseClass: association


class AddStructuralFeatureValueAction:
    pass


class ChangeEvent:
    pass


class ChangeSructuralFeatureEvent:
    baseClass: association
    structuralFeature: association


class AcceptChangeStructuralFeatureEventAction:
    baseClass: association


class DirectedFeature:
    featureDirection: attribute
    baseClass: association


class Conform:
    baseClass: association


class View:
    viewpoint: attribute[Viewpoint]
    stakeholder: attribute[Stakeholder]
    baseClass: association


class Viewpoint:
    method: attribute[Behavior]
    presentation: attribute[str]
    purpose: attribute[str]
    concern: attribute[str]
    stakeholder: attribute[Stakeholder]
    concernList: attribute[Comment]
    language: attribute[str]
    baseClass: association


class Stakeholder:
    concern: attribute[str]
    concernList: attribute[Comment]
    baseClass: association


class Expose:
    baseClass: association


class Rationale:
    baseClass: association


class Problem:
    baseClass: association


class ElementGroup:
    criterion: attribute[str]
    member: attribute[Element]
    name: attribute[str]
    orderedMember: attribute[Element]
    size: attribute[int]
    baseClass: association


class ParameterSet:
    pass


class Rate:
    rate: attribute[InstanceSpecification]
    baseClass: association


class Probability:
    probability: attribute
    baseClass: association


class ControlOperator:
    baseClass: association


class NoBuffer:
    baseClass: association


class Overwrite:
    baseClass: association


class AllocateActivityPartition:
    baseClass: association


class Trace:
    pass


class Refine:
    pass


class Tagged:
    nonunique: attribute[bool]
    ordered: attribute[bool]
    subsets: attribute[str]
    baseClass: association


class Requirement(AbstractRequirement):
    baseClass: association


class Copy(Trace):
    pass


class Verify(Trace):
    pass


class DeriveReqt(Trace):
    pass


class Satisfy(Trace):
    pass


class NestedConnectorEnd(ElementPropertyPath):
    baseClass: association


class BoundReference(EndPathMultiplicity):
    bindingPath: attribute[Property]
    boundend: attribute[ConnectorEnd]


class InterfaceBlock(Block):
    pass


class InvocationOnNestedPortAction(ElementPropertyPath):
    onNestedPort: association
    baseClass: association


class TriggerOnNestedPort(ElementPropertyPath):
    baseClass: association
    onNestedPort: association


class AddFlowPropertyValueOnNestedPortAction(ElementPropertyPath):
    baseClass: association


class ConstraintBlock(Block):
    pass


class Continuous(Rate):
    pass


class Discrete(Rate):
    pass


class Allocate(DirectedRelationshipPropertyPath):
    baseClass: association
