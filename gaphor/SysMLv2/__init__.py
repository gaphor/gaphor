from gaphor.SysMLv2.sysmlv2 import (
    InterfaceUsage,
    ConnectionUsage,
    ConnectorAsUsage,
    Usage,
    Feature,
    FeatureMembership,
    Definition,
    Classifier,
    DataType,
    EnumerationDefinition,
    OccurrenceUsage,
    Class,
    OccurrenceDefinition,
    PortionKind,
    ItemUsage,
    Structure,
    PartUsage,
    PartDefinition,
    PortDefinition,
    ConjugatedPortDefinition,
    FlowConnectionUsage,
    ItemFlow,
    Connector,
    Association,
    Step,
    Behavior,
    Interaction,
    ActionUsage,
    Expression,
    Function,
    AllocationUsage,
    AllocationDefinition,
    ConnectionDefinition,
    AssociationStructure,
    StateUsage,
    TransitionUsage,
    AcceptActionUsage,
    Succession,
    CalculationUsage,
    ConstraintUsage,
    BooleanExpression,
    Predicate,
    RequirementUsage,
    RequirementDefinition,
    ConcernUsage,
    ConcernDefinition,
    CaseUsage,
    CaseDefinition,
    CalculationDefinition,
    ActionDefinition,
    AnalysisCaseUsage,
    AnalysisCaseDefinition,
    VerificationCaseUsage,
    VerificationCaseDefinition,
    UseCaseUsage,
    UseCaseDefinition,
    ViewUsage,
    ViewDefinition,
    ViewpointUsage,
    ViewpointDefinition,
    RenderingUsage,
    RenderingDefinition,
    MetadataUsage,
    MetadataFeature,
    Metaclass,
    InterfaceDefinition,
    EventOccurrenceUsage,
    RequirementVerificationMembership,
    RequirementConstraintMembership,
    RequirementConstraintKind,
    FramedConcernMembership,
    SubjectMembership,
    ParameterMembership,
    ActorMembership,
    StakeholderMembership,
    SatisfyRequirementUsage,
    AssertConstraintUsage,
    ForLoopActionUsage,
    LoopActionUsage,
    InvocationExpression,
    TriggerKind,
    AssignmentActionUsage,
    IfActionUsage,
    SendActionUsage,
    PerformActionUsage,
    WhileLoopActionUsage,
    StateDefinition,
    StateSubactionKind,
    ExhibitStateUsage,
    TransitionFeatureKind,
    IncludeUseCaseUsage,
    OperatorExpression,
    FeatureChainExpression,
)

from gaphor.SysMLv2 import sysmlv2

__all__ = [
    "InterfaceUsage",
    "ConnectionUsage",
    "ConnectorAsUsage",
    "Usage",
    "Feature",
    "FeatureMembership",
    "Definition",
    "Classifier",
    "DataType",
    "EnumerationDefinition",
    "OccurrenceUsage",
    "Class",
    "OccurrenceDefinition",
    "PortionKind",
    "ItemUsage",
    "Structure",
    "PartUsage",
    "PartDefinition",
    "PortDefinition",
    "ConjugatedPortDefinition",
    "FlowConnectionUsage",
    "ItemFlow",
    "Connector",
    "Association",
    "Step",
    "Behavior",
    "Interaction",
    "ActionUsage",
    "Expression",
    "Function",
    "AllocationUsage",
    "AllocationDefinition",
    "ConnectionDefinition",
    "AssociationStructure",
    "StateUsage",
    "TransitionUsage",
    "AcceptActionUsage",
    "Succession",
    "CalculationUsage",
    "ConstraintUsage",
    "BooleanExpression",
    "Predicate",
    "RequirementUsage",
    "RequirementDefinition",
    "ConcernUsage",
    "ConcernDefinition",
    "CaseUsage",
    "CaseDefinition",
    "CalculationDefinition",
    "ActionDefinition",
    "AnalysisCaseUsage",
    "AnalysisCaseDefinition",
    "VerificationCaseUsage",
    "VerificationCaseDefinition",
    "UseCaseUsage",
    "UseCaseDefinition",
    "ViewUsage",
    "ViewDefinition",
    "ViewpointUsage",
    "ViewpointDefinition",
    "RenderingUsage",
    "RenderingDefinition",
    "MetadataUsage",
    "MetadataFeature",
    "Metaclass",
    "InterfaceDefinition",
    "EventOccurrenceUsage",
    "RequirementVerificationMembership",
    "RequirementConstraintMembership",
    "RequirementConstraintKind",
    "FramedConcernMembership",
    "SubjectMembership",
    "ParameterMembership",
    "ActorMembership",
    "StakeholderMembership",
    "SatisfyRequirementUsage",
    "AssertConstraintUsage",
    "ForLoopActionUsage",
    "LoopActionUsage",
    "InvocationExpression",
    "TriggerKind",
    "AssignmentActionUsage",
    "IfActionUsage",
    "SendActionUsage",
    "PerformActionUsage",
    "WhileLoopActionUsage",
    "StateDefinition",
    "StateSubactionKind",
    "ExhibitStateUsage",
    "TransitionFeatureKind",
    "IncludeUseCaseUsage",
    "OperatorExpression",
    "FeatureChainExpression",
]

