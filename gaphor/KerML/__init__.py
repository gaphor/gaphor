from gaphor.KerML.kerml import (
    eClassifiers,
    LiteralString,
    EndFeatureMembership,
    Structure,
    Class,
    DataType,
    LibraryPackage,
    LiteralExpression,
    LiteralRational,
    LiteralInteger,
    SelectExpression,
    CollectExpression,
    LiteralBoolean,
    NullExpression,
    LiteralInfinity,
    AssociationStructure,
    Invariant,
    ReturnParameterMembership,
    SuccessionItemFlow,
    BindingConnector,
    Comment,
)
from gaphor.KerML.kerml import eClass
from gaphor.KerML.kerml import (
    Dependency,
    Relationship,
    Element,
    OwningMembership,
    Membership,
    Namespace,
    Import,
    VisibilityKind,
    Documentation,
    AnnotatingElement,
    Annotation,
    TextualRepresentation,
    NamespaceImport,
    MembershipImport,
    Subclassification,
    Specialization,
    Type,
    FeatureMembership,
    Featuring,
    Feature,
    Redefinition,
    Subsetting,
    FeatureTyping,
    TypeFeaturing,
    FeatureInverting,
    FeatureChaining,
    FeatureDirectionKind,
    ReferenceSubsetting,
    Conjugation,
    Multiplicity,
    Intersecting,
    Unioning,
    Disjoining,
    Differencing,
    Classifier,
    Package,
    Expression,
    Step,
    Behavior,
    Function,
    ElementFilterMembership,
    FeatureReferenceExpression,
    InvocationExpression,
    OperatorExpression,
    FeatureChainExpression,
    MetadataAccessExpression,
    MetadataFeature,
    Metaclass,
    ParameterMembership,
    FeatureValue,
    Association,
    BooleanExpression,
    Predicate,
    ResultExpressionMembership,
    ItemFlow,
    Connector,
    ItemFlowEnd,
    ItemFeature,
    Interaction,
    Succession,
    MultiplicityRange,
)

from gaphor.KerML import kerml

__all__ = [
    "Dependency",
    "Relationship",
    "Element",
    "OwningMembership",
    "Membership",
    "Namespace",
    "Import",
    "VisibilityKind",
    "Documentation",
    "Comment",
    "AnnotatingElement",
    "Annotation",
    "TextualRepresentation",
    "NamespaceImport",
    "MembershipImport",
    "Subclassification",
    "Specialization",
    "Type",
    "FeatureMembership",
    "Featuring",
    "Feature",
    "Redefinition",
    "Subsetting",
    "FeatureTyping",
    "TypeFeaturing",
    "FeatureInverting",
    "FeatureChaining",
    "FeatureDirectionKind",
    "ReferenceSubsetting",
    "Conjugation",
    "Multiplicity",
    "Intersecting",
    "Unioning",
    "Disjoining",
    "Differencing",
    "Classifier",
    "EndFeatureMembership",
    "Structure",
    "Class",
    "DataType",
    "LibraryPackage",
    "Package",
    "Expression",
    "Step",
    "Behavior",
    "Function",
    "ElementFilterMembership",
    "LiteralString",
    "LiteralExpression",
    "LiteralRational",
    "FeatureReferenceExpression",
    "LiteralInteger",
    "InvocationExpression",
    "SelectExpression",
    "OperatorExpression",
    "CollectExpression",
    "LiteralBoolean",
    "NullExpression",
    "LiteralInfinity",
    "FeatureChainExpression",
    "MetadataAccessExpression",
    "MetadataFeature",
    "Metaclass",
    "ParameterMembership",
    "FeatureValue",
    "Association",
    "AssociationStructure",
    "BooleanExpression",
    "Predicate",
    "ResultExpressionMembership",
    "Invariant",
    "ReturnParameterMembership",
    "ItemFlow",
    "Connector",
    "ItemFlowEnd",
    "ItemFeature",
    "Interaction",
    "SuccessionItemFlow",
    "Succession",
    "BindingConnector",
    "MultiplicityRange",
]

