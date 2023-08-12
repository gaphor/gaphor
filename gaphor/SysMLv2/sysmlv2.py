"""Definition of meta model for SysML v2."""
# ruff: noqa: C901
from pyecore.ecore import (
    EReference,
    EDerivedCollection,
    EAttribute,
    abstract,
    EEnum,
)

from gaphor.UML import DataType
from gaphor.UMLTypes.uml_types import Boolean, String, Integer, Real
from gaphor.KerML.kerml import (
    ParameterMembership,
    BooleanExpression,
    InvocationExpression,
    Behavior,
    Structure,
    Association,
    LiteralExpression,
    Connector,
    Feature,
    Classifier,
    Class,
    Step,
    Function,
    FeatureMembership,
    Expression,
    MetadataFeature,
    BindingConnector,
    ItemFlow,
    Succession,
    Metaclass,
)

name = "sysmlv2"
nsURI = "https://www.omg.org/spec/SysML/20230201"
nsPrefix = "sysml"
PortionKind = EEnum("PortionKind", literals=["timeslice", "snapshot"])

RequirementConstraintKind = EEnum(
    "RequirementConstraintKind", literals=["assumption", "requirement"]
)

TriggerKind = EEnum("TriggerKind", literals=["when", "at", "after"])

StateSubactionKind = EEnum("StateSubactionKind", literals=["entry", "do", "exit"])

TransitionFeatureKind = EEnum(
    "TransitionFeatureKind", literals=["trigger", "guard", "effect"]
)


class DerivedVariant(EDerivedCollection):
    pass


class DerivedVariantmembership(EDerivedCollection):
    pass


class DerivedNestedusage(EDerivedCollection):
    pass


class DerivedDefinition(EDerivedCollection):
    pass


class DerivedUsage(EDerivedCollection):
    pass


class DerivedDirectedusage(EDerivedCollection):
    pass


class DerivedNestedreference(EDerivedCollection):
    pass


class DerivedNestedattribute(EDerivedCollection):
    pass


class DerivedNestedenumeration(EDerivedCollection):
    pass


class DerivedNestedoccurrence(EDerivedCollection):
    pass


class DerivedNesteditem(EDerivedCollection):
    pass


class DerivedNestedpart(EDerivedCollection):
    pass


class DerivedNestedport(EDerivedCollection):
    pass


class DerivedNestedconnection(EDerivedCollection):
    pass


class DerivedNestedflow(EDerivedCollection):
    pass


class DerivedNestedinterface(EDerivedCollection):
    pass


class DerivedNestedallocation(EDerivedCollection):
    pass


class DerivedNestedaction(EDerivedCollection):
    pass


class DerivedNestedstate(EDerivedCollection):
    pass


class DerivedNestedtransition(EDerivedCollection):
    pass


class DerivedNestedcalculation(EDerivedCollection):
    pass


class DerivedNestedconstraint(EDerivedCollection):
    pass


class DerivedNestedrequirement(EDerivedCollection):
    pass


class DerivedNestedconcern(EDerivedCollection):
    pass


class DerivedNestedcase(EDerivedCollection):
    pass


class DerivedNestedanalysiscase(EDerivedCollection):
    pass


class DerivedNestedverificationcase(EDerivedCollection):
    pass


class DerivedNestedusecase(EDerivedCollection):
    pass


class DerivedNestedview(EDerivedCollection):
    pass


class DerivedNestedviewpoint(EDerivedCollection):
    pass


class DerivedNestedrendering(EDerivedCollection):
    pass


class DerivedNestedmetadata(EDerivedCollection):
    pass


class Usage(Feature):
    """<p>A <code>Usage</code> is a usage of a <code>Definition</code>. A <code>Usage</code> may only be an <code>ownedFeature</code> of a <code>Definition</code> or another <code>Usage</code>.</p>

    <p>A <code>Usage</code> may have <code>nestedUsages</code> that model <code>features</code> that apply in the context of the <code>owningUsage</code>. A <code>Usage</code> may also have <code>Definitions</code> nested in it, but this has no semantic significance, other than the nested scoping resulting from the <code>Usage</code> being considered as a <code>Namespace</code> for any nested <code>Definitions</code>.</p>

    <p>However, if a <code>Usage</code> has <code>isVariation = true</code>, then it represents a <em>variation point</em> <code>Usage</code>. In this case, all of its <code>members</code> must be <code>variant</code> <code>Usages</code>, related to the <code>Usage</code> by <code>VariantMembership</code> <code>Relationships</code>. Rather than being <code>features</code> of the <code>Usage</code>, <code>variant</code> <code>Usages</code> model different concrete alternatives that can be chosen to fill in for the variation point <code>Usage</code>.</p>
    variant = variantMembership.ownedVariantUsage
    variantMembership = ownedMembership->selectByKind(VariantMembership)
    not isVariation implies variantMembership->isEmpty()
    isVariation implies variantMembership = ownedMembership
    isReference = not isComposite
    owningVariationUsage <> null implies
        specializes(owningVariationUsage)
    isVariation implies
        not ownedSpecialization.specific->exists(isVariation)
    owningVariationDefinition <> null implies
        specializes(owningVariationDefinition)
    directedUsage = directedFeature->selectByKind(Usage)
    nestedAction = nestedUsage->selectByKind(ActionUsage)
    nestedAllocation = nestedUsage->selectByKind(AllocationUsage)
    nestedAnalysisCase = nestedUsage->selectByKind(AnalysisCaseUsage)
    nestedAttribute = nestedUsage->selectByKind(AttributeUsage)
    nestedCalculation = nestedUsage->selectByKind(CalculationUsage)
    nestedCase = nestedUsage->selectByKind(CaseUsage)
    nestedConcern = nestedUsage->selectByKind(ConcernUsage)
    nestedConnection = nestedUsage->selectByKind(ConnectorAsUsage)
    nestedConstraint = nestedUsage->selectByKind(ConstraintUsage)
    ownedNested = nestedUsage->selectByKind(EnumerationUsage)
    nestedFlow = nestedUsage->selectByKind(FlowUsage)
    nestedInterface = nestedUsage->selectByKind(ReferenceUsage)
    nestedItem = nestedUsage->selectByKind(ItemUsage)
    nestedMetadata = nestedUsage->selectByKind(MetadataUsage)
    nestedOccurrence = nestedUsage->selectByKind(OccurrenceUsage)
    nestedPart = nestedUsage->selectByKind(PartUsage)
    nestedPort = nestedUsage->selectByKind(PortUsage)
    nestedReference = nestedUsage->selectByKind(ReferenceUsage)
    nestedRendering = nestedUsage->selectByKind(RenderingUsage)
    nestedRequirement = nestedUsage->selectByKind(RequirementUsage)
    nestedState = nestedUsage->selectByKind(StateUsage)
    nestedTransition = nestedUsage->selectByKind(TransitionUsage)
    nestedUsage = ownedFeature->selectByKind(Usage)
    nestedUseCase = nestedUsage->selectByKind(UseCaseUsage)
    nestedVerificationCase = nestedUsage->selectByKind(VerificationCaseUsage)
    nestedView = nestedUsage->selectByKind(ViewUsage)
    nestedViewpoint = nestedUsage->selectByKind(ViewpointUsage)
    usage = feature->selectByKind(Usage)
    owningType <> null implies
        (owningType.oclIsKindOf(Definition) or
         ownigType.oclIsKindOf(Usage))"""

    _isReference = EAttribute(
        eType=Boolean,
        unique=True,
        derived=True,
        changeable=True,
        name="isReference",
        transient=True,
    )
    isVariation = EAttribute(eType=Boolean, unique=True, derived=False, changeable=True)
    variant = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedVariant,
    )
    variantMembership = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedVariantmembership,
    )
    _owningDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningDefinition",
        transient=True,
    )
    _owningUsage = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningUsage",
        transient=True,
    )
    nestedUsage = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedusage,
    )
    definition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedDefinition,
    )
    usage = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedUsage,
    )
    directedUsage = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedDirectedusage,
    )
    nestedReference = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedreference,
    )
    nestedAttribute = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedattribute,
    )
    nestedEnumeration = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedenumeration,
    )
    nestedOccurrence = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedoccurrence,
    )
    nestedItem = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNesteditem,
    )
    nestedPart = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedpart,
    )
    nestedPort = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedport,
    )
    nestedConnection = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedconnection,
    )
    nestedFlow = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedflow,
    )
    nestedInterface = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedinterface,
    )
    nestedAllocation = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedallocation,
    )
    nestedAction = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedaction,
    )
    nestedState = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedstate,
    )
    nestedTransition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedtransition,
    )
    nestedCalculation = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedcalculation,
    )
    nestedConstraint = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedconstraint,
    )
    nestedRequirement = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedrequirement,
    )
    nestedConcern = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedconcern,
    )
    nestedCase = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedcase,
    )
    nestedAnalysisCase = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedanalysiscase,
    )
    nestedVerificationCase = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedverificationcase,
    )
    nestedUseCase = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedusecase,
    )
    nestedView = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedview,
    )
    nestedViewpoint = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedviewpoint,
    )
    nestedRendering = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedrendering,
    )
    nestedMetadata = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedNestedmetadata,
    )

    @property
    def isReference(self):
        raise NotImplementedError("Missing implementation for isReference")

    @isReference.setter
    def isReference(self, value):
        raise NotImplementedError("Missing implementation for isReference")

    @property
    def owningDefinition(self):
        raise NotImplementedError("Missing implementation for owningDefinition")

    @owningDefinition.setter
    def owningDefinition(self, value):
        raise NotImplementedError("Missing implementation for owningDefinition")

    @property
    def owningUsage(self):
        raise NotImplementedError("Missing implementation for owningUsage")

    @owningUsage.setter
    def owningUsage(self, value):
        raise NotImplementedError("Missing implementation for owningUsage")

    def __init__(
        self,
        *,
        isReference=None,
        isVariation=None,
        variant=None,
        variantMembership=None,
        owningDefinition=None,
        owningUsage=None,
        nestedUsage=None,
        definition=None,
        usage=None,
        directedUsage=None,
        nestedReference=None,
        nestedAttribute=None,
        nestedEnumeration=None,
        nestedOccurrence=None,
        nestedItem=None,
        nestedPart=None,
        nestedPort=None,
        nestedConnection=None,
        nestedFlow=None,
        nestedInterface=None,
        nestedAllocation=None,
        nestedAction=None,
        nestedState=None,
        nestedTransition=None,
        nestedCalculation=None,
        nestedConstraint=None,
        nestedRequirement=None,
        nestedConcern=None,
        nestedCase=None,
        nestedAnalysisCase=None,
        nestedVerificationCase=None,
        nestedUseCase=None,
        nestedView=None,
        nestedViewpoint=None,
        nestedRendering=None,
        nestedMetadata=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if isReference is not None:
            self.isReference = isReference

        if isVariation is not None:
            self.isVariation = isVariation

        if variant:
            self.variant.extend(variant)

        if variantMembership:
            self.variantMembership.extend(variantMembership)

        if owningDefinition is not None:
            self.owningDefinition = owningDefinition

        if owningUsage is not None:
            self.owningUsage = owningUsage

        if nestedUsage:
            self.nestedUsage.extend(nestedUsage)

        if definition:
            self.definition.extend(definition)

        if usage:
            self.usage.extend(usage)

        if directedUsage:
            self.directedUsage.extend(directedUsage)

        if nestedReference:
            self.nestedReference.extend(nestedReference)

        if nestedAttribute:
            self.nestedAttribute.extend(nestedAttribute)

        if nestedEnumeration:
            self.nestedEnumeration.extend(nestedEnumeration)

        if nestedOccurrence:
            self.nestedOccurrence.extend(nestedOccurrence)

        if nestedItem:
            self.nestedItem.extend(nestedItem)

        if nestedPart:
            self.nestedPart.extend(nestedPart)

        if nestedPort:
            self.nestedPort.extend(nestedPort)

        if nestedConnection:
            self.nestedConnection.extend(nestedConnection)

        if nestedFlow:
            self.nestedFlow.extend(nestedFlow)

        if nestedInterface:
            self.nestedInterface.extend(nestedInterface)

        if nestedAllocation:
            self.nestedAllocation.extend(nestedAllocation)

        if nestedAction:
            self.nestedAction.extend(nestedAction)

        if nestedState:
            self.nestedState.extend(nestedState)

        if nestedTransition:
            self.nestedTransition.extend(nestedTransition)

        if nestedCalculation:
            self.nestedCalculation.extend(nestedCalculation)

        if nestedConstraint:
            self.nestedConstraint.extend(nestedConstraint)

        if nestedRequirement:
            self.nestedRequirement.extend(nestedRequirement)

        if nestedConcern:
            self.nestedConcern.extend(nestedConcern)

        if nestedCase:
            self.nestedCase.extend(nestedCase)

        if nestedAnalysisCase:
            self.nestedAnalysisCase.extend(nestedAnalysisCase)

        if nestedVerificationCase:
            self.nestedVerificationCase.extend(nestedVerificationCase)

        if nestedUseCase:
            self.nestedUseCase.extend(nestedUseCase)

        if nestedView:
            self.nestedView.extend(nestedView)

        if nestedViewpoint:
            self.nestedViewpoint.extend(nestedViewpoint)

        if nestedRendering:
            self.nestedRendering.extend(nestedRendering)

        if nestedMetadata:
            self.nestedMetadata.extend(nestedMetadata)


class DerivedEnumeratedvalue(EDerivedCollection):
    pass


@abstract
class ConnectorAsUsage(Usage, Connector):
    """<p>A <code>ConnectorAsUsage</code> is both a <code>Connector</code> and a <code>Usage</code>. <code>ConnectorAsUsage</code> cannot itself be instantiated in a SysML model, but it is the base class for the concrete classes <code>BindingConnectorAsUsage</code>, <code>SuccessionAsUsage</code> and <code>ConnectionUsage</code>.</p>"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DerivedOwnedreference(EDerivedCollection):
    pass


class DerivedOwnedattribute(EDerivedCollection):
    pass


class DerivedOwnedenumeration(EDerivedCollection):
    pass


class DerivedOwnedoccurrence(EDerivedCollection):
    pass


class DerivedOwneditem(EDerivedCollection):
    pass


class DerivedOwnedpart(EDerivedCollection):
    pass


class DerivedOwnedport(EDerivedCollection):
    pass


class DerivedOwnedconnection(EDerivedCollection):
    pass


class DerivedOwnedflow(EDerivedCollection):
    pass


class DerivedOwnedinterface(EDerivedCollection):
    pass


class DerivedOwnedallocation(EDerivedCollection):
    pass


class DerivedOwnedaction(EDerivedCollection):
    pass


class DerivedOwnedstate(EDerivedCollection):
    pass


class DerivedOwnedtransition(EDerivedCollection):
    pass


class DerivedOwnedcalculation(EDerivedCollection):
    pass


class DerivedOwnedconstraint(EDerivedCollection):
    pass


class DerivedOwnedrequirement(EDerivedCollection):
    pass


class DerivedOwnedconcern(EDerivedCollection):
    pass


class DerivedOwnedcase(EDerivedCollection):
    pass


class DerivedOwnedanalysiscase(EDerivedCollection):
    pass


class DerivedOwnedverificationcase(EDerivedCollection):
    pass


class DerivedOwnedusecase(EDerivedCollection):
    pass


class DerivedOwnedview(EDerivedCollection):
    pass


class DerivedOwnedviewpoint(EDerivedCollection):
    pass


class DerivedOwnedrendering(EDerivedCollection):
    pass


class DerivedOwnedmetadata(EDerivedCollection):
    pass


class DerivedOwnedusage(EDerivedCollection):
    pass


class Definition(Classifier):
    """<p>A <code>Definition</code> is a <code>Classifier</code> of <code>Usages</code>. The actual kinds of <code>Definition</code> that may appear in a model are given by the subclasses of <code>Definition</code> (possibly as extended with user-defined <em><code>SemanticMetadata</code></em>).</p>

    <p>Normally, a <code>Definition</code> has owned Usages that model <code>features</code> of the thing being defined. A <code>Definition</code> may also have other <code>Definitions</code> nested in it, but this has no semantic significance, other than the nested scoping resulting from the <code>Definition</code> being considered as a <code>Namespace</code> for any nested <code>Definitions</code>.</p>

    <p>However, if a <code>Definition</code> has <code>isVariation</code> = <code>true</code>, then it represents a <em>variation point</em> <code>Definition</code>. In this case, all of its <code>members</code> must be <code>variant</code> <code>Usages</code>, related to the <code>Definition</code> by <code>VariantMembership</code> <code>Relationships</code>. Rather than being <code>features</code> of the <code>Definition</code>, <code>variant</code> <code>Usages</code> model different concrete alternatives that can be chosen to fill in for an abstract <code>Usage</code> of the variation point <code>Definition</code>.</p>

    isVariation implies variantMembership = ownedMembership
    variant = variantMembership.ownedVariantUsage
    variantMembership = ownedMembership->selectByKind(VariantMembership)
    not isVariation implies variantMembership->isEmpty()
    isVariation implies
        not ownedSpecialization.specific->exists(isVariation)
    usage = feature->selectByKind(Usage)
    directedUsage = directedFeature->selectByKind(Usage)
    ownedUsage = ownedFeature->selectByKind(Usage)
    ownedAttribute = ownedUsage->selectByKind(AttributeUsage)
    ownedReference = ownedUsage->selectByKind(ReferenceUsage)
    ownedEnumeration = ownedUsage->selectByKind(EnumerationUsage)
    ownedOccurrence = ownedUsage->selectByKind(OccurrenceUsage)
    ownedItem = ownedUsage->selectByKind(ItemUsage)
    ownedPart = ownedUsage->selectByKind(PartUsage)
    ownedPort = ownedUsage->selectByKind(PortUsage)
    ownedConnection = ownedUsage->selectByKind(ConnectorAsUsage)
    ownedFlow = ownedUsage->selectByKind(FlowUsage)
    ownedInterface = ownedUsage->selectByKind(ReferenceUsage)
    ownedAllocation = ownedUsage->selectByKind(AllocationUsage)
    ownedAction = ownedUsage->selectByKind(ActionUsage)
    ownedState = ownedUsage->selectByKind(StateUsage)
    ownedTransition = ownedUsage->selectByKind(TransitionUsage)
    ownedCalculation = ownedUsage->selectByKind(CalculationUsage)
    ownedConstraint = ownedUsage->selectByKind(ConstraintUsage)
    ownedRequirement = ownedUsage->selectByKind(RequirementUsage)
    ownedConcern = ownedUsage->selectByKind(ConcernUsage)
    ownedCase = ownedUsage->selectByKind(CaseUsage)
    ownedAnalysisCase = ownedUsage->selectByKind(AnalysisCaseUsage)
    ownedVerificationCase = ownedUsage->selectByKind(VerificationCaseUsage)
    ownedUseCase = ownedUsage->selectByKind(UseCaseUsage)
    ownedView = ownedUsage->selectByKind(ViewUsage)
    ownedViewpoint = ownedUsage->selectByKind(ViewpointUsage)
    ownedRendering = ownedUsage->selectByKind(RenderingUsage)
    ownedMetadata = ownedUsage->selectByKind(MetadataUsage)"""

    isVariation = EAttribute(eType=Boolean, unique=True, derived=False, changeable=True)
    variant = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedVariant,
    )
    variantMembership = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedVariantmembership,
    )
    usage = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedUsage,
    )
    directedUsage = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedDirectedusage,
    )
    ownedReference = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedreference,
    )
    ownedAttribute = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedattribute,
    )
    ownedEnumeration = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedenumeration,
    )
    ownedOccurrence = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedoccurrence,
    )
    ownedItem = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwneditem,
    )
    ownedPart = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedpart,
    )
    ownedPort = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedport,
    )
    ownedConnection = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedconnection,
    )
    ownedFlow = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedflow,
    )
    ownedInterface = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedinterface,
    )
    ownedAllocation = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedallocation,
    )
    ownedAction = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedaction,
    )
    ownedState = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedstate,
    )
    ownedTransition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedtransition,
    )
    ownedCalculation = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedcalculation,
    )
    ownedConstraint = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedconstraint,
    )
    ownedRequirement = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedrequirement,
    )
    ownedConcern = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedconcern,
    )
    ownedCase = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedcase,
    )
    ownedAnalysisCase = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedanalysiscase,
    )
    ownedVerificationCase = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedverificationcase,
    )
    ownedUseCase = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedusecase,
    )
    ownedView = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedview,
    )
    ownedViewpoint = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedviewpoint,
    )
    ownedRendering = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedrendering,
    )
    ownedMetadata = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedmetadata,
    )
    ownedUsage = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedusage,
    )

    def __init__(
        self,
        *,
        isVariation=None,
        variant=None,
        variantMembership=None,
        usage=None,
        directedUsage=None,
        ownedReference=None,
        ownedAttribute=None,
        ownedEnumeration=None,
        ownedOccurrence=None,
        ownedItem=None,
        ownedPart=None,
        ownedPort=None,
        ownedConnection=None,
        ownedFlow=None,
        ownedInterface=None,
        ownedAllocation=None,
        ownedAction=None,
        ownedState=None,
        ownedTransition=None,
        ownedCalculation=None,
        ownedConstraint=None,
        ownedRequirement=None,
        ownedConcern=None,
        ownedCase=None,
        ownedAnalysisCase=None,
        ownedVerificationCase=None,
        ownedUseCase=None,
        ownedView=None,
        ownedViewpoint=None,
        ownedRendering=None,
        ownedMetadata=None,
        ownedUsage=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if isVariation is not None:
            self.isVariation = isVariation

        if variant:
            self.variant.extend(variant)

        if variantMembership:
            self.variantMembership.extend(variantMembership)

        if usage:
            self.usage.extend(usage)

        if directedUsage:
            self.directedUsage.extend(directedUsage)

        if ownedReference:
            self.ownedReference.extend(ownedReference)

        if ownedAttribute:
            self.ownedAttribute.extend(ownedAttribute)

        if ownedEnumeration:
            self.ownedEnumeration.extend(ownedEnumeration)

        if ownedOccurrence:
            self.ownedOccurrence.extend(ownedOccurrence)

        if ownedItem:
            self.ownedItem.extend(ownedItem)

        if ownedPart:
            self.ownedPart.extend(ownedPart)

        if ownedPort:
            self.ownedPort.extend(ownedPort)

        if ownedConnection:
            self.ownedConnection.extend(ownedConnection)

        if ownedFlow:
            self.ownedFlow.extend(ownedFlow)

        if ownedInterface:
            self.ownedInterface.extend(ownedInterface)

        if ownedAllocation:
            self.ownedAllocation.extend(ownedAllocation)

        if ownedAction:
            self.ownedAction.extend(ownedAction)

        if ownedState:
            self.ownedState.extend(ownedState)

        if ownedTransition:
            self.ownedTransition.extend(ownedTransition)

        if ownedCalculation:
            self.ownedCalculation.extend(ownedCalculation)

        if ownedConstraint:
            self.ownedConstraint.extend(ownedConstraint)

        if ownedRequirement:
            self.ownedRequirement.extend(ownedRequirement)

        if ownedConcern:
            self.ownedConcern.extend(ownedConcern)

        if ownedCase:
            self.ownedCase.extend(ownedCase)

        if ownedAnalysisCase:
            self.ownedAnalysisCase.extend(ownedAnalysisCase)

        if ownedVerificationCase:
            self.ownedVerificationCase.extend(ownedVerificationCase)

        if ownedUseCase:
            self.ownedUseCase.extend(ownedUseCase)

        if ownedView:
            self.ownedView.extend(ownedView)

        if ownedViewpoint:
            self.ownedViewpoint.extend(ownedViewpoint)

        if ownedRendering:
            self.ownedRendering.extend(ownedRendering)

        if ownedMetadata:
            self.ownedMetadata.extend(ownedMetadata)

        if ownedUsage:
            self.ownedUsage.extend(ownedUsage)


class AttributeDefinition(Definition, DataType):  # type: ignore
    """<p>An <code>AttributeDefinition</code> is a <code>Definition</code> and a <code>DataType</code> of information about a quality or characteristic of a system or part of a system that has no independent identity other than its value. All <code>features</code> of an <code>AttributeDefinition</code> must be referential (non-composite).</p>

    <p>As a <code>DataType</code>, an <code>AttributeDefinition</code> must specialize, directly or indirectly, the base <code>DataType</code> <code><em>Base::DataValue</em></code> from the Kernel Semantic Library.</p>
    feature->forAll(not isComposite)"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class OccurrenceDefinition(Definition, Class):
    """<p>An <code>OccurrenceDefinition</code> is a <code>Definition</code> of a <code>Class</code> of individuals that have an independent life over time and potentially an extent over space. This includes both structural things and behaviors that act on such structures.</p>

    <p>If <code>isIndividual</code> is true, then the <code>OccurrenceDefinition</code> is constrained to represent an individual thing. The instances of such an <code>OccurrenceDefinition</code> include all spatial and temporal portions of the individual being represented, but only one of these can be the complete <code>Life</code> of the individual. All other instances must be portions of the &quot;maximal portion&quot; that is single <code>Life</code> instance, capturing the conception that all of the instances represent one individual with a single &quot;identity&quot;.</p>

    <p>An <code>OccurrenceDefinition</code> must specialize, directly or indirectly, the base <code>Class</code> <code><em>Occurrence</em></code> from the Kernel Semantic Library.</p>

    let n : Integer = ownedMember->selectByKind(LifeClass) in
    if isIndividual then n = 1 else n = 0 endif
    lifeClass =
        let lifeClasses: OrderedSet(LifeClass) =
            ownedMember->selectByKind(LifeClass) in
        if lifeClasses->isEmpty() then null
        else lifeClasses->first()
        endif"""

    isIndividual = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    _lifeClass = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="lifeClass",
        transient=True,
    )

    @property
    def lifeClass(self):
        raise NotImplementedError("Missing implementation for lifeClass")

    @lifeClass.setter
    def lifeClass(self, value):
        raise NotImplementedError("Missing implementation for lifeClass")

    def __init__(self, *, lifeClass=None, isIndividual=None, **kwargs):
        super().__init__(**kwargs)

        if isIndividual is not None:
            self.isIndividual = isIndividual

        if lifeClass is not None:
            self.lifeClass = lifeClass


