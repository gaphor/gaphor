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


class Requirement(AbstractRequirement):
    pass


class AbstractRequirement:
    pass


class Trace(DirectedRelationshipPropertyPath):
    pass


class Copy(Trace):
    pass


class Verify(Trace):
    pass


class DeriveReqt(Trace):
    pass


class Satisfy(Trace):
    pass


class TestCase:
    pass


class Block:
    pass


class ConnectorProperty:
    pass


class ParticipantProperty:
    pass


class DistributedProperty:
    pass


class ValueType:
    pass


class ElementPropertyPath:
    pass


class DirectedRelationshipPropertyPath:
    pass


class BindingConnector:
    pass


class NestedConnectorEnd(ElementPropertyPath):
    pass


class PropertySpecificType:
    pass


class EndPathMultiplicity:
    pass


class BoundReference(EndPathMultiplicity):
    pass


class AdjuntProperty:
    pass


class ClassifierBehaviorProperty:
    pass


class ProxyPort:
    pass


class FullPort:
    pass


class FlowProperty:
    pass


class InterfaceBlock(Block):
    pass


class AddStructuralFeatureValueAction:
    pass


class InvocationOnNestedPortAction(ElementPropertyPath):
    pass


class TriggerOnNestedPort(ElementPropertyPath):
    pass


class AddFlowPropertyValueOnNestedPortAction(ElementPropertyPath):
    pass


class ChangeEvent:
    pass


class ChangeSructuralFeatureEvent:
    pass


class AcceptChangeStructuralFeatureEventAction:
    pass


class DirectedFeature:
    pass


class Conform:
    pass


class View:
    pass


class Viewpoint:
    pass


class Stakeholder:
    pass


class Expose:
    pass


class Rationale:
    pass


class Problem:
    pass


class ElementGroup:
    pass


class ConstraintBlock(Block):
    pass


class ParameterSet:
    pass


class Rate:
    pass


class Probability:
    pass


class Continuous(Rate):
    pass


class Discrete(Rate):
    pass


class ControlOperator:
    pass


class NoBuffer:
    pass


class Overwrite:
    pass


class Allocate(DirectedRelationshipPropertyPath):
    pass


class AllocateActivityPartition:
    pass


class Refine:
    pass


class Tagged:
    pass