Dependency.client.eType = Element
Dependency.supplier.eType = Element
Relationship.relatedElement.eType = Element
Relationship.target.eType = Element
Relationship.source.eType = Element
Membership.memberElement.eType = Element
Namespace.membership.eType = Membership
Namespace.member.eType = Element
Namespace.importedMembership.eType = Membership
Import._importedElement.eType = Element
AnnotatingElement.annotatedElement.eType = Element
Annotation.annotatedElement.eType = Element
NamespaceImport.importedNamespace.eType = Namespace
MembershipImport.importedMembership.eType = Membership
Subclassification.superclassifier.eType = Classifier
Subclassification.subclassifier.eType = Classifier
Specialization.general.eType = Type
Specialization.specific.eType = Type
Type.feature.eType = Feature
Type.input.eType = Feature
Type.output.eType = Feature
Type.inheritedMembership.eType = Membership
Type.endFeature.eType = Feature
Type.inheritedFeature.eType = Feature
Type._multiplicity.eType = Multiplicity
Type.unioningType.eType = Type
Type.intersectingType.eType = Type
Type.featureMembership.eType = FeatureMembership
Type.differencingType.eType = Type
Type.directedFeature.eType = Feature
Featuring.type.eType = Type
Featuring.feature.eType = Feature
Feature.type.eType = Type
Feature.ownedRedefinition.eType = Redefinition
Feature.featuringType.eType = Type
Feature.chainingFeature.eType = Feature
Redefinition.redefiningFeature.eType = Feature
Redefinition.redefinedFeature.eType = Feature
Subsetting.subsettedFeature.eType = Feature
Subsetting.subsettingFeature.eType = Feature
FeatureTyping.typedFeature.eType = Feature
FeatureTyping.type.eType = Type
TypeFeaturing.featureOfType.eType = Feature
TypeFeaturing.featuringType.eType = Type
FeatureInverting.featureInverted.eType = Feature
FeatureInverting.invertingFeature.eType = Feature
FeatureChaining.chainingFeature.eType = Feature
ReferenceSubsetting.referencedFeature.eType = Feature
Conjugation.originalType.eType = Type
Conjugation.conjugatedType.eType = Type
Intersecting.intersectingType.eType = Type
Unioning.unioningType.eType = Type
Disjoining.typeDisjoined.eType = Type
Disjoining.disjoiningType.eType = Type
Differencing.differencingType.eType = Type
Package.filterCondition.eType = Expression
Expression._function.eType = Function
Expression._result.eType = Feature
Step.behavior.eType = Behavior
Step.parameter.eType = Feature
Behavior.step.eType = Step
Behavior.parameter.eType = Feature
Function.expression.eType = Expression
Function._result.eType = Feature
ElementFilterMembership._condition.eType = Expression
FeatureReferenceExpression._referent.eType = Feature
InvocationExpression.argument.eType = Expression
OperatorExpression.operand.eType = Expression
FeatureChainExpression._targetFeature.eType = Feature
MetadataAccessExpression.referencedElement.eType = Element
MetadataFeature._metaclass.eType = Metaclass
ParameterMembership._ownedMemberParameter.eType = Feature
FeatureValue._featureWithValue.eType = Feature
FeatureValue._value.eType = Expression
Association.relatedType.eType = Type
Association._sourceType.eType = Type
Association.targetType.eType = Type
Association.associationEnd.eType = Feature
BooleanExpression._predicate.eType = Predicate
ResultExpressionMembership._ownedResultExpression.eType = Expression
ItemFlow.itemType.eType = Classifier
ItemFlow._targetInputFeature.eType = Feature
ItemFlow._sourceOutputFeature.eType = Feature
ItemFlow.itemFlowEnd.eType = ItemFlowEnd
ItemFlow._itemFeature.eType = ItemFeature
ItemFlow.interaction.eType = Interaction
Connector.relatedFeature.eType = Feature
Connector.association.eType = Association
Connector.connectorEnd.eType = Feature
Connector._sourceFeature.eType = Feature
Connector.targetFeature.eType = Feature
Succession._transitionStep.eType = Step
Succession.triggerStep.eType = Step
Succession.effectStep.eType = Step
Succession.guardExpression.eType = Expression
MultiplicityRange._lowerBound.eType = Expression
MultiplicityRange._upperBound.eType = Expression
MultiplicityRange.bound.eType = Expression
Relationship.ownedRelatedElement.eType = Element
Relationship.owningRelatedElement.eType = Element
Element._owningMembership.eType = OwningMembership
Element._owningNamespace.eType = Namespace
Element.owningRelationship.eType = Relationship
Element.owningRelationship.eOpposite = Relationship.ownedRelatedElement
Element.ownedRelationship.eType = Relationship
Element.ownedRelationship.eOpposite = Relationship.owningRelatedElement
Element._owner.eType = Element
Element.ownedElement.eType = Element
Element.ownedElement.eOpposite = Element._owner
Element.documentation.eType = Documentation
Element.ownedAnnotation.eType = Annotation
Element.textualRepresentation.eType = TextualRepresentation
OwningMembership._ownedMemberElement.eType = Element
OwningMembership._ownedMemberElement.eOpposite = Element._owningMembership
Membership._membershipOwningNamespace.eType = Namespace
Namespace.ownedImport.eType = Import
Namespace.ownedMember.eType = Element
Namespace.ownedMember.eOpposite = Element._owningNamespace
Namespace.ownedMembership.eType = Membership
Namespace.ownedMembership.eOpposite = Membership._membershipOwningNamespace
Import._importOwningNamespace.eType = Namespace
Import._importOwningNamespace.eOpposite = Namespace.ownedImport
Documentation._documentedElement.eType = Element
Documentation._documentedElement.eOpposite = Element.documentation
AnnotatingElement.annotation.eType = Annotation
Annotation._owningAnnotatedElement.eType = Element
Annotation._owningAnnotatedElement.eOpposite = Element.ownedAnnotation
Annotation.annotatingElement.eType = AnnotatingElement
Annotation.annotatingElement.eOpposite = AnnotatingElement.annotation
TextualRepresentation._representedElement.eType = Element
TextualRepresentation._representedElement.eOpposite = Element.textualRepresentation
Subclassification._owningClassifier.eType = Classifier
Specialization._owningType.eType = Type
Type.ownedFeatureMembership.eType = FeatureMembership
Type.ownedFeature.eType = Feature
Type.ownedEndFeature.eType = Feature
Type._ownedConjugator.eType = Conjugation
Type.ownedIntersecting.eType = Intersecting
Type.ownedUnioning.eType = Unioning
Type.ownedDisjoining.eType = Disjoining
Type.ownedDifferencing.eType = Differencing
Type.ownedSpecialization.eType = Specialization
Type.ownedSpecialization.eOpposite = Specialization._owningType
FeatureMembership._ownedMemberFeature.eType = Feature
FeatureMembership._owningType.eType = Type
FeatureMembership._owningType.eOpposite = Type.ownedFeatureMembership
Feature._owningType.eType = Type
Feature._owningType.eOpposite = Type.ownedFeature
Feature.ownedSubsetting.eType = Subsetting
Feature._owningFeatureMembership.eType = FeatureMembership
Feature._owningFeatureMembership.eOpposite = FeatureMembership._ownedMemberFeature
Feature._endOwningType.eType = Type
Feature._endOwningType.eOpposite = Type.ownedEndFeature
Feature.ownedTyping.eType = FeatureTyping
Feature.ownedTypeFeaturing.eType = TypeFeaturing
Feature.ownedFeatureInverting.eType = FeatureInverting
Feature.ownedFeatureChaining.eType = FeatureChaining
Feature._ownedReferenceSubsetting.eType = ReferenceSubsetting
Subsetting._owningFeature.eType = Feature
Subsetting._owningFeature.eOpposite = Feature.ownedSubsetting
FeatureTyping._owningFeature.eType = Feature
FeatureTyping._owningFeature.eOpposite = Feature.ownedTyping
TypeFeaturing._owningFeatureOfType.eType = Feature
TypeFeaturing._owningFeatureOfType.eOpposite = Feature.ownedTypeFeaturing
FeatureInverting._owningFeature.eType = Feature
FeatureInverting._owningFeature.eOpposite = Feature.ownedFeatureInverting
FeatureChaining._featureChained.eType = Feature
FeatureChaining._featureChained.eOpposite = Feature.ownedFeatureChaining
ReferenceSubsetting._referencingFeature.eType = Feature
ReferenceSubsetting._referencingFeature.eOpposite = Feature._ownedReferenceSubsetting
Conjugation._owningType.eType = Type
Conjugation._owningType.eOpposite = Type._ownedConjugator
Intersecting._typeIntersected.eType = Type
Intersecting._typeIntersected.eOpposite = Type.ownedIntersecting
Unioning._typeUnioned.eType = Type
Unioning._typeUnioned.eOpposite = Type.ownedUnioning
Disjoining._owningType.eType = Type
Disjoining._owningType.eOpposite = Type.ownedDisjoining
Differencing._typeDifferenced.eType = Type
Differencing._typeDifferenced.eOpposite = Type.ownedDifferencing
Classifier.ownedSubclassification.eType = Subclassification
Classifier.ownedSubclassification.eOpposite = Subclassification._owningClassifier

otherClassifiers = [VisibilityKind, FeatureDirectionKind]

for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif.ePackage = eClass

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)