class EnumerationDefinition(AttributeDefinition):
    """<p>An <code>EnumerationDefinition</code> is an <code>AttributeDefinition</code> all of whose instances are given by an explicit list of <code>enumeratedValues</code>. This is realized by requiring that the <code>EnumerationDefinition</code> have <code>isVariation = true</code>, with the <code>enumeratedValues</code> being its <code>variants</code>.</p>
    isVariation"""

    enumeratedValue = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedEnumeratedvalue,
    )

    def __init__(self, *, enumeratedValue=None, **kwargs):
        super().__init__(**kwargs)

        if enumeratedValue:
            self.enumeratedValue.extend(enumeratedValue)


class DerivedActiondefinition(EDerivedCollection):
    pass


class DerivedOccurrencedefinition(EDerivedCollection):
    pass


class OccurrenceUsage(Usage):
    """<p>An <code>OccurrenceUsage</code> is a <code>Usage</code> whose <code>types</code> are all <code>Classes</code>. Nominally, if a <code>type</code> is an <code>OccurrenceDefinition</code>, an <code>OccurrenceUsage</code> is a <code>Usage</code> of that <code>OccurrenceDefinition</code> within a system. However, other types of Kernel <code>Classes</code> are also allowed, to permit use of <code>Classes</code> from the Kernel Model Libraries.</p>

    individualDefinition =
        let individualDefinitions : OrderedSet(OccurrenceDefinition) =
            occurrenceDefinition->
                selectByKind(OccurrenceDefinition)->
                select(isIndividual) in
        if individualDefinitions->isEmpty() then null
        else individualDefinitions->first() endif
    isIndividual implies individualDefinition <> null
    specializesFromLibrary("Occurrences::occurrences")
    isComposite and
    owningType <> null and
    (owningType.oclIsKindOf(Class) or
     owningType.oclIsKindOf(OccurrenceUsage) or
     owningType.oclIsKindOf(Feature) and
        owningType.oclAsType(Feature).type->
            exists(oclIsKind(Class))) implies
        specializesFromLibrary("Occurrences::Occurrence::suboccurrences")
    occurrenceDefinition->select(isIndividual).size() <= 1
    portionKind <> null implies
        occurrenceDefinition->forAll(occ |
            featuringType->exists(specializes(occ)))"""

    isIndividual = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    portionKind = EAttribute(
        eType=PortionKind, unique=True, derived=False, changeable=True
    )
    occurrenceDefinition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOccurrencedefinition,
    )
    _individualDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="individualDefinition",
        transient=True,
    )

    @property
    def individualDefinition(self):
        raise NotImplementedError("Missing implementation for individualDefinition")

    @individualDefinition.setter
    def individualDefinition(self, value):
        raise NotImplementedError("Missing implementation for individualDefinition")

    def __init__(
        self,
        *,
        occurrenceDefinition=None,
        individualDefinition=None,
        isIndividual=None,
        portionKind=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if isIndividual is not None:
            self.isIndividual = isIndividual

        if portionKind is not None:
            self.portionKind = portionKind

        if occurrenceDefinition:
            self.occurrenceDefinition.extend(occurrenceDefinition)

        if individualDefinition is not None:
            self.individualDefinition = individualDefinition


class ActionUsage(OccurrenceUsage, Step):
    """<p>An <code>ActionUsage</code> is a <code>Usage</code> that is also a <code>Step</code>, and, so, is typed by a <code>Behavior</code>. Nominally, if the type is an <code>ActionDefinition</code>, an <code>ActionUsage</code> is a <code>Usage</code> of that <code>ActionDefinition</code> within a system. However, other kinds of kernel <code>Behaviors</code> are also allowed, to permit use of <code>Behaviors</code> from the Kernel Model Libraries.</p>

    isSubactionUsage() implies
        specializesFromLibrary('Actions::Action::subactions')
    specializesFromLibrary('Actions::actions')
    isComposite and owningType <> null and
    (owningType.oclIsKindOf(PartDefinition) or
     owningType.oclIsKindOf(PartUsage)) implies
        specializesFromLibrary('Parts::Part::ownedActions')
    owningFeatureMembership <> null and
    owningFeatureMembership.oclIsKindOf(StateSubactionMembership) implies
        let kind : StateSubactionKind =
            owningFeatureMembership.oclAsType(StateSubactionMembership).kind in
        if kind = StateSubactionKind::entry then
            redefinesFromLibrary('States::StateAction::entryAction')
        else if kind = StateSubactionKind::do then
            redefinesFromLibrary('States::StateAction::doAction')
        else
            redefinesFromLibrary('States::StateAction::exitAction')
        endif endif
    owningType <> null and
        (owningType.oclIsKindOf(AnalysisCaseDefinition) and
            owningType.oclAsType(AnalysisCaseDefinition).analysisAction->
                includes(self) or
         owningType.oclIsKindOf(AnalysisCaseUsage) and
            owningType.oclAsType(AnalysisCaseUsage).analysisAction->
                includes(self)) implies
        specializesFromLibrary('AnalysisCases::AnalysisCase::analysisSteps')"""

    actionDefinition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedActiondefinition,
    )

    def __init__(self, *, actionDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if actionDefinition:
            self.actionDefinition.extend(actionDefinition)

    def inputParameters(self):
        """<p>Return the owned input <code>parameters</code> of this <code>ActionUsage</code>.</p>
        input->select(f | f.owner = self)"""
        raise NotImplementedError("operation inputParameters(...) not yet implemented")

    def inputParameter(self, i=None):
        """<p>Return the <code>i<code>-th owned input <code>parameter</code> of the <code>ActionUsage</code>. Return null if the <code>ActionUsage</code> has less than <code>i<code> owned input <code>parameters</code>.</p>
        if inputParameters()->size() < i then null
        else inputParameters()->at(i)
        endif"""
        raise NotImplementedError("operation inputParameter(...) not yet implemented")

    def argument(self, i=None):
        """<p>Return the <code>i<code>-th argument <code>Expression</code> of an <code>ActionUsage</code>, defined as the <code>value</code> <code>Expression</code> of the <code>FeatureValue</code> of the <code>i<code>-th owned input <code>parameter</code> of the <code>ActionUsage</code>. Return null if the <code>ActionUsage</code> has less than <code>i<code> owned input <code>parameters</code> or the <code>i<code>-th owned input <code>parameter</code> has no <code>FeatureValue</code>.</code>
        if inputParameter(i) = null then null
        else
            let featureValue : Sequence(FeatureValue) = inputParameter(i).
                ownedMembership->select(oclIsKindOf(FeatureValue)) in
            if featureValue->isEmpty() then null
            else featureValue->at(1).value
            endif
        endif"""
        raise NotImplementedError("operation argument(...) not yet implemented")

    def isSubactionUsage(self):
        """<p>Check if this <code>ActionUsage</code> is composite and has an <code>owningType</code> that is an <code>ActionDefinition</code> or <code>ActionUsage</code> but is <em>not</em> the <code>entryAction</code> or <code>exitAction</em></code> of a <code>StateDefinition</code> or <code>StateUsage</code>. If so, then it represents an <code><em>Action</em></code> that is a <code><em>subaction</em></code> of another <code><em>Action</em></code>.</p>
        isComposite and owningType <> null and
        (owningType.oclIsKindOf(ActionDefinition) or
         owningType.oclIsKindOf(ActionUsage)) and
        (owningFeatureMembership.oclIsKindOf(StateSubactionMembership) implies
         owningFeatureMembership.oclAsType(StateSubactionMembership).kind =
            StateSubactionKind::do)"""
        raise NotImplementedError("operation isSubactionUsage(...) not yet implemented")


class Predicate(Function):
    """<p>A <code>Predicate</code> is a <code>Function</code> whose <code>result</code> <code>parameter</code> has type <code><em>Boolean</em></code> and multiplicity <code>1..1</code>.</p>

    specializesFromLibrary("Performances::BooleanEvaluation")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RequirementConstraintMembership(FeatureMembership):
    """<p>A <code>RequirementConstraintMembership</code> is a <code>FeatureMembership</code> for an assumed or required <code>ConstraintUsage</code> of a <code>RequirementDefinition</code> or <code>RequirementUsage<code>.</p>
    referencedConstraint =
        let reference : ReferenceSubsetting =
            ownedConstraint.ownedReferenceSubsetting in
        if reference = null then ownedConstraint
        else if not reference.referencedFeature.oclIsKindOf(ConstraintUsage) then null
        else reference.referencedFeature.oclAsType(ConstraintUsage)
        endif endif
    owningType.oclIsKindOf(RequirementDefinition) or
    owningType.oclIsKindOf(RequirementUsage)
    ownedConstraint.isComposite"""

    kind = EAttribute(
        eType=RequirementConstraintKind, unique=True, derived=False, changeable=True
    )
    _ownedConstraint = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedConstraint",
        transient=True,
    )
    _referencedConstraint = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="referencedConstraint",
        transient=True,
    )

    @property
    def ownedConstraint(self):
        raise NotImplementedError("Missing implementation for ownedConstraint")

    @ownedConstraint.setter
    def ownedConstraint(self, value):
        raise NotImplementedError("Missing implementation for ownedConstraint")

    @property
    def referencedConstraint(self):
        raise NotImplementedError("Missing implementation for referencedConstraint")

    @referencedConstraint.setter
    def referencedConstraint(self, value):
        raise NotImplementedError("Missing implementation for referencedConstraint")

    def __init__(
        self, *, kind=None, ownedConstraint=None, referencedConstraint=None, **kwargs
    ):
        super().__init__(**kwargs)

        if kind is not None:
            self.kind = kind

        if ownedConstraint is not None:
            self.ownedConstraint = ownedConstraint

        if referencedConstraint is not None:
            self.referencedConstraint = referencedConstraint


class RequirementVerificationMembership(RequirementConstraintMembership):
    """<p>A <code>RequirementVerificationMembership</code> is a <code>RequirementConstraintMembership </code> used in the objective of a <code>VerificationCase</code> to identify a <code>RequirementUsage</code> that is verified by the <code>VerificationCase</code>.</p>
    kind = RequirementConstraintKind::requirement
    owningType.oclIsKindOf(RequirementUsage) and
    owningType.owningFeatureMembership <> null and
    owningType.owningFeatureMembership.oclIsKindOf(ObjectiveMembership)"""

    _ownedRequirement = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedRequirement",
        transient=True,
    )
    _verifiedRequirement = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="verifiedRequirement",
        transient=True,
    )

    @property
    def ownedRequirement(self):
        raise NotImplementedError("Missing implementation for ownedRequirement")

    @ownedRequirement.setter
    def ownedRequirement(self, value):
        raise NotImplementedError("Missing implementation for ownedRequirement")

    @property
    def verifiedRequirement(self):
        raise NotImplementedError("Missing implementation for verifiedRequirement")

    @verifiedRequirement.setter
    def verifiedRequirement(self, value):
        raise NotImplementedError("Missing implementation for verifiedRequirement")

    def __init__(self, *, ownedRequirement=None, verifiedRequirement=None, **kwargs):
        super().__init__(**kwargs)

        if ownedRequirement is not None:
            self.ownedRequirement = ownedRequirement

        if verifiedRequirement is not None:
            self.verifiedRequirement = verifiedRequirement


class FramedConcernMembership(RequirementConstraintMembership):
    """<p>A <code>FramedConcernMembership</code> is a <code>RequirementConstraintMembership</code> for a framed <code>ConcernUsage</code> of a <code>RequirementDefinition</code> or <code>RequirementUsage</code>.</p>
    kind = RequirementConstraintKind::requirement"""

    _ownedConcern = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedConcern",
        transient=True,
    )
    _referencedConcern = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="referencedConcern",
        transient=True,
    )

    @property
    def ownedConcern(self):
        raise NotImplementedError("Missing implementation for ownedConcern")

    @ownedConcern.setter
    def ownedConcern(self, value):
        raise NotImplementedError("Missing implementation for ownedConcern")

    @property
    def referencedConcern(self):
        raise NotImplementedError("Missing implementation for referencedConcern")

    @referencedConcern.setter
    def referencedConcern(self, value):
        raise NotImplementedError("Missing implementation for referencedConcern")

    def __init__(self, *, ownedConcern=None, referencedConcern=None, **kwargs):
        super().__init__(**kwargs)

        if ownedConcern is not None:
            self.ownedConcern = ownedConcern

        if referencedConcern is not None:
            self.referencedConcern = referencedConcern


class SubjectMembership(ParameterMembership):
    """<p>A <code>SubjectMembership</code> is a <code>ParameterMembership</code> that indicates that its <code>ownedSubjectParameter</code> is the subject of its <code>owningType</code>. The <code>owningType</code> of a <code>SubjectMembership</code> must be a <code>RequirementDefinition</code>, <code>RequirementUsage</code>, <code>CaseDefinition</code>, or <code>CaseUsage</code>.</p>
    owningType.oclIsType(RequirementDefinition) or
    owningType.oclIsType(RequiremenCaseRequirementDefinition) or
    owningType.oclIsType(CaseDefinition) or
    owningType.oclIsType(CaseUsage)"""

    _ownedSubjectParameter = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedSubjectParameter",
        transient=True,
    )

    @property
    def ownedSubjectParameter(self):
        raise NotImplementedError("Missing implementation for ownedSubjectParameter")

    @ownedSubjectParameter.setter
    def ownedSubjectParameter(self, value):
        raise NotImplementedError("Missing implementation for ownedSubjectParameter")

    def __init__(self, *, ownedSubjectParameter=None, **kwargs):
        super().__init__(**kwargs)

        if ownedSubjectParameter is not None:
            self.ownedSubjectParameter = ownedSubjectParameter


class ActorMembership(ParameterMembership):
    """<p>An <code>ActorMembership</code> is a <code>ParameterMembership</code> that identifies a <code>PartUsage</code> as an <em>actor</em> <code>parameter</code>, which specifies a role played by an external entity in interaction with the <code>owningType</code> of the <code>ActorMembership</code>.</p>
    owningType.oclIsKindOf(RequirementUsage) or
    owningType.oclIsKindOf(RequirementDefinition) or
    owningType.oclIsKindOf(CaseDefinition) or
    owningType.oclIsKindOf(CaseUsage)"""

    _ownedActorParameter = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedActorParameter",
        transient=True,
    )

    @property
    def ownedActorParameter(self):
        raise NotImplementedError("Missing implementation for ownedActorParameter")

    @ownedActorParameter.setter
    def ownedActorParameter(self, value):
        raise NotImplementedError("Missing implementation for ownedActorParameter")

    def __init__(self, *, ownedActorParameter=None, **kwargs):
        super().__init__(**kwargs)

        if ownedActorParameter is not None:
            self.ownedActorParameter = ownedActorParameter


class StakeholderMembership(ParameterMembership):
    """<p>A <code>StakeholderMembership</code> is a <code>ParameterMembership</code> that identifies a <code>PartUsage</code> as a <code>stakeholderParameter</code> of a <code>RequirementDefinition</code> or <code>RequirementUsage</code>, which specifies a role played by an entity with concerns framed by the <code>owningType</code>.</p>
    owningType.oclIsKindOf(RequirementUsage) or
    owningType.oclIsKindOf(RequirementDefinition)"""

    _ownedStakeholderParameter = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedStakeholderParameter",
        transient=True,
    )

    @property
    def ownedStakeholderParameter(self):
        raise NotImplementedError(
            "Missing implementation for ownedStakeholderParameter"
        )

    @ownedStakeholderParameter.setter
    def ownedStakeholderParameter(self, value):
        raise NotImplementedError(
            "Missing implementation for ownedStakeholderParameter"
        )

    def __init__(self, *, ownedStakeholderParameter=None, **kwargs):
        super().__init__(**kwargs)

        if ownedStakeholderParameter is not None:
            self.ownedStakeholderParameter = ownedStakeholderParameter


class Invariant(BooleanExpression):
    """<p>An <code>Invariant</code> is a <code>BooleanExpression</code> that is asserted to have a specific <code><em>Boolean</em></code> result value. If <code>isNegated = false</code>, then the result is asserted to be true. If <code>isNegated = true</code>, then the result is asserted to be false.</p>

    if isNegated then
        specializesFromLibrary("Performances::falseEvaluations")
    else
        specializesFromLibrary("Performances::trueEvaluations")
    endif"""

    isNegated = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )

    def __init__(self, *, isNegated=None, **kwargs):
        super().__init__(**kwargs)

        if isNegated is not None:
            self.isNegated = isNegated


class TriggerInvocationExpression(InvocationExpression):
    """<p>A <code>TriggerInvocationExpression<code> is an <code>InvocationExpression</code> that invokes one of the trigger <code>Functions</code> from the Kernel Semantic Library <code><em>Triggers<em></code> package, as indicated by its <code>kind</code>.</p>
    specializesFromLibrary(
        if kind = TriggerKind::when then
            'Triggers::TriggerWhen'
        else if kind = TriggerKind::at then
            'Triggers::TriggerAt'
        else
            'Triggers::TriggerAfter'
        endif endif
    )"""

    kind = EAttribute(eType=TriggerKind, unique=True, derived=False, changeable=True)

    def __init__(self, *, kind=None, **kwargs):
        super().__init__(**kwargs)

        if kind is not None:
            self.kind = kind


class ReturnParameterMembership(ParameterMembership):
    """<p>A <code>ReturnParameterMembership</code> is a <code>ParameterMembership</code> that indicates that the <code>ownedMemberParameter</code> is the <code>result</code> <code>parameter</code> of a <code>Function</code> or <code>Expression</code>. The <code>direction</code> of the <code>ownedMemberParameter</code> must be <code>out</code>.</p>

    owningType.oclIsKindOf(Function) or owningType.oclIsKindOf(Expression)
    ownedMemberParameter.direction = ParameterDirectionKind::out"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DerivedOperand(EDerivedCollection):
    pass


class OperatorExpression(InvocationExpression):
    """<p>An <code>OperatorExpression</code> is an <code>InvocationExpression</code> whose <code>function</code> is determined by resolving its <code>operator</code> in the context of one of the standard packages from the Kernel Function Library.</p>
    let libFunctions : Sequence(Element) =
        Sequence{"BaseFunctions", "DataFunctions", "ControlFunctions"}->
        collect(ns | resolveGlobal(ns + "::'" + operator + "'")) in
    libFunctions->includes(function)
    """

    operator = EAttribute(eType=String, unique=True, derived=False, changeable=True)
    operand = EReference(
        ordered=True,
        unique=True,
        containment=True,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOperand,
    )

    def __init__(self, *, operator=None, operand=None, **kwargs):
        super().__init__(**kwargs)

        if operator is not None:
            self.operator = operator

        if operand:
            self.operand.extend(operand)


class LiteralBoolean(LiteralExpression):
    """<p><code>LiteralBoolean</code> is a <code>LiteralExpression</code> that provides a <code><em>Boolean</em></code> value as a result. Its <code>result</code> <code>parameter</code> must have type <code><em>Boolean</em></code>.</p>"""

    value = EAttribute(eType=Boolean, unique=True, derived=False, changeable=True)

    def __init__(self, *, value=None, **kwargs):
        super().__init__(**kwargs)

        if value is not None:
            self.value = value


class LiteralInteger(LiteralExpression):
    """<p>A <code>LiteralInteger</code> is a <code>LiteralExpression</code> that provides an <code><em>Integer</em></code> value as a result. Its <code>result</code> <code>parameter</code> must have the type <code><em>Integer</em></code>.</p>"""

    value = EAttribute(eType=Integer, unique=True, derived=False, changeable=True)

    def __init__(self, *, value=None, **kwargs):
        super().__init__(**kwargs)

        if value is not None:
            self.value = value


class LiteralRational(LiteralExpression):
    """<p>A <code>LiteralRational</code> is a <code>LiteralExpression</code> that provides a <code><em>Rational</em></code> value as a result. Its <code>result</code> <code>parameter</code> must have the type <code><em>Rational</em></code>.</p>"""

    value = EAttribute(eType=Real, unique=True, derived=False, changeable=True)

    def __init__(self, *, value=None, **kwargs):
        super().__init__(**kwargs)

        if value is not None:
            self.value = value


class LiteralInfinity(LiteralExpression):
    """<p>A <code>LiteralInfinity</code> is a <code>LiteralExpression</code> that provides the positive infinity value (<code>*</code>). It's <code>result</code> must have the type <code><em>Positive</em></code>.</p>"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class LiteralString(LiteralExpression):
    """<p>A <code>LiteralString</code> is a <code>LiteralExpression</code> that provides a <code><em>String</em></code> value as a result. Its <code>result</code> <code>parameter</code> must have the type <code><em>String</em></code>.</p>"""

    value = EAttribute(eType=String, unique=True, derived=False, changeable=True)

    def __init__(self, *, value=None, **kwargs):
        super().__init__(**kwargs)

        if value is not None:
            self.value = value


class ItemDefinition(OccurrenceDefinition, Structure):
    """<p>An <code>ItemDefinition</code> is an <code>OccurrenceDefinition</code> of the <code>Structure</code> of things that may themselves be systems or parts of systems, but may also be things that are acted on by a system or parts of a system, but which do not necessarily perform actions themselves. This includes items that can be exchanged between parts of a system, such as water or electrical signals.</p>

    specializesFromLibrary("Items::Item")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PortDefinition(OccurrenceDefinition, Structure):
    """<p>A <code>PortDefinition</code> defines a point at which external entities can connect to and interact with a system or part of a system. Any <code>ownedUsages</code> of a <code>PortDefinition</code>, other than <code>PortUsages</code>, must not be composite.</p>



    conjugatedPortDefinition =
    let conjugatedPortDefinitions : OrderedSet(ConjugatedPortDefinition) =
        ownedMember->selectByKind(ConjugatedPortDefinition) in
    if conjugatedPortDefinitions->isEmpty() then null
    else conjugatedPortDefinitions->first()
    endif
    ownedUsage->
        reject(oclIsKindOf(PortUsage))->
        forAll(not isComposite)
    not oclIsKindOf(ConjugatedPortDefinition) implies
        ownedMember->
            selectByKind(ConjugatedPortDefinition)->
            size() = 1
    specializeFromLibrary('Ports::Port')"""

    _conjugatedPortDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="conjugatedPortDefinition",
        transient=True,
    )

    @property
    def conjugatedPortDefinition(self):
        raise NotImplementedError("Missing implementation for conjugatedPortDefinition")

    @conjugatedPortDefinition.setter
    def conjugatedPortDefinition(self, value):
        raise NotImplementedError("Missing implementation for conjugatedPortDefinition")

    def __init__(self, *, conjugatedPortDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if conjugatedPortDefinition is not None:
            self.conjugatedPortDefinition = conjugatedPortDefinition


class Interaction(Association, Behavior):
    """<p>An <code>Interaction</code> is a <code>Behavior</code> that is also an <code>Association</code>, providing a context for multiple objects that have behaviors that impact one another.</p>"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AssociationStructure(Association, Structure):
    """<p>An <code>AssociationStructure</code> is an <code>Association</code> that is also a <code>Structure</code>, classifying link objects that are both links and objects. As objects, link objects can be created and destroyed, and their non-end <code>Features</code> can change over time. However, the values of the end <code>Features</code> of a link object are fixed and cannot change over its lifetime.</p>
    specializesFromLibrary("Objects::ObjectLink")
    endFeature->size() = 2 implies
        specializesFromLibrary("Objects::BinaryLinkObject")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DerivedStatedefinition(EDerivedCollection):
    pass


class StateUsage(ActionUsage):
    """<p>A <code>StateUsage</code> is an <code>ActionUsage</code> that is nominally the <code>Usage</code> of a <code>StateDefinition</code>. However, other kinds of kernel <code>Behaviors</code> are also allowed as <code>types</code>, to permit use of <code>Behaviors</code from the Kernel Model Libraries.</p>

    <p>A <code>StateUsage</code> may be related to up to three of its <code>ownedFeatures</code> by <code>StateSubactionMembership</code> <code>Relationships<code>, all of different <code>kinds</code>, corresponding to the entry, do and exit actions of the <code>StateUsage</code>.</p>

    let general : Sequence(Type) = ownedGeneralization.general in
    general->selectByKind(StateDefinition)->
        forAll(g | g.isParallel = isParallel) and
    general->selectByKind(StateUsage)->
        forAll(g | g.parallel = isParallel)
    doAction =
        let doMemberships : Sequence(StateSubactionMembership) =
            ownedMembership->
                selectByKind(StateSubactionMembership)->
                select(kind = StateSubactionKind::do) in
        if doMemberships->isEmpty() then null
        else doMemberships->at(1)
        endif
    entryAction =
        let entryMemberships : Sequence(StateSubactionMembership) =
            ownedMembership->
                selectByKind(StateSubactionMembership)->
                select(kind = StateSubactionKind::entry) in
        if entryMemberships->isEmpty() then null
        else entryMemberships->at(1)
        endif
    isParallel implies
        nestedAction.incomingTransition->isEmpty() and
        nestedAction.outgoingTransition->isEmpty()
    isSubstateUsage(true) implies
        specializesFromLibrary('States::State::substates')
    exitAction =
        let exitMemberships : Sequence(StateSubactionMembership) =
            ownedMembership->
                selectByKind(StateSubactionMembership)->
                select(kind = StateSubactionKind::exit) in
        if exitMemberships->isEmpty() then null
        else exitMemberships->at(1)
        endif
    specializesFromLibrary('States::StateAction')
    ownedMembership->
        selectByKind(StateSubactionMembership)->
        isUnique(kind)
    isSubstateUsage(false) implies
        specializesFromLibrary('States::State::substates')"""

    isParallel = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    stateDefinition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedStatedefinition,
    )
    _entryAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="entryAction",
        transient=True,
    )
    _doAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="doAction",
        transient=True,
    )
    _exitAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="exitAction",
        transient=True,
    )

    @property
    def entryAction(self):
        raise NotImplementedError("Missing implementation for entryAction")

    @entryAction.setter
    def entryAction(self, value):
        raise NotImplementedError("Missing implementation for entryAction")

    @property
    def doAction(self):
        raise NotImplementedError("Missing implementation for doAction")

    @doAction.setter
    def doAction(self, value):
        raise NotImplementedError("Missing implementation for doAction")

    @property
    def exitAction(self):
        raise NotImplementedError("Missing implementation for exitAction")

    @exitAction.setter
    def exitAction(self, value):
        raise NotImplementedError("Missing implementation for exitAction")

    def __init__(
        self,
        *,
        stateDefinition=None,
        entryAction=None,
        doAction=None,
        exitAction=None,
        isParallel=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if isParallel is not None:
            self.isParallel = isParallel

        if stateDefinition:
            self.stateDefinition.extend(stateDefinition)

        if entryAction is not None:
            self.entryAction = entryAction

        if doAction is not None:
            self.doAction = doAction

        if exitAction is not None:
            self.exitAction = exitAction

    def isSubstateUsage(self, isParallel=None):
        """<p>Check if this <code>StateUsage</code> is composite and has an <code>owningType</code> that is an <code>StateDefinition</code> or <code>StateUsage</code> with the given value of <code>isParallel</code>, but is <em>not</em> an <code>entryAction</code> or <code>exitAction</code>. If so, then it represents a <code><em>StateAction</em></code> that is a <code><em>substate</em></code> or <code><em>exclusiveState</em></code> (for <code>isParallel = false</code>) of another <code><em>StateAction</em></code>.</p>
        owningType <> null and
        (owningType.oclIsKindOf(StateDefinition) and
            owningType.oclAsType(StateDefinition).isParallel = isParallel or
         owningType.oclIsKindOf(StateUsage) and
            owningType.oclAsType(StateUsage).isParallel = isParallel) and
        not owningFeatureMembership.oclIsKindOf(StateSubactionMembership)"""
        raise NotImplementedError("operation isSubstateUsage(...) not yet implemented")


class DerivedTriggeraction(EDerivedCollection):
    pass


class DerivedGuardexpression(EDerivedCollection):
    pass


class DerivedEffectaction(EDerivedCollection):
    pass


class TransitionUsage(ActionUsage):
    """<p>A <code>TransitionUsage</code> is an <code>ActionUsage<code> representing a triggered transition between <code>ActionUsages</code> or <code>StateUsages</code>. When triggered by a <code>triggerAction</code>, when its <code>guardExpression</code> is true, the <code>TransitionUsage</code> asserts that its <code>source</code> is exited, then its <code>effectAction</code> (if any) is performed, and then its <code>target</code> is entered.</p>

    <p>A <code>TransitionUsage<code> can be related to some of its <code>ownedFeatures</code> using <code>TransitionFeatureMembership</code> <code>Relationships</code>, corresponding to the <code>triggerAction</code>, <code>guardExpression</code> and <code>effectAction</code> of the <code>TransitionUsage</code>.</p>
    isComposite and owningType <> null and
    (owningType.oclIsKindOf(ActionDefinition) or
     owningType.oclIsKindOf(ActionUsage)) and
    not (owningType.oclIsKindOf(StateDefinition) or
         owningType.oclIsKindOf(StateUsage)) implies
        specializesFromLibrary("Actions::Action::decisionTransitionActions")
    isComposite and owningType <> null and
    (owningType.oclIsKindOf(StateDefinition) or
     owningType.oclIsKindOf(StateUsage)) implies
        specializesFromLibrary("States::State::stateTransitions")
    specializesFromLibrary("Actions::actions::transitionActions")
    source =
        if ownedMembership->isEmpty() then null
        else
            let member : Element =
                ownedMembership->at(1).memberElement in
            if not member.oclIsKindOf(ActionUsage) then null
            else member.oclAsKindOf(ActionUsage)
            endif
        endif
    target =
        if succession.targetFeature->isEmpty() then null
        else
            let targetFeature : Feature =
                succession.targetFeature->at(1) in
            if not targetFeature.oclIsKindOf(ActionUsage) then null
            else targetFeature.oclAsType(ActionUsage)
            endif
        endif
    triggerAction = ownedFeatureMembership->
        selectByKind(TransitionFeatureMembership)->
        select(kind = TransitionFeatureKind::trigger).transitionFeature->
        selectByKind(AcceptActionUsage)
    let successions : Sequence(Successions) =
        ownedMember->selectByKind(Succession) in
    successions->notEmpty() and
    successions->at(1).targetFeature->
        forAll(oclIsKindOf(ActionUsage))
    guardExpression = ownedFeatureMembership->
        selectByKind(TransitionFeatureMembership)->
        select(kind = TransitionFeatureKind::trigger).transitionFeature->
        selectByKind(Expression)
    triggerAction->forAll(specializesFromLibrary('Actions::TransitionAction::accepter') and
    guardExpression->forAll(specializesFromLibrary('Actions::TransitionAction::guard') and
    effectAction->forAll(specializesFromLibrary('Actions::TransitionAction::effect'))
    triggerAction = ownedFeatureMembership->
        selectByKind(TransitionFeatureMembership)->
        select(kind = TransitionFeatureKind::trigger).transitionFeatures->
        selectByKind(AcceptActionUsage)
    succession.sourceFeature = source
    ownedMember->selectByKind(BindingConnector)->exists(b |
        b.relatedFeatures->includes(source) and
        b.relatedFeatures->includes(inputParameter(2)))
    triggerAction->notEmpty() implies
        let payloadParameter : Feature = inputParameter(2) in
        payloadParameter <> null and
        payloadParameter.subsetsChain(triggerAction->at(1), triggerPayloadParameter())
    ownedMember->selectByKind(BindingConnector)->exists(b |
        b.relatedFeatures->includes(succession) and
        b.relatedFeatures->includes(resolveGlobal(
            'TransitionPerformances::TransitionPerformance::transitionLink')))
    if triggerAction->isEmpty() then
        inputParameters()->size() >= 1
    else
        inputParameters()->size() >= 2
    endif

    succession = ownedMember->selectByKind(Succession)->at(1)"""

    _source = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="source",
        transient=True,
    )
    _target = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="target",
        transient=True,
    )
    triggerAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedTriggeraction,
    )
    guardExpression = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedGuardexpression,
    )
    effectAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedEffectaction,
    )
    _succession = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="succession",
        transient=True,
    )

    @property
    def source(self):
        raise NotImplementedError("Missing implementation for source")

    @source.setter
    def source(self, value):
        raise NotImplementedError("Missing implementation for source")

    @property
    def target(self):
        raise NotImplementedError("Missing implementation for target")

    @target.setter
    def target(self, value):
        raise NotImplementedError("Missing implementation for target")

    @property
    def succession(self):
        raise NotImplementedError("Missing implementation for succession")

    @succession.setter
    def succession(self, value):
        raise NotImplementedError("Missing implementation for succession")

    def __init__(
        self,
        *,
        source=None,
        target=None,
        triggerAction=None,
        guardExpression=None,
        effectAction=None,
        succession=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if source is not None:
            self.source = source

        if target is not None:
            self.target = target

        if triggerAction:
            self.triggerAction.extend(triggerAction)

        if guardExpression:
            self.guardExpression.extend(guardExpression)

        if effectAction:
            self.effectAction.extend(effectAction)

        if succession is not None:
            self.succession = succession

    def triggerPayloadParameter(self):
        """<p>Return the <code>payloadParameter</code> of the <code>triggerAction</code> of this <code>TransitionUsage</code>, if it has one.</p>
        if triggerAction->isEmpty() then null
        else triggerAction->first().payloadParameter
        endif"""
        raise NotImplementedError(
            "operation triggerPayloadParameter(...) not yet implemented"
        )


class AcceptActionUsage(ActionUsage):
    """<p>An <code>AcceptActionUsage</code> is an <code>ActionUsage</code> that specifies the acceptance of an <em><code>incomingTransfer</code></em> from the <code><em>Occurrence</em></code> given by the result of its <code>receiverArgument</code> Expression. (If no <code>receiverArgument</code> is provided, the default is the <em><code>this</code></em> context of the AcceptActionUsage.) The payload of the accepted <em><code>Transfer</em></code> is output on its <code>payloadParameter</code>. Which <em><code>Transfers</em></code> may be accepted is determined by conformance to the typing and (potentially) binding of the <code>payloadParameter</code>.</p>

    inputParameters()->size() >= 2
    receiverArgument = argument(2)
    payloadArgument = argument(1)
    payloadParameter =
     if parameter->isEmpty() then null
     else parameter->first() endif
    not isTriggerAction() implies
        specializesFromLibrary('Actions::acceptActions')
    isSubactionUsage() and not isTriggerAction() implies
        specializesFromLibrary('Actions::Action::acceptSubactions')
    isTriggerAction() implies
        specializesFromLibrary('Actions::TransitionAction::accepter')
    payloadArgument <> null and
    payloadArgument.oclIsKindOf(TriggerInvocationExpression) implies
        let invocation : Expression =
            payloadArgument.oclAsType(Expression) in
        parameter->size() >= 2 and
        invocation.parameter->size() >= 2 and
        ownedFeature->selectByKind(BindingConnector)->exists(b |
            b.relatedFeatures->includes(parameter->at(2)) and
            b.relatedFeatures->includes(invocation.parameter->at(2)))"""

    _receiverArgument = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="receiverArgument",
        transient=True,
    )
    _payloadParameter = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="payloadParameter",
        transient=True,
    )
    _payloadArgument = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="payloadArgument",
        transient=True,
    )

    @property
    def receiverArgument(self):
        raise NotImplementedError("Missing implementation for receiverArgument")

    @receiverArgument.setter
    def receiverArgument(self, value):
        raise NotImplementedError("Missing implementation for receiverArgument")

    @property
    def payloadParameter(self):
        raise NotImplementedError("Missing implementation for payloadParameter")

    @payloadParameter.setter
    def payloadParameter(self, value):
        raise NotImplementedError("Missing implementation for payloadParameter")

    @property
    def payloadArgument(self):
        raise NotImplementedError("Missing implementation for payloadArgument")

    @payloadArgument.setter
    def payloadArgument(self, value):
        raise NotImplementedError("Missing implementation for payloadArgument")

    def __init__(
        self,
        *,
        receiverArgument=None,
        payloadParameter=None,
        payloadArgument=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if receiverArgument is not None:
            self.receiverArgument = receiverArgument

        if payloadParameter is not None:
            self.payloadParameter = payloadParameter

        if payloadArgument is not None:
            self.payloadArgument = payloadArgument

    def isTriggerAction(self):
        """<p>Check if this <code>AcceptActionUsage</code> is the <code>triggerAction</code> of a <code>TransitionUsage</code>.</p>
        owningType <> null and
        owningType.oclIsKindOf(TransitionUsage) and
        owningType.oclAsType(TransitionUsage).triggerAction->includes(self)"""
        raise NotImplementedError("operation isTriggerAction(...) not yet implemented")


class DerivedAction(EDerivedCollection):
    pass


class ActionDefinition(OccurrenceDefinition, Behavior):
    """<p>An <code>ActionDefinition</code> is a <code>Definition</code> that is also a <code>Behavior</code> that defines an <em><code>Action</code></em> performed by a system or part of a system.</p>
    specializesFromLibrary('Actions::Action')
    action = usage->selectByKind(ActionUsage)"""

    action = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedAction,
    )

    def __init__(self, *, action=None, **kwargs):
        super().__init__(**kwargs)

        if action:
            self.action.extend(action)