InterfaceUsage.interfaceDefinition.eType = InterfaceDefinition
ConnectionUsage.connectionDefinition.eType = AssociationStructure
Usage.variant.eType = Usage
Usage.definition.eType = Classifier
Usage.usage.eType = Usage
Usage.directedUsage.eType = Usage
Usage.nestedOccurrence.eType = OccurrenceUsage
Usage.nestedItem.eType = ItemUsage
Usage.nestedPart.eType = PartUsage
Usage.nestedConnection.eType = ConnectorAsUsage
Usage.nestedFlow.eType = FlowConnectionUsage
Usage.nestedInterface.eType = InterfaceUsage
Usage.nestedAllocation.eType = AllocationUsage
Usage.nestedAction.eType = ActionUsage
Usage.nestedState.eType = StateUsage
Usage.nestedTransition.eType = TransitionUsage
Usage.nestedCalculation.eType = CalculationUsage
Usage.nestedConstraint.eType = ConstraintUsage
Usage.nestedRequirement.eType = RequirementUsage
Usage.nestedConcern.eType = ConcernUsage
Usage.nestedCase.eType = CaseUsage
Usage.nestedAnalysisCase.eType = AnalysisCaseUsage
Usage.nestedVerificationCase.eType = VerificationCaseUsage
Usage.nestedUseCase.eType = UseCaseUsage
Usage.nestedView.eType = ViewUsage
Usage.nestedViewpoint.eType = ViewpointUsage
Usage.nestedRendering.eType = RenderingUsage
Usage.nestedMetadata.eType = MetadataUsage
Feature.chainingFeature.eType = Feature
Definition.variant.eType = Usage
Definition.usage.eType = Usage
Definition.directedUsage.eType = Usage
Definition.ownedOccurrence.eType = OccurrenceUsage
Definition.ownedItem.eType = ItemUsage
Definition.ownedPart.eType = PartUsage
Definition.ownedConnection.eType = ConnectorAsUsage
Definition.ownedFlow.eType = FlowConnectionUsage
Definition.ownedInterface.eType = InterfaceUsage
Definition.ownedAllocation.eType = AllocationUsage
Definition.ownedAction.eType = ActionUsage
Definition.ownedState.eType = StateUsage
Definition.ownedTransition.eType = TransitionUsage
Definition.ownedCalculation.eType = CalculationUsage
Definition.ownedConstraint.eType = ConstraintUsage
Definition.ownedRequirement.eType = RequirementUsage
Definition.ownedConcern.eType = ConcernUsage
Definition.ownedCase.eType = CaseUsage
Definition.ownedAnalysisCase.eType = AnalysisCaseUsage
Definition.ownedVerificationCase.eType = VerificationCaseUsage
Definition.ownedUseCase.eType = UseCaseUsage
Definition.ownedView.eType = ViewUsage
Definition.ownedViewpoint.eType = ViewpointUsage
Definition.ownedRendering.eType = RenderingUsage
Definition.ownedMetadata.eType = MetadataUsage
OccurrenceUsage.occurrenceDefinition.eType = Class
OccurrenceUsage._individualDefinition.eType = OccurrenceDefinition
ItemUsage.itemDefinition.eType = Structure
PartUsage.partDefinition.eType = PartDefinition
FlowConnectionUsage.flowConnectionDefinition.eType = Interaction
ItemFlow.itemType.eType = Classifier
ItemFlow._targetInputFeature.eType = Feature
ItemFlow._sourceOutputFeature.eType = Feature
ItemFlow.interaction.eType = Interaction
Connector.relatedFeature.eType = Feature
Connector.association.eType = Association
Connector.connectorEnd.eType = Feature
Connector._sourceFeature.eType = Feature
Connector.targetFeature.eType = Feature
Association.associationEnd.eType = Feature
Step.behavior.eType = Behavior
Step.parameter.eType = Feature
Behavior.step.eType = Step
Behavior.parameter.eType = Feature
ActionUsage.actionDefinition.eType = Behavior
Expression._function.eType = Function
Expression._result.eType = Feature
Function.expression.eType = Expression
Function._result.eType = Feature
AllocationUsage.allocationDefinition.eType = AllocationDefinition
AllocationDefinition.allocation.eType = AllocationUsage
ConnectionDefinition.connectionEnd.eType = Usage
StateUsage.stateDefinition.eType = Behavior
StateUsage._entryAction.eType = ActionUsage
StateUsage._doAction.eType = ActionUsage
StateUsage._exitAction.eType = ActionUsage
TransitionUsage._source.eType = ActionUsage
TransitionUsage._target.eType = ActionUsage
TransitionUsage.triggerAction.eType = AcceptActionUsage
TransitionUsage.guardExpression.eType = Expression
TransitionUsage.effectAction.eType = ActionUsage
TransitionUsage._succession.eType = Succession
AcceptActionUsage._receiverArgument.eType = Expression
AcceptActionUsage._payloadArgument.eType = Expression
Succession._transitionStep.eType = Step
Succession.triggerStep.eType = Step
Succession.effectStep.eType = Step
Succession.guardExpression.eType = Expression
CalculationUsage._calculationDefinition.eType = Function
ConstraintUsage._constraintDefinition.eType = Predicate
BooleanExpression._predicate.eType = Predicate
RequirementUsage._requirementDefinition.eType = RequirementDefinition
RequirementUsage.requiredConstraint.eType = ConstraintUsage
RequirementUsage.assumedConstraint.eType = ConstraintUsage
RequirementUsage._subjectParameter.eType = Usage
RequirementUsage.framedConcern.eType = ConcernUsage
RequirementUsage.actorParameter.eType = PartUsage
RequirementUsage.stakeholderParameter.eType = PartUsage
RequirementDefinition._subjectParameter.eType = Usage
RequirementDefinition.actorParameter.eType = PartUsage
RequirementDefinition.stakeholderParameter.eType = PartUsage
RequirementDefinition.assumedConstraint.eType = ConstraintUsage
RequirementDefinition.requiredConstraint.eType = ConstraintUsage
RequirementDefinition.framedConcern.eType = ConcernUsage
ConcernUsage._concernDefinition.eType = ConcernDefinition
CaseUsage._objectiveRequirement.eType = RequirementUsage
CaseUsage._caseDefinition.eType = CaseDefinition
CaseUsage._subjectParameter.eType = Usage
CaseUsage.actorParameter.eType = PartUsage
CaseDefinition._objectiveRequirement.eType = RequirementUsage
CaseDefinition._subjectParameter.eType = Usage
CaseDefinition.actorParameter.eType = PartUsage
CalculationDefinition.calculation.eType = CalculationUsage
ActionDefinition.action.eType = ActionUsage
AnalysisCaseUsage.analysisAction.eType = ActionUsage
AnalysisCaseUsage._analysisCaseDefinition.eType = AnalysisCaseDefinition
AnalysisCaseUsage._resultExpression.eType = Expression
AnalysisCaseDefinition.analysisAction.eType = ActionUsage
AnalysisCaseDefinition._resultExpression.eType = Expression
VerificationCaseUsage._verificationCaseDefinition.eType = VerificationCaseDefinition
VerificationCaseUsage.verifiedRequirement.eType = RequirementUsage
VerificationCaseDefinition.verifiedRequirement.eType = RequirementUsage
UseCaseUsage._useCaseDefinition.eType = UseCaseDefinition
UseCaseUsage.includedUseCase.eType = UseCaseUsage
UseCaseDefinition.includedUseCase.eType = UseCaseUsage
ViewUsage._viewDefinition.eType = ViewDefinition
ViewUsage.satisfiedViewpoint.eType = ViewpointUsage
ViewUsage._viewRendering.eType = RenderingUsage
ViewUsage.viewCondition.eType = Expression
ViewDefinition.view.eType = ViewUsage
ViewDefinition.satisfiedViewpoint.eType = ViewpointUsage
ViewDefinition._viewRendering.eType = RenderingUsage
ViewDefinition.viewCondition.eType = Expression
ViewpointUsage._viewpointDefinition.eType = ViewpointDefinition
ViewpointUsage.viewpointStakeholder.eType = PartUsage
ViewpointDefinition.viewpointStakeholder.eType = PartUsage
RenderingUsage._renderingDefinition.eType = RenderingDefinition
RenderingDefinition.rendering.eType = RenderingUsage
MetadataUsage._metadataDefinition.eType = Metaclass
MetadataFeature._metaclass.eType = Metaclass
EventOccurrenceUsage._eventOccurrence.eType = OccurrenceUsage
RequirementVerificationMembership._ownedRequirement.eType = RequirementUsage
RequirementVerificationMembership._verifiedRequirement.eType = RequirementUsage
RequirementConstraintMembership._ownedConstraint.eType = ConstraintUsage
RequirementConstraintMembership._referencedConstraint.eType = ConstraintUsage
FramedConcernMembership._ownedConcern.eType = ConcernUsage
FramedConcernMembership._referencedConcern.eType = ConcernUsage
SubjectMembership._ownedSubjectParameter.eType = Usage
ParameterMembership._ownedMemberParameter.eType = Feature
ActorMembership._ownedActorParameter.eType = PartUsage
StakeholderMembership._ownedStakeholderParameter.eType = PartUsage
SatisfyRequirementUsage._satisfiedRequirement.eType = RequirementUsage
SatisfyRequirementUsage._satisfyingFeature.eType = Feature
AssertConstraintUsage._assertedConstraint.eType = ConstraintUsage
ForLoopActionUsage._seqArgument.eType = Expression
LoopActionUsage._bodyAction.eType = ActionUsage
InvocationExpression.argument.eType = Expression
AssignmentActionUsage._targetArgument.eType = Expression
AssignmentActionUsage._valueExpression.eType = Expression
AssignmentActionUsage._referent.eType = Feature
IfActionUsage._elseAction.eType = ActionUsage
IfActionUsage._thenAction.eType = ActionUsage
IfActionUsage._ifArgument.eType = Expression
SendActionUsage._receiverArgument.eType = Expression
SendActionUsage._payloadArgument.eType = Expression
SendActionUsage._senderArgument.eType = Expression
PerformActionUsage._performedAction.eType = ActionUsage
WhileLoopActionUsage._whileArgument.eType = Expression
WhileLoopActionUsage._untilArgument.eType = Expression
StateDefinition.state.eType = StateUsage
StateDefinition._entryAction.eType = ActionUsage
StateDefinition._doAction.eType = ActionUsage
StateDefinition._exitAction.eType = ActionUsage
ExhibitStateUsage._exhibitedState.eType = StateUsage
IncludeUseCaseUsage._useCaseIncluded.eType = UseCaseUsage
OperatorExpression.operand.eType = Expression
FeatureChainExpression._targetFeature.eType = Feature
Usage._owningDefinition.eType = Definition
Usage._owningUsage.eType = Usage
Usage.nestedUsage.eType = Usage
Usage.nestedUsage.eOpposite = Usage._owningUsage
Feature._owningFeatureMembership.eType = FeatureMembership
FeatureMembership._ownedMemberFeature.eType = Feature
FeatureMembership._ownedMemberFeature.eOpposite = Feature._owningFeatureMembership
Definition.ownedUsage.eType = Usage
Definition.ownedUsage.eOpposite = Usage._owningDefinition
PortDefinition._conjugatedPortDefinition.eType = ConjugatedPortDefinition
ConjugatedPortDefinition._originalPortDefinition.eType = PortDefinition
ConjugatedPortDefinition._originalPortDefinition.eOpposite = (
    PortDefinition._conjugatedPortDefinition
)

otherClassifiers = [
    PortionKind,
    RequirementConstraintKind,
    TriggerKind,
    StateSubactionKind,
    TransitionFeatureKind,
]