class DerivedSatisfiedviewpoint(EDerivedCollection):
    pass


class DerivedExposedelement(EDerivedCollection):
    pass


class DerivedViewcondition(EDerivedCollection):
    pass


class DerivedItemdefinition(EDerivedCollection):
    pass


class ItemUsage(OccurrenceUsage):
    """<p>An <code>ItemUsage</code> is a <code>ItemUsage</code> whose <code>definition</code> is a <code>Structure</code>. Nominally, if the <code>definition</code> is an <code>ItemDefinition</code>, an <code>ItemUsage</code> is a <code>ItemUsage</code> of that <code>ItemDefinition</code> within a system. However, other kinds of Kernel <code>Structures</code> are also allowed, to permit use of <code>Structures</code> from the Kernel Model Libraries.</p>
    itemDefinition = occurrenceDefinition->selectByKind(ItemDefinition)
    specializesFromLibrary("Items::items")
    isComposite and owningType <> null and
    (owningType.oclIsKindOf(ItemDefinition) or
     owningType.oclIsKindOf(ItemUsage)) implies
        specializesFromLibrary("Items::Item::subitem")"""

    itemDefinition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedItemdefinition,
    )

    def __init__(self, *, itemDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if itemDefinition:
            self.itemDefinition.extend(itemDefinition)


class DerivedPartdefinition(EDerivedCollection):
    pass


class PartUsage(ItemUsage):
    """<p>A <code>PartUsage</code> is a usage of a <code>PartDefinition</code> to represent a system or a part of a system. At least one of the <code>itemDefinitions</code> of the <code>PartUsage</code> must be a <code>PartDefinition</code>.</p>

    <p>A <code>PartUsage</code> must subset, directly or indirectly, the base <code>PartUsage</code> <em><code>parts</code></em> from the Systems Model Library.</p>
    itemDefinition->selectByKind(PartDefinition)
    partDefinition->notEmpty()
    specializesFromLibrary("Parts::parts")
    isComposite and owningType <> null and
    (owningType.oclIsKindOf(ItemDefinition) or
     owningType.oclIsKindOf(ItemUsage)) implies
        specializesFromLibrary("Items::Item::subparts")
    owningFeatureMembership <> null and
    owningFeatureMembership.oclIsKindOf(ActorMembership) implies
        if owningType.oclIsKindOf(RequirementDefinition) or
           owningType.oclIsKindOf(RequirementUsage)
        then specializesFromLibrary('Requirements::RequirementCheck::actors')
        else specializesFromLibrary('Cases::Case::actors')
    owningFeatureMembership <> null and
    owningFeatureMembership.oclIsKindOf(StakeholderMembership) implies
        specializesFromLibrary('Requirements::RequirementCheck::stakeholders')"""

    partDefinition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedPartdefinition,
    )

    def __init__(self, *, partDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if partDefinition:
            self.partDefinition.extend(partDefinition)


class ViewUsage(PartUsage):
    """<p>A <code>ViewUsage</code> is a usage of a <code>ViewDefinition</code> to specify the generation of a view of the <code>members</code> of a collection of <code>exposedNamespaces</code>. The <code>ViewUsage</code> can satisfy more <code>viewpoints</code> than its definition, and it can specialize the <code>viewRendering</code> specified by its definition.<p>
    exposedElement = ownedImport->selectByKind(Expose).
        importedMemberships(Set{}).memberElement->
        select(elm | includeAsExposed(elm))->
        asOrderedSet()
    satisfiedViewpoint = ownedRequirement->
        selectByKind(ViewpointUsage)->
        select(isComposite)
    viewCondition = featureMembership->
        selectByKind(ElementFilterMembership).
        condition
    viewRendering =
        let renderings: OrderedSet(ViewRenderingMembership) =
            featureMembership->selectByKind(ViewRenderingMembership) in
        if renderings->isEmpty() then null
        else renderings->first().referencedRendering
        endif
    featureMembership->
        selectByKind(ViewRenderingMembership)->
        size() <= 1
    specializesFromLibrary('Views::views')
    owningType <> null and
    (owningType.oclIsKindOf(ViewDefinition) or
     owningType.oclIsKindOf(ViewUsage)) implies
        specializesFromLibrary('Views::View::subviews')"""

    _viewDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="viewDefinition",
        transient=True,
    )
    satisfiedViewpoint = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedSatisfiedviewpoint,
    )
    exposedElement = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedExposedelement,
    )
    _viewRendering = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="viewRendering",
        transient=True,
    )
    viewCondition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedViewcondition,
    )

    @property
    def viewDefinition(self):
        raise NotImplementedError("Missing implementation for viewDefinition")

    @viewDefinition.setter
    def viewDefinition(self, value):
        raise NotImplementedError("Missing implementation for viewDefinition")

    @property
    def viewRendering(self):
        raise NotImplementedError("Missing implementation for viewRendering")

    @viewRendering.setter
    def viewRendering(self, value):
        raise NotImplementedError("Missing implementation for viewRendering")

    def __init__(
        self,
        *,
        viewDefinition=None,
        satisfiedViewpoint=None,
        exposedElement=None,
        viewRendering=None,
        viewCondition=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if viewDefinition is not None:
            self.viewDefinition = viewDefinition

        if satisfiedViewpoint:
            self.satisfiedViewpoint.extend(satisfiedViewpoint)

        if exposedElement:
            self.exposedElement.extend(exposedElement)

        if viewRendering is not None:
            self.viewRendering = viewRendering

        if viewCondition:
            self.viewCondition.extend(viewCondition)

    def includeAsExposed(self, element=None):
        """<p>Determine whether the given <code>element</code> meets all the owned and inherited <code>viewConditions</code>.</p>
        let metadataFeatures: Sequence(AnnotatingElement) =
            element.ownedAnnotation.annotatingElement->
                select(oclIsKindOf(MetadataFeature)) in
        self.membership->selectByKind(ElementFilterMembership).
            condition->forAll(cond |
                metadataFeatures->exists(elem |
                    cond.checkCondition(elem)))"""
        raise NotImplementedError("operation includeAsExposed(...) not yet implemented")


class RenderingUsage(PartUsage):
    """<p>A <code>RenderingUsage</code> is the usage of a <code>RenderingDefinition</code> to specify the rendering of a specific model view to produce a physical view artifact.</p>


    specializeFromLibrary('Views::renderings')
    owningType <> null and
    (owningType.oclIsKindOf(RenderingDefinition) or
     owningType.oclIsKindOf(RenderingUsage)) implies
        specializesFromLibrary('Views::Rendering::subrenderings')
    owningFeatureMembership <> null and
    owningFeatureMembership.oclIsKindOf(ViewRenderingMembership) implies
        redefinesFromLibrary('Views::View::viewRendering')"""

    _renderingDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="renderingDefinition",
        transient=True,
    )

    @property
    def renderingDefinition(self):
        raise NotImplementedError("Missing implementation for renderingDefinition")

    @renderingDefinition.setter
    def renderingDefinition(self, value):
        raise NotImplementedError("Missing implementation for renderingDefinition")

    def __init__(self, *, renderingDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if renderingDefinition is not None:
            self.renderingDefinition = renderingDefinition


@abstract
class ControlNode(ActionUsage):
    """<p>A <code>ControlNode</code> is an <code>ActionUsage</code> that does not have any inherent behavior but provides constraints on incoming and outgoing <code>Successions</code> that are used to control other <code>Actions</code>. A <code>ControlNode</code> must be a composite owned <code>usage</code> of an <code>ActionDefinition</code> or <code>ActionUsage</code>.</p>

    sourceConnector->selectByKind(Succession)->
        collect(connectorEnd->at(1).multiplicity)->
        forAll(sourceMult |
            multiplicityHasBounds(sourceMult, 1, 1))
    owningType <> null and
    (owningType.oclIsKindOf(ActionDefinition) or
     owningType.oclIsKindOf(ActionUsage))
    targetConnector->selectByKind(Succession)->
        collect(connectorEnd->at(2).multiplicity)->
        forAll(targetMult |
            multiplicityHasBounds(targetMult, 1, 1))
    specializesFromLibrary('Action::Action::controls')"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def multiplicityHasBounds(self, mult=None, lower=None, upper=None):
        """<p>Check that the given <code>Multiplicity</code> has <code>lowerBound</code> and <code>upperBound</code> expressions that are model-level evaluable to the given <code>lower</code> and <code>upper</code> values.</p>
        mult <> null and
        if mult.oclIsKindOf(MultiplicityRange) then
            mult.oclAsType(MultiplicityRange).hasBounds(lower, upper)
        else
            mult.allSuperTypes()->exists(
                oclisKindOf(MultiplicityRange) and
                oclAsType(MultiplicityRange).hasBounds(lower, upper)
        endif"""
        raise NotImplementedError(
            "operation multiplicityHasBounds(...) not yet implemented"
        )


@abstract
class LoopActionUsage(ActionUsage):
    """<p>A <code>LoopActionUsage</code> is an <code>ActionUsage</code> that specifies that its <code>bodyAction</code> should be performed repeatedly. Its subclasses <code>WhileLoopActionUsage</code> and <code>ForLoopActionUsage</code> provide different ways to determine how many times the <code>bodyAction</code> should be performed.</p>
    bodyAction =
        let parameter : Feature = inputParameter(2) in
        if parameter <> null and parameter.oclIsKindOf(Action) then
            parameter.oclAsType(Action)
        else
            null
        endif"""

    _bodyAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="bodyAction",
        transient=True,
    )

    @property
    def bodyAction(self):
        raise NotImplementedError("Missing implementation for bodyAction")

    @bodyAction.setter
    def bodyAction(self, value):
        raise NotImplementedError("Missing implementation for bodyAction")

    def __init__(self, *, bodyAction=None, **kwargs):
        super().__init__(**kwargs)

        if bodyAction is not None:
            self.bodyAction = bodyAction


class AssignmentActionUsage(ActionUsage):
    """<p>An <code>AssignmentActionUsage</code> is an <code>ActionUsage</code> that is defined, directly or indirectly, by the <code>ActionDefinition</code> <em><code>AssignmentAction</code></em> from the Systems Model Library. It specifies that the value of the <code>referent</code> <code>Feature</code>, relative to the target given by the result of the <code>targetArgument</code> <code>Expression</code>, should be set to the result of the <code>valueExpression</code>.</p>

    specializesFromLibrary('Actions::assignmentActions')
    let targetParameter : Feature = inputParameter(1) in
    targetParameter <> null and
    targetParameter.ownedFeature->notEmpty() and
    targetParameter.ownedFeature->first().
        redefines('AssignmentAction::target::startingAt')
    valueExpression = argument(2)
    targetArgument = argument(1)
    isSubactionUsage() implies
        specializesFromLibrary('Actions::Action::assignments')
    let targetParameter : Feature = inputParameter(1) in
    targetParameter <> null and
    targetParameter.ownedFeature->notEmpty() and
    targetParameter->first().ownedFeature->notEmpty() and
    targetParameter->first().ownedFeature->first().
        redefines('AssigmentAction::target::startingAt::accessedFeature')
    let targetParameter : Feature = inputParameter(1) in
    targetParameter <> null and
    targetParameter.ownedFeature->notEmpty() and
    targetParameter->first().ownedFeature->notEmpty() and
    targetParameter->first().ownedFeature->first().redefines(referent)
    referent =
        let unownedFeatures : Sequence(Feature) = ownedMembership->
            reject(oclIsKindOf(OwningMembership)).memberElement->
            selectByKind(Feature) in
        if unownedFeatures->isEmpty() then null
        else unownedFeatures->first().oclAsType(Feature)
        endif"""

    _targetArgument = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="targetArgument",
        transient=True,
    )
    _valueExpression = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="valueExpression",
        transient=True,
    )
    _referent = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="referent",
        transient=True,
    )

    @property
    def targetArgument(self):
        raise NotImplementedError("Missing implementation for targetArgument")

    @targetArgument.setter
    def targetArgument(self, value):
        raise NotImplementedError("Missing implementation for targetArgument")

    @property
    def valueExpression(self):
        raise NotImplementedError("Missing implementation for valueExpression")

    @valueExpression.setter
    def valueExpression(self, value):
        raise NotImplementedError("Missing implementation for valueExpression")

    @property
    def referent(self):
        raise NotImplementedError("Missing implementation for referent")

    @referent.setter
    def referent(self, value):
        raise NotImplementedError("Missing implementation for referent")

    def __init__(
        self, *, targetArgument=None, valueExpression=None, referent=None, **kwargs
    ):
        super().__init__(**kwargs)

        if targetArgument is not None:
            self.targetArgument = targetArgument

        if valueExpression is not None:
            self.valueExpression = valueExpression

        if referent is not None:
            self.referent = referent


class IfActionUsage(ActionUsage):
    """<p>An <code>IfActionUsage</code> is an <code>ActionUsage</code> that specifies that the <code>thenAction</code> <code>ActionUsage</code> should be performed if the result of the <code>ifArgument</code> <code>Expression</code> is true. It may also optionally specify an <code>elseAction</code> <code>ActionUsage</code> that is performed if the result of the <code>ifArgument</code> is false.</p>
    thenAction =
        let parameter : Feature = inputParameter(2) in
        if parameter <> null and parameter.oclIsKindOf(ActionUsage) then
            parameter.oclAsType(ActionUsage)
        else
            null
        endif
    isSubactionUsage() implies
        specializesFromLibrary('Actions::Action::ifSubactions')
    if elseAction = null then
        specifiesFromLibrary('Actions::ifThenActions')
    else
        specifiesFromLibrary('Actions::ifThenElseActions')
    endif
    ifArgument =
        let parameter : Feature = inputParameter(1) in
        if parameter <> null and parameter.oclIsKindOf(Expression) then
            parameter.oclAsType(Expression)
        else
            null
        endif
    elseAction =
        let parameter : Feature = inputParameter(3) in
        if parameter <> null and parameter.oclIsKindOf(ActionUsage) then
            parameter.oclAsType(ActionUsage)
        else
            null
        endif"""

    _elseAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="elseAction",
        transient=True,
    )
    _thenAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="thenAction",
        transient=True,
    )
    _ifArgument = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ifArgument",
        transient=True,
    )

    @property
    def elseAction(self):
        raise NotImplementedError("Missing implementation for elseAction")

    @elseAction.setter
    def elseAction(self, value):
        raise NotImplementedError("Missing implementation for elseAction")

    @property
    def thenAction(self):
        raise NotImplementedError("Missing implementation for thenAction")

    @thenAction.setter
    def thenAction(self, value):
        raise NotImplementedError("Missing implementation for thenAction")

    @property
    def ifArgument(self):
        raise NotImplementedError("Missing implementation for ifArgument")

    @ifArgument.setter
    def ifArgument(self, value):
        raise NotImplementedError("Missing implementation for ifArgument")

    def __init__(self, *, elseAction=None, thenAction=None, ifArgument=None, **kwargs):
        super().__init__(**kwargs)

        if elseAction is not None:
            self.elseAction = elseAction

        if thenAction is not None:
            self.thenAction = thenAction

        if ifArgument is not None:
            self.ifArgument = ifArgument


class SendActionUsage(ActionUsage):
    """<p>A <code>SendActionUsage</code> is an <code>ActionUsage</code> that specifies the sending of a payload given by the result of its <code>payloadArgument</code> <code>Expression</code> via a <em><code>MessageTransfer</code></em> whose <em><code>source</code></em> is given by the result of the <code>senderArgument</code> <code>Expression</code> and whose <code>target</code> is given by the result of the <code>receiverArgument</code> <code>Expression</code>. If no <code>senderArgument</code> is provided, the default is the <em><code>this</code></em> context for the action. If no <code>receiverArgument</code> is given, then the receiver is to be determined by, e.g., outgoing <em><code>Connections</code></em> from the sender.</p>

    senderArgument = argument(2)
    payloadArgument = argument(1)
    inputParameters()->size() >= 3
    receiverArgument = argument(3)
    isSubactionUsage() implies
        specializesFromLibrary('Actions::Action::acceptSubactions')
    specializesFromLibrary("Actions::sendActions")"""

    _receiverArgument = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="receiverArgument",
        transient=True,
    )
    _payloadArgument = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="payloadArgument",
        transient=True,
    )
    _senderArgument = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="senderArgument",
        transient=True,
    )

    @property
    def receiverArgument(self):
        raise NotImplementedError("Missing implementation for receiverArgument")

    @receiverArgument.setter
    def receiverArgument(self, value):
        raise NotImplementedError("Missing implementation for receiverArgument")

    @property
    def payloadArgument(self):
        raise NotImplementedError("Missing implementation for payloadArgument")

    @payloadArgument.setter
    def payloadArgument(self, value):
        raise NotImplementedError("Missing implementation for payloadArgument")

    @property
    def senderArgument(self):
        raise NotImplementedError("Missing implementation for senderArgument")

    @senderArgument.setter
    def senderArgument(self, value):
        raise NotImplementedError("Missing implementation for senderArgument")

    def __init__(
        self,
        *,
        receiverArgument=None,
        payloadArgument=None,
        senderArgument=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if receiverArgument is not None:
            self.receiverArgument = receiverArgument

        if payloadArgument is not None:
            self.payloadArgument = payloadArgument

        if senderArgument is not None:
            self.senderArgument = senderArgument


class SelectExpression(OperatorExpression):
    """<p>A <code>SelectExpression</code> is an <code>OperatorExpression</code> whose operator is <code>"select"</code>, which resolves to the <code>Function</code> <em><code>ControlFunctions::select</code></em> from the Kernel Functions Library.</p>"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CollectExpression(OperatorExpression):
    """<p>A <code>CollectExpression</code> is an <code>OperatorExpression</code> whose <code>operator</code> is <code>"collect"</code>, which resolves to the <code>Function</code> <em><code>ControlFunctions::collect</code></em> from the Kernel Functions Library.</p>
    operator = 'collect'"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FeatureChainExpression(OperatorExpression):
    """<p>A <code>FeatureChainExpression</code> is an <code>OperatorExpression</code> whose operator is <code>"."</code>, which resolves to the <code>Function</code> <em><code>ControlFunctions::'.'</code></em> from the Kernel Functions Library. It evaluates to the result of chaining the <code>result</code> <code>Feature</code> of its single <code>argument</code> <code>Expression</code> with its <code>targetFeature</code>.</p>
    let sourceParameter : Feature = sourceTargetFeature() in
    sourceTargetFeature <> null and
    sourceTargetFeature.redefinesFromLibrary("ControlFunctions::'.'::source::target")
    let sourceParameter : Feature = sourceTargetFeature() in
    sourceTargetFeature <> null and
    sourceTargetFeature.redefines(targetFeature)
    targetFeature =
        let nonParameterMemberships : Sequence(Membership) = ownedMembership->
            reject(oclIsKindOf(ParameterMembership)) in
        if nonParameterMemberships->isEmpty() or
           not nonParameterMemberships->first().memberElement.oclIsKindOf(Feature)
        then null
        else nonParameterMemberships->first().memberElement.oclAsType(Feature)
        endif"""

    _targetFeature = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="targetFeature",
        transient=True,
    )

    @property
    def targetFeature(self):
        raise NotImplementedError("Missing implementation for targetFeature")

    @targetFeature.setter
    def targetFeature(self, value):
        raise NotImplementedError("Missing implementation for targetFeature")

    def __init__(self, *, targetFeature=None, **kwargs):
        super().__init__(**kwargs)

        if targetFeature is not None:
            self.targetFeature = targetFeature

    def sourceTargetFeature(self):
        """<p>Return the first <code>ownedFeature</code> of the first owned input <code>parameter</code> of this <code>FeatureChainExpression</code> (if any).</p>
        let inputParameters : Feature = ownedFeatures->
            select(direction = _'in') in
        if inputParameters->isEmpty() or
           inputParameters->first().ownedFeature->isEmpty()
        then null
        else inputParameters->first().ownedFeature->first()
        endif"""
        raise NotImplementedError(
            "operation sourceTargetFeature(...) not yet implemented"
        )


class PartDefinition(ItemDefinition):
    """<p>A <code>PartDefinition</code> is an <code>ItemDefinition</code> of a <code>Class</code> of systems or parts of systems. Note that all parts may be considered items for certain purposes, but not all items are parts that can perform actions within a system.</p>

    specializesFromLibrary("Parts::Part")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ConjugatedPortDefinition(PortDefinition):
    """<p>A <code>ConjugatedPortDefinition</code> is a <code>PortDefinition</code> that is a <code>PortDefinition</code> of its original <code>PortDefinition</code>. That is, a <code>ConjugatedPortDefinition</code> inherits all the <code>features</code> of the original <code>PortDefinition</code>, but input <code>flows</code> of the original <code>PortDefinition</code> become outputs on the <code>ConjugatedPortDefinition</code> and output <code>flows</code> of the original <code>PortDefinition</code> become inputs on the <code>ConjugatedPortDefinition</code>. Every <code>PortDefinition</code> (that is not itself a <code><code>ConjugatedPortDefinition</code></code>) has exactly one corresponding <code>ConjugatedPortDefinition</code>, whose effective name is the name of the <code>originalPortDefinition</code>, with the character <code>~</code> prepended.</p>
    ownedPortConjugator.originalPortDefinition = originalPortDefinition
    conjugatedPortDefinition = null"""

    _ownedPortConjugator = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedPortConjugator",
        transient=True,
    )
    _originalPortDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="originalPortDefinition",
        transient=True,
    )

    @property
    def ownedPortConjugator(self):
        raise NotImplementedError("Missing implementation for ownedPortConjugator")

    @ownedPortConjugator.setter
    def ownedPortConjugator(self, value):
        raise NotImplementedError("Missing implementation for ownedPortConjugator")

    @property
    def originalPortDefinition(self):
        raise NotImplementedError("Missing implementation for originalPortDefinition")

    @originalPortDefinition.setter
    def originalPortDefinition(self, value):
        raise NotImplementedError("Missing implementation for originalPortDefinition")

    def __init__(
        self, *, ownedPortConjugator=None, originalPortDefinition=None, **kwargs
    ):
        super().__init__(**kwargs)

        if ownedPortConjugator is not None:
            self.ownedPortConjugator = ownedPortConjugator

        if originalPortDefinition is not None:
            self.originalPortDefinition = originalPortDefinition


class CalculationUsage(ActionUsage, Expression):
    """<p>A <code>CalculationUsage</code> is an <code>ActionUsage<code> that is also an <code>Expression</code>, and, so, is typed by a <code>Function</code>. Nominally, if the <code>type</code> is a <code>CalculationDefinition</code>, a <code>CalculationUsage</code> is a <code>Usage</code> of that <code>CalculationDefinition</code> within a system. However, other kinds of kernel <code>Functions</code> are also allowed, to permit use of <code>Functions</code> from the Kernel Model Libraries.</p>
    specializesFromLibrary('Calculations::calculations')
    owningType <> null and
    (owningType.oclIsKindOf(CalculationDefinition) or
     owningType.oclIsKindOf(CalculationUsage)) implies
        specializesFromLibrary('Calculations::Calculation::subcalculations')"""

    _calculationDefinition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        name="calculationDefinition",
        transient=True,
    )

    @property
    def calculationDefinition(self):
        raise NotImplementedError("Missing implementation for calculationDefinition")

    @calculationDefinition.setter
    def calculationDefinition(self, value):
        raise NotImplementedError("Missing implementation for calculationDefinition")

    def __init__(self, *, calculationDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if calculationDefinition is not None:
            self.calculationDefinition = calculationDefinition


class ConstraintUsage(OccurrenceUsage, BooleanExpression):
    """<p>A <code>ConstraintUsage</code> is an <code>OccurrenceUsage</code> that is also a <code>BooleanExpression<code>, and, so, is typed by a <code>Predicate</code>. Nominally, if the type is a <code>ConstraintDefinition<code>, a <code>ConstraintUsage</code> is a <code>Usage</code> of that <code>ConstraintDefinition<code>. However, other kinds of kernel <code>Predicates</code> are also allowed, to permit use of <code>Predicates</code> from the Kernel Model Libraries.</p>
    owningFeatureMembership <> null and
    owningFeatureMembership.oclIsKindOf(RequirementConstraintMembership) implies
        if owningFeatureMembership.oclAsType(RequirementConstraintMembership).kind =
            RequirementConstraintKind::assumption then
            specializesFromLibrary('Requirements::RequirementCheck::assumptions')
        else
            specializesFromLibrary('Requirements::RequirementCheck::constraints')
        endif
    specializesFromLibrary('Constraints::constraintChecks')
    owningType <> null and
    (owningType.oclIsKindOf(ItemDefinition) or
     owningType.oclIsKindOf(ItemUsage)) implies
        specializesFromLibrary('Items::Item::checkedConstraints')"""

    _constraintDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="constraintDefinition",
        transient=True,
    )

    @property
    def constraintDefinition(self):
        raise NotImplementedError("Missing implementation for constraintDefinition")

    @constraintDefinition.setter
    def constraintDefinition(self, value):
        raise NotImplementedError("Missing implementation for constraintDefinition")

    def __init__(self, *, constraintDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if constraintDefinition is not None:
            self.constraintDefinition = constraintDefinition


class MetadataUsage(ItemUsage, MetadataFeature):
    """<p>A  <code>MetadataUsage</code> is a <code>Usage</code> and a <code>MetadataFeature</code>, used to annotate other <code>Elements</code> in a system model with metadata. As a <code>MetadataFeature</code>, its type must be a <code>Metaclass</code>, which will nominally be a <code>MetadataDefinition</code>. However, any kernel <code>Metaclass</code> is also allowed, to permit use of <code>Metaclasses</code> from the Kernel Model Libraries.</p>
    specializesFromLibrary('Metadata::metadataItems')"""

    _metadataDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="metadataDefinition",
        transient=True,
    )

    @property
    def metadataDefinition(self):
        raise NotImplementedError("Missing implementation for metadataDefinition")

    @metadataDefinition.setter
    def metadataDefinition(self, value):
        raise NotImplementedError("Missing implementation for metadataDefinition")

    def __init__(self, *, metadataDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if metadataDefinition is not None:
            self.metadataDefinition = metadataDefinition


class BindingConnectorAsUsage(ConnectorAsUsage, BindingConnector):
    """<p>A <code>BindingConnectorAsUsage</code> is both a <code>BindingConnector</code> and a <code>ConnectorAsUsage</code>.</p>"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SuccessionItemFlow(ItemFlow, Succession):
    """<p>A <code>SuccessionItemFlow</code> is an <code>ItemFlow</code> that also provides temporal ordering. It classifies <code><em>Transfers</em></code> that cannot start until the source <code><em>Occurrence</em></code> has completed and that must complete before the target <code><em>Occurrence</em></code> can start.</p>
    specializesFromLibrary("Transfers::flowTransfersBefore")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SuccessionAsUsage(ConnectorAsUsage, Succession):
    """<p>A <code>SuccessionAsUsage</code> is both a <code>ConnectorAsUsage</code> and a <code>Succession</code>.<p>"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class JoinNode(ControlNode):
    """<p>A <code>JoinNode</code> is a <code>ControlNode</code> that waits for the completion of all the predecessor <code>Actions</code> given by incoming <code>Successions</code>.</p>
    sourceConnector->selectByKind(Succession)->size() <= 1
    specializesFromLibrary("Actions::Action::join")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ForkNode(ControlNode):
    """<p>A <code>ForkNode</code> is a <code>ControlNode</code> that must be followed by successor <code>Actions</code> as given by all its outgoing <code>Successions</code>.</p>
    targetConnector->selectByKind(Succession)->size() <= 1
    specializesFromLibrary("Actions::Action::forks")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MergeNode(ControlNode):
    """<p>A <code>MergeNode</code> is a <code>ControlNode</code> that asserts the merging of its incoming <code>Successions</code>. A <code>MergeNode</code> may have at most one outgoing <code>Successions</code>.</p>
    sourceConnector->selectAsKind(Succession)->size() <= 1
    targetConnector->selectByKind(Succession)->
        collect(connectorEnd->at(1))->
        forAll(sourceMult |
            multiplicityHasBounds(sourceMult, 0, 1))
    targetConnector->selectByKind(Succession)->
        forAll(subsetsChain(this,
            resolveGlobal("ControlPerformances::MergePerformance::incomingHBLink")))
    specializesFromLibrary("Actions::Action::merges")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ForLoopActionUsage(LoopActionUsage):
    """<p>A <code>ForLoopActionUsage</code> is a <code>LoopActionUsage</code> that specifies that its <code>bodyClause</code> <code>ActionUsage</code> should be performed once for each value, in order, from the sequence of values obtained as the result of the <code>seqArgument</code> <code>Expression</code>, with the <code>loopVariable</code> set to the value for each iteration.</p>
    seqArgument =
        let parameter : Feature = inputParameter(1) in
        if parameter <> null and parameter.oclIsKindOf(Expression) then
            parameter.oclAsType(Expression)
        else
            null
        endif

    isSubactionUsage() implies
        specializesFromLibrary('Actions::Action::forLoops')
    loopVariable <> null and
    loopVariable.redefinesFromLibrary('Actions::ForLoopAction::var')
    specializesFromLibrary('Actions::forLoopActions')
    loopVariable =
        if ownedFeature->isEmpty() or
            not ownedFeature->first().oclIsKindOf(ReferenceUsage) then
            null
        else
            ownedFeature->first().oclAsType(ReferenceUsage)
        endif"""

    _seqArgument = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="seqArgument",
        transient=True,
    )
    _loopVariable = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="loopVariable",
        transient=True,
    )

    @property
    def seqArgument(self):
        raise NotImplementedError("Missing implementation for seqArgument")

    @seqArgument.setter
    def seqArgument(self, value):
        raise NotImplementedError("Missing implementation for seqArgument")

    @property
    def loopVariable(self):
        raise NotImplementedError("Missing implementation for loopVariable")

    @loopVariable.setter
    def loopVariable(self, value):
        raise NotImplementedError("Missing implementation for loopVariable")

    def __init__(self, *, seqArgument=None, loopVariable=None, **kwargs):
        super().__init__(**kwargs)

        if seqArgument is not None:
            self.seqArgument = seqArgument

        if loopVariable is not None:
            self.loopVariable = loopVariable


class EventOccurrenceUsage(OccurrenceUsage):
    """<p>An <code>EventOccurrenceUsage</code> is an <code>OccurrenceUsage</code> that represents another <code>OccurrenceUsage<code> occurring as a <code><em>suboccurrence<em></code> of the containing occurrence of the <code>EventOccurrenceUsage</code>. Unless it is the <code>EventOccurrenceUsage</code> itself, the referenced <code>OccurrenceUsage</code> is related to the <code>EventOccurrenceUsage<code> by a <code>ReferenceSubsetting</code> <code>Relationship</code>.</p>

    <p>If the <code>EventOccurrenceUsage</code> is owned by an <code>OccurrenceDefinition</code> or <code>OccurrenceUsage</code>, then it also subsets the <em><code>timeEnclosedOccurrences</code></em> property of the <code>Class</code> <em><code>Occurrence</code></em> from the Kernel Semantic Library model <em><code>Occurrences</code></em>.</p>
    eventOccurrence =
        if ownedReferenceSubsetting = null then self
        else if ownedReferenceSubsetting.referencedFeature.oclIsKindOf(OccurrenceUsage) then
            ownedReferenceSubsetting.referencedFeature.oclAsType(OccurrenceUsage)
        else null
        endif endif
    ownedReferenceSubsetting <> null implies
        ownedReferenceSubsetting.referencedFeature.oclIsKindOf(OccurrenceUsage)
    owningType <> null and
    (owningType.oclIsKindOf(OccurrenceDefinition) or
     owningType.oclIsKindOf(OccurrenceUsage)) implies
        specializesFromLibrary("Occurrences::Occurrence::timeEnclosedOccurrences")
    isReference"""

    _eventOccurrence = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="eventOccurrence",
        transient=True,
    )

    @property
    def eventOccurrence(self):
        raise NotImplementedError("Missing implementation for eventOccurrence")

    @eventOccurrence.setter
    def eventOccurrence(self, value):
        raise NotImplementedError("Missing implementation for eventOccurrence")

    def __init__(self, *, eventOccurrence=None, **kwargs):
        super().__init__(**kwargs)

        if eventOccurrence is not None:
            self.eventOccurrence = eventOccurrence


class PerformActionUsage(ActionUsage, EventOccurrenceUsage):
    """<p>A <code>PerformActionUsage</code> is an <code>ActionUsage</code> that represents the performance of an <code>ActionUsage</code>. Unless it is the <code>PerformActionUsage</code> itself, the <code>ActionUsage</code> to be performed is related to the <code>PerformActionUsage</code> by a <code>ReferenceSubsetting</code> relationship. A <code>PerformActionUsage</code> is also an <code>EventOccurrenceUsage</code>, with its <code>performedAction</code> as the <code>eventOccurrence</code>.</p>
    ownedReferenceSubsetting <> null implies
        ownedReferenceSubsetting.referencedFeature.oclIsKindOf(ActionUsage)
    owningType <> null and
    (owningType.oclIsKindOf(PartDefinition) or
     owningType.oclIsKindOf(PartUsage)) implies
        specializesFromLibrary('Parts::Part::performedActions')"""

    _performedAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="performedAction",
        transient=True,
    )

    @property
    def performedAction(self):
        raise NotImplementedError("Missing implementation for performedAction")

    @performedAction.setter
    def performedAction(self, value):
        raise NotImplementedError("Missing implementation for performedAction")

    def __init__(self, *, performedAction=None, **kwargs):
        super().__init__(**kwargs)

        if performedAction is not None:
            self.performedAction = performedAction


class DecisionNode(ControlNode):
    """<p>A <code>DecisionNode</code> is a <code>ControlNode</code> that makes a selection from its outgoing <code>Successions</code>.</p>
    targetConnector->selectByKind(Succession)->size() <= 1
    sourceConnector->selectAsKind(Succession)->
        collect(connectorEnd->at(2))->
        forAll(targetMult |
            multiplicityHasBounds(targetMult, 0, 1))
    specializesFromLibrary("Actions::Action::decisions")
    sourceConnector->selectByKind(Succession)->
        forAll(subsetsChain(this,
            resolveGlobal("ControlPerformances::MergePerformance::outgoingHBLink")))"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class WhileLoopActionUsage(LoopActionUsage):
    """<p>A <code>WhileLoopActionUsage</code> is a <code>LoopActionUsage</code> that specifies that the <code>bodyClause</code> <code>ActionUsage</code> should be performed repeatedly while the result of the <code>whileArgument</code> <code>Expression</code> is true or until the result of the <code>untilArgument</code> <code>Expression</code> (if provided) is true. The <code>whileArgument</code> <code>Expression</code> is evaluated before each (possible) performance of the <code>bodyClause</code>, and the <code>untilArgument</code> <code>Expression</code> is evaluated after each performance of the <code>bodyClause</code>.</p>
    isSubactionUsage() implies
        specializesFromLibrary('Actions::Action::whileLoops')
    untilArgument =
        let parameter : Feature = inputParameter(3) in
        if parameter <> null and parameter.oclIsKindOf(Expression) then
            parameter.oclAsType(Expression)
        else
            null
        endif

    specializesFromLibrary('Actions::whileLoopActions')
    whileArgument =
        let parameter : Feature = inputParameter(1) in
        if parameter <> null and parameter.oclIsKindOf(Expression) then
            parameter.oclAsType(Expression)
        else
            null
        endif"""

    _whileArgument = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="whileArgument",
        transient=True,
    )
    _untilArgument = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="untilArgument",
        transient=True,
    )

    @property
    def whileArgument(self):
        raise NotImplementedError("Missing implementation for whileArgument")

    @whileArgument.setter
    def whileArgument(self, value):
        raise NotImplementedError("Missing implementation for whileArgument")

    @property
    def untilArgument(self):
        raise NotImplementedError("Missing implementation for untilArgument")

    @untilArgument.setter
    def untilArgument(self, value):
        raise NotImplementedError("Missing implementation for untilArgument")

    def __init__(self, *, whileArgument=None, untilArgument=None, **kwargs):
        super().__init__(**kwargs)

        if whileArgument is not None:
            self.whileArgument = whileArgument

        if untilArgument is not None:
            self.untilArgument = untilArgument


class DerivedState(EDerivedCollection):
    pass


class StateDefinition(ActionDefinition):
    """<p>A <code>StateDefinition</code> is the <code>Definition</code> of the </code>Behavior</code> of a system or part of a system in a certain state condition.</p>

    <p>A <code>StateDefinition</code> may be related to up to three of its <code>ownedFeatures</code> by <code>StateBehaviorMembership</cod> <code>Relationships</code>, all of different <code>kinds</code>, corresponding to the entry, do and exit actions of the <code>StateDefinition</code>.</p>
    ownedGeneralization.general->selectByKind(StateDefinition)->
        forAll(g | g.isParallel = isParallel)
    specializesFromLibrary('States::StateAction')
    ownedMembership->
        selectByKind(StateSubactionMembership)->
        isUnique(kind)
    state = action->selectByKind(StateUsage)
    doAction =
        let doMemberships : Sequence(StateSubactionMembership) =
            ownedMembership->
                selectByKind(StateSubactionMembership)->
                select(kind = StateSubactionKind::do) in
        if doMemberships->isEmpty() then null
        else doMemberships->at(1)
        endif
    entryAction =
        let entryMemberships : Sequence(StateSubactionMembership) =
            ownedMembership->
                selectByKind(StateSubactionMembership)->
                select(kind = StateSubactionKind::entry) in
        if entryMemberships->isEmpty() then null
        else entryMemberships->at(1)
        endif
    isParallel implies
        ownedAction.incomingTransition->isEmpty() and
        ownedAction.outgoingTransition->isEmpty()
    exitAction =
        let exitMemberships : Sequence(StateSubactionMembership) =
            ownedMembership->
                selectByKind(StateSubactionMembership)->
                select(kind = StateSubactionKind::exit) in
        if exitMemberships->isEmpty() then null
        else exitMemberships->at(1)
        endif"""

    isParallel = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    state = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedState,
    )
    _entryAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="entryAction",
        transient=True,
    )
    _doAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="doAction",
        transient=True,
    )
    _exitAction = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="exitAction",
        transient=True,
    )

    @property
    def entryAction(self):
        raise NotImplementedError("Missing implementation for entryAction")

    @entryAction.setter
    def entryAction(self, value):
        raise NotImplementedError("Missing implementation for entryAction")

    @property
    def doAction(self):
        raise NotImplementedError("Missing implementation for doAction")

    @doAction.setter
    def doAction(self, value):
        raise NotImplementedError("Missing implementation for doAction")

    @property
    def exitAction(self):
        raise NotImplementedError("Missing implementation for exitAction")

    @exitAction.setter
    def exitAction(self, value):
        raise NotImplementedError("Missing implementation for exitAction")

    def __init__(
        self,
        *,
        state=None,
        entryAction=None,
        doAction=None,
        exitAction=None,
        isParallel=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if isParallel is not None:
            self.isParallel = isParallel

        if state:
            self.state.extend(state)

        if entryAction is not None:
            self.entryAction = entryAction

        if doAction is not None:
            self.doAction = doAction

        if exitAction is not None:
            self.exitAction = exitAction


class DerivedText(EDerivedCollection):
    pass


class DerivedRequiredconstraint(EDerivedCollection):
    pass


class DerivedAssumedconstraint(EDerivedCollection):
    pass


class DerivedFramedconcern(EDerivedCollection):
    pass


class DerivedActorparameter(EDerivedCollection):
    pass


class DerivedStakeholderparameter(EDerivedCollection):
    pass


class RequirementUsage(ConstraintUsage):
    """<p>A <code>RequirementUsage</code> is a <code>Usage</code> of a <code>RequirementDefinition</code>.</p>
    actorParameter = featureMembership->
        selectByKind(ActorMembership).
        ownedActorParameter
    assumedConstraint = ownedFeatureMembership->
        selectByKind(RequirementConstraintMembership)->
        select(kind = RequirementConstraintKind::assumption).
        ownedConstraint
    framedConcern = featureMembership->
        selectByKind(FramedConcernMembership).
        ownedConcern
    requiredConstraint = ownedFeatureMembership->
        selectByKind(RequirementConstraintMembership)->
        select(kind = RequirementConstraintKind::requirement).
        ownedConstraint
    stakeholderParameter = featureMembership->
        selectByKind(AStakholderMembership).
        ownedStakeholderParameter
    subjectParameter =
        let subjects : OrderedSet(SubjectMembership) =
            featureMembership->selectByKind(SubjectMembership) in
        if subjects->isEmpty() then null
        else subjects->first().ownedSubjectParameter
        endif
    text = documentation.body
    featureMembership->
        selectByKind(SubjectMembership)->
        size() <= 1
    input->notEmpty() and input->first() = subjectParameter
    specializesFromLibrary('Requirements::requirementChecks')
    isComposite and owningType <> null and
        (owningType.oclIsKindOf(RequirementDefinition) or
         owningType.oclIsKindOf(RequirementUsage)) implies
        specializesFromLibrary('Requirements::RequirementCheck::subrequirements')
    owningfeatureMembership <> null and
    owningfeatureMembership.oclIsKindOf(ObjectiveMembership) implies
        owningType.ownedSpecialization.general->forAll(gen |
            (gen.oclIsKindOf(CaseDefinition) implies
                redefines(gen.oclAsType(CaseDefinition).objectiveRequirement)) and
            (gen.oclIsKindOf(CaseUsage) implies
                redefines(gen.oclAsType(CaseUsage).objectiveRequirement))
    owningFeatureMembership <> null and
    owningFeatureMembership.oclIsKindOf(RequirementVerificationMembership) implies
        specializesFromLibrary('VerificationCases::VerificationCase::obj::requirementVerifications')
    """

    reqId = EAttribute(eType=String, unique=True, derived=False, changeable=True)
    text = EAttribute(
        eType=String,
        unique=True,
        derived=True,
        changeable=True,
        upper=-1,
        transient=True,
        derived_class=DerivedText,
    )
    _requirementDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="requirementDefinition",
        transient=True,
    )
    requiredConstraint = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedRequiredconstraint,
    )
    assumedConstraint = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedAssumedconstraint,
    )
    _subjectParameter = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="subjectParameter",
        transient=True,
    )
    framedConcern = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedFramedconcern,
    )
    actorParameter = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedActorparameter,
    )
    stakeholderParameter = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedStakeholderparameter,
    )

    @property
    def requirementDefinition(self):
        raise NotImplementedError("Missing implementation for requirementDefinition")

    @requirementDefinition.setter
    def requirementDefinition(self, value):
        raise NotImplementedError("Missing implementation for requirementDefinition")

    @property
    def subjectParameter(self):
        raise NotImplementedError("Missing implementation for subjectParameter")

    @subjectParameter.setter
    def subjectParameter(self, value):
        raise NotImplementedError("Missing implementation for subjectParameter")

    def __init__(
        self,
        *,
        requirementDefinition=None,
        reqId=None,
        text=None,
        requiredConstraint=None,
        assumedConstraint=None,
        subjectParameter=None,
        framedConcern=None,
        actorParameter=None,
        stakeholderParameter=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if reqId is not None:
            self.reqId = reqId

        if text:
            self.text.extend(text)

        if requirementDefinition is not None:
            self.requirementDefinition = requirementDefinition

        if requiredConstraint:
            self.requiredConstraint.extend(requiredConstraint)

        if assumedConstraint:
            self.assumedConstraint.extend(assumedConstraint)

        if subjectParameter is not None:
            self.subjectParameter = subjectParameter

        if framedConcern:
            self.framedConcern.extend(framedConcern)

        if actorParameter:
            self.actorParameter.extend(actorParameter)

        if stakeholderParameter:
            self.stakeholderParameter.extend(stakeholderParameter)


class ConstraintDefinition(OccurrenceDefinition, Predicate):
    """<p>A <code>ConstraintDefinition</code> is an <code>OccurrenceDefinition</code> that is also a <code>Predicate</code> that defines a constraint that may be asserted to hold on a system or part of a system.</p>


    specializesFromLibrary('Constraints::ConstraintCheck')"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CaseUsage(CalculationUsage):
    """<p>A <code>CaseUsage</code> is a <code>Usage</code> of a <code>CaseDefinition</code>.</p>
    objectiveRequirement =
        let objectives: OrderedSet(RequirementUsage) =
            featureMembership->
                selectByKind(ObjectiveMembership).
                ownedRequirement in
        if objectives->isEmpty() then null
        else objectives->first().ownedObjectiveRequirement
        endif
    featureMembership->
        selectByKind(ObjectiveMembership)->
        size() <= 1
    featureMembership->
            selectByKind(SubjectMembership)->
            size() <= 1
    actorParameter = featureMembership->
        selectByKind(ActorMembership).
        ownedActorParameter
    subjectParameter =
        let subjects : OrderedSet(SubjectMembership) =
            featureMembership->selectByKind(SubjectMembership) in
        if subjects->isEmpty() then null
        else subjects->first().ownedSubjectParameter
        endif
    input->notEmpty() and input->first() = subjectParameter
    specializeFromLibrary('Cases::cases')
    isComposite and owningType <> null and
        (owningType.oclIsKindOf(CaseDefinition) or
         owningType.oclIsKindOf(CaseUsage)) implies
        specializesFromLibrary('Cases::Case::subcases')"""

    _objectiveRequirement = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        name="objectiveRequirement",
        transient=True,
    )
    _caseDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="caseDefinition",
        transient=True,
    )
    _subjectParameter = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="subjectParameter",
        transient=True,
    )
    actorParameter = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedActorparameter,
    )

    @property
    def objectiveRequirement(self):
        raise NotImplementedError("Missing implementation for objectiveRequirement")

    @objectiveRequirement.setter
    def objectiveRequirement(self, value):
        raise NotImplementedError("Missing implementation for objectiveRequirement")

    @property
    def caseDefinition(self):
        raise NotImplementedError("Missing implementation for caseDefinition")

    @caseDefinition.setter
    def caseDefinition(self, value):
        raise NotImplementedError("Missing implementation for caseDefinition")

    @property
    def subjectParameter(self):
        raise NotImplementedError("Missing implementation for subjectParameter")

    @subjectParameter.setter
    def subjectParameter(self, value):
        raise NotImplementedError("Missing implementation for subjectParameter")

    def __init__(
        self,
        *,
        objectiveRequirement=None,
        caseDefinition=None,
        subjectParameter=None,
        actorParameter=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if objectiveRequirement is not None:
            self.objectiveRequirement = objectiveRequirement

        if caseDefinition is not None:
            self.caseDefinition = caseDefinition

        if subjectParameter is not None:
            self.subjectParameter = subjectParameter

        if actorParameter:
            self.actorParameter.extend(actorParameter)


class DerivedCalculation(EDerivedCollection):
    pass


class CalculationDefinition(ActionDefinition, Function):
    """<p>A <code>CalculationDefinition</code> is an <coed>ActionDefinition</code> that also defines a <code>Function</code> producing a <code>result</code>.</p>
    specializesFromLibrary('Calculations::Calculation')
    calculation = action->selectByKind(CalculationUsage)"""

    calculation = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedCalculation,
    )

    def __init__(self, *, calculation=None, **kwargs):
        super().__init__(**kwargs)

        if calculation:
            self.calculation.extend(calculation)


class DerivedView(EDerivedCollection):
    pass


class ViewDefinition(PartDefinition):
    """<p>A <code>ViewDefinition</code> is a <code>PartDefinition</code> that specifies how a view artifact is constructed to satisfy a <code>viewpoint</code>. It specifies a <code>viewConditions</code> to define the model content to be presented and a <code>viewRendering</code> to define how the model content is presented.</p>
    view = usage->selectByKind(ViewUsage)
    satisfiedViewpoint = ownedRequirement->
        selectByKind(ViewpointUsage)->
        select(isComposite)
    viewRendering =
        let renderings: OrderedSet(ViewRenderingMembership) =
            featureMembership->selectByKind(ViewRenderingMembership) in
        if renderings->isEmpty() then null
        else renderings->first().referencedRendering
        endif
    viewCondition = featureMembership->
        selectByKind(ElementFilterMembership).
        condition
    featureMembership->
        selectByKind(ViewRenderingMembership)->
        size() <= 1
    specializesFromLibrary('Views::View')"""

    view = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedView,
    )
    satisfiedViewpoint = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedSatisfiedviewpoint,
    )
    _viewRendering = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="viewRendering",
        transient=True,
    )
    viewCondition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedViewcondition,
    )

    @property
    def viewRendering(self):
        raise NotImplementedError("Missing implementation for viewRendering")

    @viewRendering.setter
    def viewRendering(self, value):
        raise NotImplementedError("Missing implementation for viewRendering")

    def __init__(
        self,
        *,
        view=None,
        satisfiedViewpoint=None,
        viewRendering=None,
        viewCondition=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if view:
            self.view.extend(view)

        if satisfiedViewpoint:
            self.satisfiedViewpoint.extend(satisfiedViewpoint)

        if viewRendering is not None:
            self.viewRendering = viewRendering

        if viewCondition:
            self.viewCondition.extend(viewCondition)


class DerivedRendering(EDerivedCollection):
    pass


class RenderingDefinition(PartDefinition):
    """<p>A <code>RenderingDefinition</code> is a <code>PartDefinition</code> that defines a specific rendering of the content of a model view (e.g., symbols, style, layout, etc.).</p>
    rendering = usages->selectByKind(RenderingUsage)
    specializesFromLibrary('Views::Rendering')"""

    rendering = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedRendering,
    )

    def __init__(self, *, rendering=None, **kwargs):
        super().__init__(**kwargs)

        if rendering:
            self.rendering.extend(rendering)


class MetadataDefinition(ItemDefinition, Metaclass):
    """<p>A <code>MetadataDefinition</code> is an <code>ItemDefinition</code> that is also a <code>Metaclass</code>.</p>
    specializesFromLibrary('Metadata::MetadataItem')"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DerivedConnectiondefinition(EDerivedCollection):
    pass


class ConnectionUsage(ConnectorAsUsage, PartUsage):
    """<p>A <code>ConnectionUsage</code> is a <code>ConnectorAsUsage</code> that is also a <code>PartUsage</code>. Nominally, if its type is a <code>ConnectionDefinition</code>, then a <code>ConnectionUsage</code> is a Usage of that <code>ConnectionDefinition</code>, representing a connection between parts of a system. However, other kinds of kernel <code>AssociationStructures</code> are also allowed, to permit use of <code>AssociationStructures</code> from the Kernel Model Libraries.</p>
    specializesFromLibrary("Connections::connections")
    ownedEndFeature->size() = 2 implies
        specializesFromLibrary("Connections::binaryConnections")"""

    connectionDefinition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedConnectiondefinition,
    )

    def __init__(self, *, connectionDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if connectionDefinition:
            self.connectionDefinition.extend(connectionDefinition)


class RequirementDefinition(ConstraintDefinition):
    """<p>A <code>RequirementDefinition</code> is a <code>ConstraintDefinition</code> that defines a requirement used in the context of a specification as a constraint that a valid solution must satisfy. The specification is relative to a specified subject, possibly in collaboration with one or more external actors.</p>
    text = documentation.body
    assumedConstraint = ownedFeatureMembership->
        selectByKind(RequirementConstraintMembership)->
        select(kind = RequirementConstraintKind::assumption).
        ownedConstraint
    requiredConstraint = ownedFeatureMembership->
        selectByKind(RequirementConstraintMembership)->
        select(kind = RequirementConstraintKind::requirement).
        ownedConstraint
    subjectParameter =
        let subjects : OrderedSet(SubjectMembership) =
            featureMembership->selectByKind(SubjectMembership) in
        if subjects->isEmpty() then null
        else subjects->first().ownedSubjectParameter
        endif
    framedConcern = featureMembership->
        selectByKind(FramedConcernMembership).
        ownedConcern
    actorParameter = featureMembership->
        selectByKind(ActorMembership).
        ownedActorParameter
    stakeholderParameter = featureMembership->
        selectByKind(StakholderMembership).
        ownedStakeholderParameter
    featureMembership->
        selectByKind(SubjectMembership)->
        size() <= 1
    input->notEmpty() and input->first() = subjectParameter
    specializesFromLibrary('Requirements::RequirementCheck')"""

    reqId = EAttribute(eType=String, unique=True, derived=False, changeable=True)
    text = EAttribute(
        eType=String,
        unique=True,
        derived=True,
        changeable=True,
        upper=-1,
        transient=True,
        derived_class=DerivedText,
    )
    _subjectParameter = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="subjectParameter",
        transient=True,
    )
    actorParameter = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedActorparameter,
    )
    stakeholderParameter = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedStakeholderparameter,
    )
    assumedConstraint = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedAssumedconstraint,
    )
    requiredConstraint = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedRequiredconstraint,
    )
    framedConcern = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedFramedconcern,
    )

    @property
    def subjectParameter(self):
        raise NotImplementedError("Missing implementation for subjectParameter")

    @subjectParameter.setter
    def subjectParameter(self, value):
        raise NotImplementedError("Missing implementation for subjectParameter")

    def __init__(
        self,
        *,
        reqId=None,
        text=None,
        subjectParameter=None,
        actorParameter=None,
        stakeholderParameter=None,
        assumedConstraint=None,
        requiredConstraint=None,
        framedConcern=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if reqId is not None:
            self.reqId = reqId

        if text:
            self.text.extend(text)

        if subjectParameter is not None:
            self.subjectParameter = subjectParameter

        if actorParameter:
            self.actorParameter.extend(actorParameter)

        if stakeholderParameter:
            self.stakeholderParameter.extend(stakeholderParameter)

        if assumedConstraint:
            self.assumedConstraint.extend(assumedConstraint)

        if requiredConstraint:
            self.requiredConstraint.extend(requiredConstraint)

        if framedConcern:
            self.framedConcern.extend(framedConcern)


class ConcernUsage(RequirementUsage):
    """<p>A <code>ConcernUsage</code> is a <code>Usage</code> of a <code>ConcernDefinition</code>.</p>

     The <code>ownedStakeholder</code> features of the ConcernUsage shall all subset the <em><code>ConcernCheck::concernedStakeholders</code> </em>feature. If the ConcernUsage is an <code>ownedFeature</code> of a StakeholderDefinition or StakeholderUsage, then the ConcernUsage shall have an <code>ownedStakeholder</code> feature that is bound to the <em><code>self</code></em> feature of its owner.</p>

    specializesFromLibrary('Requirements::concernChecks')
    owningFeatureMembership <> null and
    owningFeatureMembership.oclIsKindOf(FramedConcernMembership) implies
        specializesFromLibrary('Requirements::RequirementCheck::concerns')"""

    _concernDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="concernDefinition",
        transient=True,
    )

    @property
    def concernDefinition(self):
        raise NotImplementedError("Missing implementation for concernDefinition")

    @concernDefinition.setter
    def concernDefinition(self, value):
        raise NotImplementedError("Missing implementation for concernDefinition")

    def __init__(self, *, concernDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if concernDefinition is not None:
            self.concernDefinition = concernDefinition


class CaseDefinition(CalculationDefinition):
    """<p>A <code>CaseDefinition</code> is a <code>CalculationDefinition</code> for a process, often involving collecting evidence or data, relative to a subject, possibly involving the collaboration of one or more other actors, producing a result that meets an objective.</p>
    objectiveRequirement =
        let objectives: OrderedSet(RequirementUsage) =
            featureMembership->
                selectByKind(ObjectiveMembership).
                ownedRequirement in
        if objectives->isEmpty() then null
        else objectives->first().ownedObjectiveRequirement
        endif
    featureMembership->
        selectByKind(ObjectiveMembership)->
        size() <= 1
    subjectParameter =
        let subjectMems : OrderedSet(SubjectMembership) =
            featureMembership->selectByKind(SubjectMembership) in
        if subjectMems->isEmpty() then null
        else subjectMems->first().ownedSubjectParameter
        endif
    actorParameter = featureMembership->
        selectByKind(ActorMembership).
        ownedActorParameter
    featureMembership->selectByKind(SubjectMembership)->size() <= 1
    input->notEmpty() and input->first() = subjectParameter
    specializesFromLibrary('Cases::Case')"""

    _objectiveRequirement = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        name="objectiveRequirement",
        transient=True,
    )
    _subjectParameter = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="subjectParameter",
        transient=True,
    )
    actorParameter = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedActorparameter,
    )

    @property
    def objectiveRequirement(self):
        raise NotImplementedError("Missing implementation for objectiveRequirement")

    @objectiveRequirement.setter
    def objectiveRequirement(self, value):
        raise NotImplementedError("Missing implementation for objectiveRequirement")

    @property
    def subjectParameter(self):
        raise NotImplementedError("Missing implementation for subjectParameter")

    @subjectParameter.setter
    def subjectParameter(self, value):
        raise NotImplementedError("Missing implementation for subjectParameter")

    def __init__(
        self,
        *,
        objectiveRequirement=None,
        subjectParameter=None,
        actorParameter=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if objectiveRequirement is not None:
            self.objectiveRequirement = objectiveRequirement

        if subjectParameter is not None:
            self.subjectParameter = subjectParameter

        if actorParameter:
            self.actorParameter.extend(actorParameter)


class DerivedAnalysisaction(EDerivedCollection):
    pass


class AnalysisCaseUsage(CaseUsage):
    """<p>An <code>AnalysisCaseUsage</code> is a <code>Usage</code> of an <code>AnalysisCaseDefinition</code>.</p>
    analysisAction = usage->select(
        isComposite and
        specializes('AnalysisCases::AnalysisAction'))
    resultExpression =
        let results : OrderedSet(ResultExpressionMembership) =
            featureMembersip->
                selectByKind(ResultExpressionMembership) in
        if results->isEmpty() then null
        else results->first().ownedResultExpression
        endif
    specializesFromLibrary('AnalysisCases::analysisCases')
    isComposite and owningType <> null and
        (owningType.oclIsKindOf(AnalysisCaseDefinition) or
         owningType.oclIsKindOf(AnalysisCaseUsage)) implies
        specializesFromLibrary('AnalysisCases::AnalysisCase::subAnalysisCases')"""

    analysisAction = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedAnalysisaction,
    )
    _analysisCaseDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="analysisCaseDefinition",
        transient=True,
    )
    _resultExpression = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="resultExpression",
        transient=True,
    )

    @property
    def analysisCaseDefinition(self):
        raise NotImplementedError("Missing implementation for analysisCaseDefinition")

    @analysisCaseDefinition.setter
    def analysisCaseDefinition(self, value):
        raise NotImplementedError("Missing implementation for analysisCaseDefinition")

    @property
    def resultExpression(self):
        raise NotImplementedError("Missing implementation for resultExpression")

    @resultExpression.setter
    def resultExpression(self, value):
        raise NotImplementedError("Missing implementation for resultExpression")

    def __init__(
        self,
        *,
        analysisAction=None,
        analysisCaseDefinition=None,
        resultExpression=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if analysisAction:
            self.analysisAction.extend(analysisAction)

        if analysisCaseDefinition is not None:
            self.analysisCaseDefinition = analysisCaseDefinition

        if resultExpression is not None:
            self.resultExpression = resultExpression


class DerivedVerifiedrequirement(EDerivedCollection):
    pass


class VerificationCaseUsage(CaseUsage):
    """<p>A <code>VerificationCaseUsage</code> is a </code>Usage</code> of a <code>VerificationCaseDefinition</code>.</p>
    verifiedRequirement =
        if objectiveRequirement = null then OrderedSet{}
        else
            objectiveRequirement.featureMembership->
                selectByKind(RequirementVerificationMembership).
                verifiedRequirement->asOrderedSet()
        endif
    specializesFromLibrary('VerificationCases::verificationCases')
    isComposite and owningType <> null and
        (owningType.oclIsKindOf(VerificationCaseDefinition) or
         owningType.oclIsKindOf(VerificationCaseUsage))"""

    _verificationCaseDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="verificationCaseDefinition",
        transient=True,
    )
    verifiedRequirement = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedVerifiedrequirement,
    )

    @property
    def verificationCaseDefinition(self):
        raise NotImplementedError(
            "Missing implementation for verificationCaseDefinition"
        )

    @verificationCaseDefinition.setter
    def verificationCaseDefinition(self, value):
        raise NotImplementedError(
            "Missing implementation for verificationCaseDefinition"
        )

    def __init__(
        self, *, verificationCaseDefinition=None, verifiedRequirement=None, **kwargs
    ):
        super().__init__(**kwargs)

        if verificationCaseDefinition is not None:
            self.verificationCaseDefinition = verificationCaseDefinition

        if verifiedRequirement:
            self.verifiedRequirement.extend(verifiedRequirement)


class DerivedIncludedusecase(EDerivedCollection):
    pass


class UseCaseUsage(CaseUsage):
    """<p>A <code>UseCaseUsage</code> is a <code>Usage</code> of a <code>UseCaseDefinition</code>.</p>
    includedUseCase = ownedUseCase->
        selectByKind(IncludeUseCaseUsage).
        useCaseIncluded
    specializesFromLibrary('UseCases::useCases')
    isComposite and owningType <> null and
    (owningType.oclIsKindOf(UseCaseDefinition) or
     owningType.oclIsKindOf(UseCaseUsage)) implies
        specializesFromLibrary('UseCases::UseCase::subUseCases')"""

    _useCaseDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="useCaseDefinition",
        transient=True,
    )
    includedUseCase = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedIncludedusecase,
    )

    @property
    def useCaseDefinition(self):
        raise NotImplementedError("Missing implementation for useCaseDefinition")

    @useCaseDefinition.setter
    def useCaseDefinition(self, value):
        raise NotImplementedError("Missing implementation for useCaseDefinition")

    def __init__(self, *, useCaseDefinition=None, includedUseCase=None, **kwargs):
        super().__init__(**kwargs)

        if useCaseDefinition is not None:
            self.useCaseDefinition = useCaseDefinition

        if includedUseCase:
            self.includedUseCase.extend(includedUseCase)


class DerivedViewpointstakeholder(EDerivedCollection):
    pass


class ViewpointUsage(RequirementUsage):
    """<p>A <code>ViewpointUsage<code> is a <code>Usage</code> of a <code>ViewpointDefinition</code>.</p>


    viewpointStakeholder = framedConcern.featureMemberhsip->
        selectByKind(StakeholderMembership).
        ownedStakeholderParameter
    specializesFromLibrary('Views::viewpoints')
    isComposite and owningType <> null and
    (owningType.oclIsKindOf(ViewDefinition) or
     owningType.oclIsKindOf(ViewUsage)) implies
        specializesFromLibrary('Views::View::viewpointSatisfactions')"""

    _viewpointDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="viewpointDefinition",
        transient=True,
    )
    viewpointStakeholder = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedViewpointstakeholder,
    )

    @property
    def viewpointDefinition(self):
        raise NotImplementedError("Missing implementation for viewpointDefinition")

    @viewpointDefinition.setter
    def viewpointDefinition(self, value):
        raise NotImplementedError("Missing implementation for viewpointDefinition")

    def __init__(
        self, *, viewpointDefinition=None, viewpointStakeholder=None, **kwargs
    ):
        super().__init__(**kwargs)

        if viewpointDefinition is not None:
            self.viewpointDefinition = viewpointDefinition

        if viewpointStakeholder:
            self.viewpointStakeholder.extend(viewpointStakeholder)


class AssertConstraintUsage(ConstraintUsage, Invariant):
    """<p>An <code>AssertConstraintUsage</code> is a <code>ConstraintUsage</code> that is also an <code>Invariant</code> and, so, is asserted to be true (by default). Unless it is the <code>AssertConstraintUsage</code> itself, the asserted <code>ConstraintUsage</code> is related to the <code>AssertConstraintUsage</code> by a ReferenceSubsetting <code>Relationship</code>.</p>
    assertedConstraint =
        if ownedReferenceSubsetting = null then self
        else ownedReferenceSubsetting.referencedFeature.oclAsType(ConstraintUsage)
        endif
    if isNegated then
        specializesFromLibrary('Constraints::negatedConstraints')
    else
        specializesFromLibrary('Constraints::assertedConstraints')
    endif"""

    _assertedConstraint = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="assertedConstraint",
        transient=True,
    )

    @property
    def assertedConstraint(self):
        raise NotImplementedError("Missing implementation for assertedConstraint")

    @assertedConstraint.setter
    def assertedConstraint(self, value):
        raise NotImplementedError("Missing implementation for assertedConstraint")

    def __init__(self, *, assertedConstraint=None, **kwargs):
        super().__init__(**kwargs)

        if assertedConstraint is not None:
            self.assertedConstraint = assertedConstraint


class ExhibitStateUsage(StateUsage, PerformActionUsage):
    """<p>An <code>ExhibitStateUsage</code> is a <code>StateUsage</code> that represents the exhibiting of a <code>StateUsage</code>. Unless it is the <code>StateUsage</code> itself, the <code>StateUsage</code> to be exhibited is related to the <code>ExhibitStateUsage</code> by a <code>ReferenceSubsetting</code> <code>Relationship</code>. An <code>ExhibitStateUsage</code> is also a <code>PerformActionUsage</code>, with its <code>exhibitedState</code> as the <code>performedAction</code>.</p>

    owningType <> null and
    (owningType.oclIsKindOf(PartDefinition) or
     owningType.oclIsKindOf(PartUsage)) implies
        specializesFromLibrary('Parts::Part::exhibitedStates')"""

    _exhibitedState = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="exhibitedState",
        transient=True,
    )

    @property
    def exhibitedState(self):
        raise NotImplementedError("Missing implementation for exhibitedState")

    @exhibitedState.setter
    def exhibitedState(self, value):
        raise NotImplementedError("Missing implementation for exhibitedState")

    def __init__(self, *, exhibitedState=None, **kwargs):
        super().__init__(**kwargs)

        if exhibitedState is not None:
            self.exhibitedState = exhibitedState


class DerivedInterfacedefinition(EDerivedCollection):
    pass


class InterfaceUsage(ConnectionUsage):
    """<p>An <code>InterfaceUsage</code> is a Usage of an <code>InterfaceDefinition</code> to represent an interface connecting parts of a system through specific ports.</p>
    ownedEndFeature->size() = 2 implies
        specializesFromLibrary("Interfaces::binaryInterfaces")
    specializesFromLibrary("Interfaces::interfaces")"""

    interfaceDefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedInterfacedefinition,
    )

    def __init__(self, *, interfaceDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if interfaceDefinition:
            self.interfaceDefinition.extend(interfaceDefinition)


class DerivedAllocationdefinition(EDerivedCollection):
    pass


class AllocationUsage(ConnectionUsage):
    """<p>An <code>AllocationUsage</code> is a usage of an <code>AllocationDefinition</code> asserting the allocation of the <code>source</code> feature to the <code>target</code> feature.</p>
    specializesFromLibrary("Allocations::allocations")"""

    allocationDefinition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedAllocationdefinition,
    )

    def __init__(self, *, allocationDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if allocationDefinition:
            self.allocationDefinition.extend(allocationDefinition)


class ConcernDefinition(RequirementDefinition):
    """<p>A <code>ConcernDefinition</code> is a <code>RequirementDefinition</code> that one or more stakeholders may be interested in having addressed. These stakeholders are identified by the <code>ownedStakeholders</code>of the <code>ConcernDefinition</code>.</p>

    specializesFromLibrary('Requirements::ConcernCheck')"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AnalysisCaseDefinition(CaseDefinition):
    """<p>An <code>AnalysisCaseDefinition</code> is a <code>CaseDefinition</code> for the case of carrying out an analysis.</p>
    analysisAction = action->select(
        isComposite and
        specializes('AnalysisCases::AnalysisAction'))
    resultExpression =
        let results : OrderedSet(ResultExpressionMembership) =
            featureMembersip->
                selectByKind(ResultExpressionMembership) in
        if results->isEmpty() then null
        else results->first().ownedResultExpression
        endif
    specializesFromLibrary('AnalysisCases::AnalysisCase')"""

    analysisAction = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedAnalysisaction,
    )
    _resultExpression = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="resultExpression",
        transient=True,
    )

    @property
    def resultExpression(self):
        raise NotImplementedError("Missing implementation for resultExpression")

    @resultExpression.setter
    def resultExpression(self, value):
        raise NotImplementedError("Missing implementation for resultExpression")

    def __init__(self, *, analysisAction=None, resultExpression=None, **kwargs):
        super().__init__(**kwargs)

        if analysisAction:
            self.analysisAction.extend(analysisAction)

        if resultExpression is not None:
            self.resultExpression = resultExpression


class VerificationCaseDefinition(CaseDefinition):
    """<p>A <code>VerificationCaseDefinition</code> is a <code>CaseDefinition</code> for the purpose of verification of the subject of the case against its requirements.</p>
    verifiedRequirement =
        if objectiveRequirement = null then OrderedSet{}
        else
            objectiveRequirement.featureMembership->
                selectByKind(RequirementVerificationMembership).
                verifiedRequirement->asOrderedSet()
        endif
    specializesFromLibrary('VerificationCases::VerificationCase')"""

    verifiedRequirement = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedVerifiedrequirement,
    )

    def __init__(self, *, verifiedRequirement=None, **kwargs):
        super().__init__(**kwargs)

        if verifiedRequirement:
            self.verifiedRequirement.extend(verifiedRequirement)


class UseCaseDefinition(CaseDefinition):
    """<p>A <code>UseCaseDefinition</code> is a <code>CaseDefinition</code> that specifies a set of actions performed by its subject, in interaction with one or more actors external to the subject. The objective is to yield an observable result that is of value to one or more of the actors.</p>

    includedUseCase = ownedUseCase->
        selectByKind(IncludeUseCaseUsage).
        useCaseIncluded
    specializesFromLibrary('UseCases::UseCase')"""

    includedUseCase = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedIncludedusecase,
    )

    def __init__(self, *, includedUseCase=None, **kwargs):
        super().__init__(**kwargs)

        if includedUseCase:
            self.includedUseCase.extend(includedUseCase)


class ViewpointDefinition(RequirementDefinition):
    """<p>A <code>ViewpointDefinition</code> is a <code>RequirementDefinition</code> that specifies one or more stakeholder concerns that are to be satisfied by creating a view of a model.</p>
    viewpointStakeholder = framedConcern.featureMemberhsip->
        selectByKind(StakeholderMembership).
        ownedStakeholderParameter
    specializesFromLibrary('Views::Viewpoint')"""

    viewpointStakeholder = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedViewpointstakeholder,
    )

    def __init__(self, *, viewpointStakeholder=None, **kwargs):
        super().__init__(**kwargs)

        if viewpointStakeholder:
            self.viewpointStakeholder.extend(viewpointStakeholder)


class DerivedConnectionend(EDerivedCollection):
    pass


class ConnectionDefinition(PartDefinition, AssociationStructure):
    """<p>A <code>ConnectionDefinition</code> is a <code>PartDefinition</code> that is also an <code>AssociationStructure</code>. The end <code>Features</code> of a <code>ConnectionDefinition</code> must be <code>Usages</code>.</p>
    specializesFromLibrary("Connections::Connection")
    ownedEndFeature->size() = 2 implies
        specializesFromLibrary("Connections::BinaryConnections")"""

    connectionEnd = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedConnectionend,
    )

    def __init__(self, *, connectionEnd=None, **kwargs):
        super().__init__(**kwargs)

        if connectionEnd:
            self.connectionEnd.extend(connectionEnd)


class SatisfyRequirementUsage(RequirementUsage, AssertConstraintUsage):
    """<p>A <code>SatisfyRequirementUsage</code> is an <code>AssertConstraintUsage</code> that asserts, by default, that a satisfied <code>RequirementUsage</code> is true for a specific <code>satisfyingFeature</code>, or, if <code>isNegated = true</code>, that the <code>RequirementUsage</code> is false. The satisfied <code>RequirementUsage</code> is related to the <code>SatisfyRequirementUsage</code> by a <code>ReferenceSubsetting</code> <code>Relationship</code>.</p>
    satisfyingFeature =
        let bindings: BindingConnector = ownedMember->
            selectByKind(BindingConnector)->
            select(b | b.relatedElement->includes(subjectParameter)) in
        if bindings->isEmpty() or
           bindings->first().relatedElement->exits(r | r <> subjectParameter)
        then null
        else bindings->first().relatedElement->any(r | r <> subjectParameter)
        endif
    ownedMember->selectByKind(BindingConnector)->
        select(b |
            b.relatedElement->includes(subjectParameter) and
            b.relatedElement->exists(r | r <> subjectParameter))->
        size() = 1"""

    _satisfiedRequirement = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="satisfiedRequirement",
        transient=True,
    )
    _satisfyingFeature = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="satisfyingFeature",
        transient=True,
    )

    @property
    def satisfiedRequirement(self):
        raise NotImplementedError("Missing implementation for satisfiedRequirement")

    @satisfiedRequirement.setter
    def satisfiedRequirement(self, value):
        raise NotImplementedError("Missing implementation for satisfiedRequirement")

    @property
    def satisfyingFeature(self):
        raise NotImplementedError("Missing implementation for satisfyingFeature")

    @satisfyingFeature.setter
    def satisfyingFeature(self, value):
        raise NotImplementedError("Missing implementation for satisfyingFeature")

    def __init__(self, *, satisfiedRequirement=None, satisfyingFeature=None, **kwargs):
        super().__init__(**kwargs)

        if satisfiedRequirement is not None:
            self.satisfiedRequirement = satisfiedRequirement

        if satisfyingFeature is not None:
            self.satisfyingFeature = satisfyingFeature


class DerivedAllocation(EDerivedCollection):
    pass


class AllocationDefinition(ConnectionDefinition):
    """<p>An <code>AllocationDefinition</code> is a <code>ConnectionDefinition</code> that specifies that some or all of the responsibility to realize the intent of the <code>source</code> is allocated to the <code>target</code> instances. Such allocations define mappings across the various structures and hierarchies of a system model, perhaps as a precursor to more rigorous specifications and implementations. An <code>AllocationDefinition</code> can itself be refined using nested <code>allocations</code> that give a finer-grained decomposition of the containing allocation mapping.</p>
    allocation = usage->selectAsKind(AllocationUsage)
    specializesFromLibrary("Allocations::Allocation")"""

    allocation = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedAllocation,
    )

    def __init__(self, *, allocation=None, **kwargs):
        super().__init__(**kwargs)

        if allocation:
            self.allocation.extend(allocation)


class DerivedInterfaceend(EDerivedCollection):
    pass


class InterfaceDefinition(ConnectionDefinition):
    """<p>An <code>InterfaceDefinition</code> is a <code>ConnectionDefinition</code> all of whose ends are <code>PortUsages</code>, defining an interface between elements that interact through such ports.</p>
    specializesFromLibrary("Interfaces::Interface")
    ownedEndFeature->size() = 2 implies
        specializesFromLibrary("Interfaces::BinaryInterface")"""

    interfaceEnd = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedInterfaceend,
    )

    def __init__(self, *, interfaceEnd=None, **kwargs):
        super().__init__(**kwargs)

        if interfaceEnd:
            self.interfaceEnd.extend(interfaceEnd)


class IncludeUseCaseUsage(UseCaseUsage, PerformActionUsage):
    """<p>An <code>IncludeUseCaseUsage</code> is a <code>UseCaseUsage</code> that represents the inclusion of a <code>UseCaseUsage</code> by a <code>UseCaseDefinition</code> or <code>UseCaseUsage</code>. Unless it is the <code>IncludeUseCaseUsage</code> itself, the <code>UseCaseUsage</code> to be included is related to the <code>includedUseCase</code> by a <code>ReferenceSubsetting</code> <code>Relationship</code>. An <code>IncludeUseCaseUsage</code> is also a PerformActionUsage, with its <code>useCaseIncluded</code> as the <code>performedAction</code>.</p>

    owningType <> null and
    (owningType.oclIsKindOf(UseCaseDefinition) or
     owningType.oclIsKindOf(UseCaseUsage) implies
        specializesFromLibrary('UseCases::UseCase::includedUseCases')"""

    _useCaseIncluded = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="useCaseIncluded",
        transient=True,
    )

    @property
    def useCaseIncluded(self):
        raise NotImplementedError("Missing implementation for useCaseIncluded")

    @useCaseIncluded.setter
    def useCaseIncluded(self, value):
        raise NotImplementedError("Missing implementation for useCaseIncluded")

    def __init__(self, *, useCaseIncluded=None, **kwargs):
        super().__init__(**kwargs)

        if useCaseIncluded is not None:
            self.useCaseIncluded = useCaseIncluded


class DerivedFlowconnectiondefinition(EDerivedCollection):
    pass


class FlowConnectionUsage(ConnectionUsage, ActionUsage, ItemFlow):
    """<p>A <code>FlowConnectionUsage</code> is a <code>ConnectionUsage</code> that is also an <code>ItemFlow</code>.</p>
    if itemFlowEnds->isEmpty() then
        specializesFromLibrary("Connections::messageConnections")
    else
        specializesFromLibrary("Connections::flowConnections"
    endif"""

    flowConnectionDefinition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedFlowconnectiondefinition,
    )

    def __init__(self, *, flowConnectionDefinition=None, **kwargs):
        super().__init__(**kwargs)

        if flowConnectionDefinition:
            self.flowConnectionDefinition.extend(flowConnectionDefinition)


class FlowConnectionDefinition(ConnectionDefinition, ActionDefinition, Interaction):
    """<p>A <code>FlowConnectionDefinition</code> is a <code>ConnectionDefinition</code> and <code>ActionDefinition</code> that is also an <code>Interaction</code> representing flows between <code>Usages</code>.</p>
    specializesFromLibrary("Connections::MessageConnection")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SuccessionFlowConnectionUsage(FlowConnectionUsage, SuccessionItemFlow):
    """<p>A <code>SuccessionFlowConnectionUsage</code> is a <code>FlowConnectionUsage</code> that is also a <code>SuccessionItemFlow</code>.</p>
    specializesFromLibrary("Connections::successionFlowConnections")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
