"""Definition of meta model for KerML."""
# ruff: noqa: C901
from functools import partial
import pyecore.ecore as Ecore
from pyecore.ecore import (
    EReference,
    EDerivedCollection,
    EAttribute,
    abstract,
    EEnum,
    EPackage,
    EObject,
    MetaEClass,
)
from gaphor.UMLTypes.uml_types import String, Real, Boolean, Integer


name = "kerml"
nsURI = "https://www.omg.org/spec/KerML/20230201"
nsPrefix = "kerml"

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}  # type: ignore
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)
VisibilityKind = EEnum("VisibilityKind", literals=["private", "protected", "public"])

FeatureDirectionKind = EEnum("FeatureDirectionKind", literals=["in_", "inout", "out"])


class DerivedOwnedelement(EDerivedCollection):
    pass


class DerivedDocumentation(EDerivedCollection):
    pass


class DerivedOwnedannotation(EDerivedCollection):
    pass


class DerivedTextualrepresentation(EDerivedCollection):
    pass


@abstract
class Element(EObject, metaclass=MetaEClass):
    """<p>An <code>Element</code> is a constituent of a model that is uniquely identified relative to all other <code>Elements</code>. It can have <code>Relationships</code> with other <code>Elements</code>. Some of these <code>Relationships</code> might imply ownership of other <code>Elements</code>, which means that if an <code>Element</code> is deleted from a model, then so are all the <code>Elements</code> that it owns.</p>

    ownedElement = ownedRelationship.ownedRelatedElement
    owner = owningRelationship.owningRelatedElement
    qualifiedName =
        if owningNamespace = null then null
        else if owningNamespace.owner = null then escapedName()
        else if owningNamespace.qualifiedName = null or
                escapedName() = null then null
        else owningNamespace.qualifiedName + '::' + escapedName()
        endif endif endif
    documentation = ownedElement->selectByKind(Documentation)
    ownedAnnotation = ownedRelationship->
        selectByKind(Annotation)->
        select(a | a.annotatedElement = self)
    name = effectiveName()
    ownedRelationship->exists(isImplied) implies isImpliedIncluded
    isLibraryElement = libraryNamespace() <>null

    shortName = effectiveShortName()
    owningNamespace =
        if owningMembership = null then null
        else owningMembership.membershipOwningNamespace
        endif
    textualRepresentation = ownedElement->selectByKind(TextualRepresentation)"""

    elementId = EAttribute(
        eType=String, unique=True, derived=False, changeable=True, iD=True
    )
    aliasIds = EAttribute(
        eType=String, unique=True, derived=False, changeable=True, upper=-1
    )
    declaredShortName = EAttribute(
        eType=String, unique=True, derived=False, changeable=True
    )
    declaredName = EAttribute(eType=String, unique=True, derived=False, changeable=True)
    _shortName = EAttribute(
        eType=String,
        unique=True,
        derived=True,
        changeable=True,
        name="shortName",
        transient=True,
    )
    _name = EAttribute(
        eType=String,
        unique=True,
        derived=True,
        changeable=True,
        name="name",
        transient=True,
    )
    _qualifiedName = EAttribute(
        eType=String,
        unique=True,
        derived=True,
        changeable=True,
        name="qualifiedName",
        transient=True,
    )
    isImpliedIncluded = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    _isLibraryElement = EAttribute(
        eType=Boolean,
        unique=True,
        derived=True,
        changeable=True,
        name="isLibraryElement",
        transient=True,
    )
    _owningMembership = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningMembership",
        transient=True,
    )
    _owningNamespace = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningNamespace",
        transient=True,
    )
    owningRelationship = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    ownedRelationship = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )
    _owner = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owner",
        transient=True,
    )
    ownedElement = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedelement,
    )
    documentation = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedDocumentation,
    )
    ownedAnnotation = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedannotation,
    )
    textualRepresentation = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedTextualrepresentation,
    )

    @property
    def owningMembership(self):
        raise NotImplementedError("Missing implementation for owningMembership")

    @owningMembership.setter
    def owningMembership(self, value):
        raise NotImplementedError("Missing implementation for owningMembership")

    @property
    def owningNamespace(self):
        raise NotImplementedError("Missing implementation for owningNamespace")

    @owningNamespace.setter
    def owningNamespace(self, value):
        raise NotImplementedError("Missing implementation for owningNamespace")

    @property
    def owner(self):
        raise NotImplementedError("Missing implementation for owner")

    @owner.setter
    def owner(self, value):
        raise NotImplementedError("Missing implementation for owner")

    @property
    def shortName(self):
        raise NotImplementedError("Missing implementation for shortName")

    @shortName.setter
    def shortName(self, value):
        raise NotImplementedError("Missing implementation for shortName")

    @property
    def name(self):
        raise NotImplementedError("Missing implementation for name")

    @name.setter
    def name(self, value):
        raise NotImplementedError("Missing implementation for name")

    @property
    def qualifiedName(self):
        raise NotImplementedError("Missing implementation for qualifiedName")

    @qualifiedName.setter
    def qualifiedName(self, value):
        raise NotImplementedError("Missing implementation for qualifiedName")

    @property
    def isLibraryElement(self):
        raise NotImplementedError("Missing implementation for isLibraryElement")

    @isLibraryElement.setter
    def isLibraryElement(self, value):
        raise NotImplementedError("Missing implementation for isLibraryElement")

    def __init__(
        self,
        *,
        owningMembership=None,
        owningNamespace=None,
        owningRelationship=None,
        elementId=None,
        ownedRelationship=None,
        owner=None,
        ownedElement=None,
        documentation=None,
        ownedAnnotation=None,
        textualRepresentation=None,
        aliasIds=None,
        declaredShortName=None,
        declaredName=None,
        shortName=None,
        name=None,
        qualifiedName=None,
        isImpliedIncluded=None,
        isLibraryElement=None
    ):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if elementId is not None:
            self.elementId = elementId

        if aliasIds:
            self.aliasIds.extend(aliasIds)

        if declaredShortName is not None:
            self.declaredShortName = declaredShortName

        if declaredName is not None:
            self.declaredName = declaredName

        if shortName is not None:
            self.shortName = shortName

        if name is not None:
            self.name = name

        if qualifiedName is not None:
            self.qualifiedName = qualifiedName

        if isImpliedIncluded is not None:
            self.isImpliedIncluded = isImpliedIncluded

        if isLibraryElement is not None:
            self.isLibraryElement = isLibraryElement

        if owningMembership is not None:
            self.owningMembership = owningMembership

        if owningNamespace is not None:
            self.owningNamespace = owningNamespace

        if owningRelationship is not None:
            self.owningRelationship = owningRelationship

        if ownedRelationship:
            self.ownedRelationship.extend(ownedRelationship)

        if owner is not None:
            self.owner = owner

        if ownedElement:
            self.ownedElement.extend(ownedElement)

        if documentation:
            self.documentation.extend(documentation)

        if ownedAnnotation:
            self.ownedAnnotation.extend(ownedAnnotation)

        if textualRepresentation:
            self.textualRepresentation.extend(textualRepresentation)

    def escapedName(self):
        """<p>Return <code>name</code>, if that is not null, otherwise the <code>shortName</code>, if that is not null, otherwise null. If the returned value is non-null, it is returned as-is if it has the form of a basic name, or, otherwise, represented as a restricted name according to the lexical structure of the KerML textual notation (i.e., surrounded by single quote characters and with special characters escaped).</p>"""
        raise NotImplementedError("operation escapedName(...) not yet implemented")

    def effectiveShortName(self):
        """<p>Return an effective <code>shortName</code> for this <code>Element</code>. By default this is the same as its <code>declaredShortName</code>.</p>"""
        raise NotImplementedError(
            "operation effectiveShortName(...) not yet implemented"
        )

    def effectiveName(self):
        """<p>Return an effective <code>name</code> for this <code>Element</code>. By default this is the same as its <code>declaredName</code>.</p>"""
        raise NotImplementedError("operation effectiveName(...) not yet implemented")

    def libraryNamespace(self):
        """<p>By default, return the library Namespace of the <code>owningRelationship</code> of this Element, if it has one.</p>"""
        raise NotImplementedError("operation libraryNamespace(...) not yet implemented")


class DerivedRelatedelement(EDerivedCollection):
    pass


@abstract
class Relationship(Element):
    """<p>A <code>Relationship</code> is an <code>Element</code> that relates other <code>Element</code>. Some of its <code>relatedElements</code> may be owned, in which case those <code>ownedRelatedElements</code> will be deleted from a model if their <code>owningRelationship</code> is. A <code>Relationship</code> may also be owned by another <code>Element</code>, in which case the <code>ownedRelatedElements</code> of the <code>Relationship</code> are also considered to be transitively owned by the <code>owningRelatedElement</code> of the <code>Relationship</code>.</p>

    <p>The <code>relatedElements</code> of a <code>Relationship</code> are divided into <code>source</code> and <code>target</code> <code>Elements</code>. The <code>Relationship</code> is considered to be directed from the <code>source</code> to the <code>target</code> <code>Elements</code>. An undirected <code>Relationship</code> may have either all <code>source</code> or all <code>target</code> <code>Elements</code>.</p>

    <p>A &quot;relationship <code>Element</code>&quot; in the abstract syntax is generically any <code>Element</code> that is an instance of either <code>Relationship</code> or a direct or indirect specialization of <code>Relationship</code>. Any other kind of <code>Element</code> is a &quot;non-relationship <code>Element</code>&quot;. It is a convention of that non-relationship <code>Elements</code> are <em>only</em> related via reified relationship <code>Elements</code>. Any meta-associations directly between non-relationship <code>Elements</code> must be derived from underlying reified <code>Relationship</code>.</p>

    relatedElement = source->union(target)"""

    isImplied = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    ownedRelatedElement = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )
    owningRelatedElement = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    relatedElement = EReference(
        ordered=True,
        unique=False,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedRelatedelement,
    )
    target = EReference(
        ordered=True, unique=True, containment=False, derived=False, upper=-1
    )
    source = EReference(
        ordered=True, unique=True, containment=False, derived=False, upper=-1
    )

    def __init__(
        self,
        *,
        ownedRelatedElement=None,
        owningRelatedElement=None,
        relatedElement=None,
        target=None,
        source=None,
        isImplied=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if isImplied is not None:
            self.isImplied = isImplied

        if ownedRelatedElement:
            self.ownedRelatedElement.extend(ownedRelatedElement)

        if owningRelatedElement is not None:
            self.owningRelatedElement = owningRelatedElement

        if relatedElement:
            self.relatedElement.extend(relatedElement)

        if target:
            self.target.extend(target)

        if source:
            self.source.extend(source)


class DerivedMembership(EDerivedCollection):
    pass


class DerivedOwnedimport(EDerivedCollection):
    pass


class DerivedMember(EDerivedCollection):
    pass


class DerivedOwnedmember(EDerivedCollection):
    pass


class DerivedImportedmembership(EDerivedCollection):
    pass


class DerivedOwnedmembership(EDerivedCollection):
    pass


class Namespace(Element):
    """<p>A <code>Namespace</code> is an <code>Element</code> that contains other <code>Element</code>, known as its <code>members</code>, via <code>Membership</code> <code>Relationships</code> with those <code>Elements</code>. The <code>members</code> of a <code>Namespace</code> may be owned by the <code>Namespace</code>, aliased in the <code>Namespace</code>, or imported into the <code>Namespace</code> via <code>Import</code> <code>Relationships</code> with other <code>Namespace</code>.</p>

    <p>A <code>Namespace</code> can provide names for its <code>members</code> via the <code>memberNames</code> and <code>memberShortNames</code> specified by the <code>Memberships</code> in the <code>Namespace</code>. If a <code>Membership</code> specifies a <code>memberName</code> and/or <code>memberShortName</code>, then that those are names of the corresponding <code>memberElement</code> relative to the <code>Namespace</code>. For an <code>OwningMembership</code>, the <code>owningMemberName</code> and <code>owningMemberShortName</code> are given by the <code>Element</code> <code>name</code> and <code>shortName</code>. Note that the same <code>Element</code> may be the <code>memberElement</code> of multiple <code>Memberships</code> in a <code>Namespace</code> (though it may be owned at most once), each of which may define a separate alias for the <code>Element</code> relative to the <code>Namespace</code>.</p>

    membership->forAll(m1 |
        membership->forAll(m2 |
            m1 <> m2 implies m1.isDistinguishableFrom(m2)))
    member = membership.memberElement
    ownedMember = ownedMembership->selectByKind(OwningMembership).ownedMemberElement
    importedMembership = importedMemberships(Set{})
    ownedImport = ownedRelationship->selectByKind(Import)
    ownedMembership = ownedRelationship->selectByKind(Membership)"""

    membership = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedMembership,
    )
    ownedImport = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedimport,
    )
    member = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedMember,
    )
    ownedMember = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedmember,
    )
    importedMembership = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedImportedmembership,
    )
    ownedMembership = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedmembership,
    )

    def __init__(
        self,
        *,
        membership=None,
        ownedImport=None,
        member=None,
        ownedMember=None,
        importedMembership=None,
        ownedMembership=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if membership:
            self.membership.extend(membership)

        if ownedImport:
            self.ownedImport.extend(ownedImport)

        if member:
            self.member.extend(member)

        if ownedMember:
            self.ownedMember.extend(ownedMember)

        if importedMembership:
            self.importedMembership.extend(importedMembership)

        if ownedMembership:
            self.ownedMembership.extend(ownedMembership)

    def namesOf(self, element=None):
        """<p>Return the names of the given <code>element</code> as it is known in this <code>Namespace</code>.</p>"""
        raise NotImplementedError("operation namesOf(...) not yet implemented")

    def visibilityOf(self, mem=None):
        """<p>Returns this visibility of <code>mem</code> relative to this <code>Namespace</code>. If <code>mem</code> is an <code>importedMembership</code>, this is the <code>visibility</code> of its Import. Otherwise it is the <code>visibility</code> of the <code>Membership</code> itself.</p>"""
        raise NotImplementedError("operation visibilityOf(...) not yet implemented")

    def visibleMemberships(self, excluded=None, isRecursive=None, includeAll=None):
        """<p>If <code>includeAll = true</code>, then return all the <code>Memberships</code> of this <code>Namespace</code>. Otherwise, return only the publicly visible <code>Memberships</code> of this <code>Namespace</code> (which includes those <code>ownedMemberships</code> that have a <code>visibility</code> of <code>public</code> and those <code>importedMemberships</code> imported with a <code>visibility</code> of <code>public</code>). If <code>isRecursive = true</code>, also recursively include all visible <code>Memberships</code> of any visible owned <code>Namespaces</code>.</p>"""
        raise NotImplementedError(
            "operation visibleMemberships(...) not yet implemented"
        )

    def importedMemberships(self, excluded=None):
        """<p>Derive the imported <code>Memberships</code> of this <code>Namespace</code> as the <code>importedMembership</code> of all <code>ownedImports</code>, excluding those Imports whose <code>importOwningNamespace</code> is in the <code>excluded</code> set, and excluding <code>Memberships</code> that have distinguisibility collisions with each other or with any <code>ownedMembership</code>.</p>"""
        raise NotImplementedError(
            "operation importedMemberships(...) not yet implemented"
        )

    def resolve(self, qualifiedName=None):
        """<p>Resolve the given qualified name to the named <code>Membership</code> (if any), starting with this <code>Namespace</code> as the local scope. The qualified name string must conform to the concrete syntax of the KerML textual notation. According to the KerML name resolution rules every qualified name will resolve to either a single <code>Membership</code>, or to none.</p>"""
        raise NotImplementedError("operation resolve(...) not yet implemented")

    def resolveGlobal(self, qualifiedName=None):
        """<p>Resolve the given qualified name to the named <code>Membership</code> (if any) in the effective global <code>Namespace</code> that is the outermost naming scope. The qualified name string must conform to the concrete syntax of the KerML textual notation.</p>"""
        raise NotImplementedError("operation resolveGlobal(...) not yet implemented")

    def resolveLocal(self, name=None):
        """<p>Resolve a simple <code>name</code> starting with this <code>Namespace</code> as the local scope, and continuing with containing outer scopes as necessary. However, if this <code>Namespace</code> is a root <code>Namespace</code>, then the resolution is done directly in global scope.</p>"""
        raise NotImplementedError("operation resolveLocal(...) not yet implemented")

    def resolveVisible(self, name=None):
        """<p>Resolve a simple name from the visible <code>Memberships</code> of this <code>Namespace</code>.</p>"""
        raise NotImplementedError("operation resolveVisible(...) not yet implemented")

    def qualificationOf(self, qualifiedName=None):
        """<p>Return a string with valid KerML syntax representing the qualification part of a given <code>qualifiedName</code>, that is, a qualified name with all the segment names of the given name except the last. If the given <code>qualifiedName</code> has only one segment, then return null.</p>"""
        raise NotImplementedError("operation qualificationOf(...) not yet implemented")

    def unqualifiedNameOf(self, qualifiedName=None):
        """<p>Return the simple name that is the last segment name of the given <code>qualifiedName</code>. If this segment name has the form of a KerML unrestricted name, then "unescape" it by removing the surrounding single quotes and replacing all escape sequences with the specified character.</p>"""
        raise NotImplementedError(
            "operation unqualifiedNameOf(...) not yet implemented"
        )


class DerivedAnnotatedelement(EDerivedCollection):
    pass


class AnnotatingElement(Element):
    """<p>An <code>AnnotatingElement</code> is an <code>Element</code> that provides additional description of or metadata on some other <code>Element</code>. An <code>AnnotatingElement</code> is either attached to its <code>annotatedElements</code> by <code>Annotation</code> <code>Relationships</code>, or it implicitly annotates its <code>owningNamespace</code>.</p>

    annotatedElement =
     if annotation->notEmpty() then annotation.annotatedElement
     else Sequence{owningNamespace} endif"""

    annotation = EReference(
        ordered=True, unique=True, containment=False, derived=False, upper=-1
    )
    annotatedElement = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedAnnotatedelement,
    )

    def __init__(self, *, annotation=None, annotatedElement=None, **kwargs):
        super().__init__(**kwargs)

        if annotation:
            self.annotation.extend(annotation)

        if annotatedElement:
            self.annotatedElement.extend(annotatedElement)


class Dependency(Relationship):
    """<p>A <code>Dependency</code> is a <code>Relationship</code> that indicates that one or more <code>client</code> <code>Elements</code> require one more <code>supplier</code> <code>Elements</code> for their complete specification. In general, this means that a change to one of the <code>supplier</code> <code>Elements</code> may necessitate a change to, or re-specification of, the <code>client</code> <code>Elements</code>.</p>

    <p>Note that a <code>Dependency</code> is entirely a model-level <code>Relationship</code>, without instance-level semantics.</p>
    """

    client = EReference(
        ordered=True, unique=True, containment=False, derived=False, upper=-1
    )
    supplier = EReference(
        ordered=True, unique=True, containment=False, derived=False, upper=-1
    )

    def __init__(self, *, client=None, supplier=None, **kwargs):
        super().__init__(**kwargs)

        if client:
            self.client.extend(client)

        if supplier:
            self.supplier.extend(supplier)


class Membership(Relationship):
    """<p>A <code>Membership</code> is a <code>Relationship</code> between a <code>Namespace</code> and an <code>Element</code> that indicates the <code>Element</code> is a <code>member</code> of (i.e., is contained in) the Namespace. Any <code>memberNames</code> specify how the <code>memberElement</code> is identified in the <code>Namespace</code> and the <code>visibility</code> specifies whether or not the <code>memberElement</code> is publicly visible from outside the <code>Namespace</code>.</p>

    <p>If a <code>Membership</code> is an <code>OwningMembership</code>, then it owns its <code>memberElement</code>, which becomes an <code>ownedMember</code> of the <code>membershipOwningNamespace</code>. Otherwise, the <code>memberNames</code> of a <code>Membership</code> are effectively aliases within the <code>membershipOwningNamespace</code> for an <code>Element</code> with a separate <code>OwningMembership</code> in the same or a different <code>Namespace</code>.</p>

    <p>&nbsp;</p>

    memberElementId = memberElement.elementId"""

    _memberElementId = EAttribute(
        eType=String,
        unique=True,
        derived=True,
        changeable=True,
        name="memberElementId",
        transient=True,
    )
    memberShortName = EAttribute(
        eType=String, unique=True, derived=False, changeable=True
    )
    memberName = EAttribute(eType=String, unique=True, derived=False, changeable=True)
    visibility = EAttribute(
        eType=VisibilityKind,
        unique=True,
        derived=False,
        changeable=True,
        default_value=VisibilityKind.public,
    )
    _membershipOwningNamespace = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="membershipOwningNamespace",
        transient=True,
    )
    memberElement = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )

    @property
    def memberElementId(self):
        raise NotImplementedError("Missing implementation for memberElementId")

    @memberElementId.setter
    def memberElementId(self, value):
        raise NotImplementedError("Missing implementation for memberElementId")

    @property
    def membershipOwningNamespace(self):
        raise NotImplementedError(
            "Missing implementation for membershipOwningNamespace"
        )

    @membershipOwningNamespace.setter
    def membershipOwningNamespace(self, value):
        raise NotImplementedError(
            "Missing implementation for membershipOwningNamespace"
        )

    def __init__(
        self,
        *,
        memberElementId=None,
        membershipOwningNamespace=None,
        memberShortName=None,
        memberElement=None,
        memberName=None,
        visibility=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if memberElementId is not None:
            self.memberElementId = memberElementId

        if memberShortName is not None:
            self.memberShortName = memberShortName

        if memberName is not None:
            self.memberName = memberName

        if visibility is not None:
            self.visibility = visibility

        if membershipOwningNamespace is not None:
            self.membershipOwningNamespace = membershipOwningNamespace

        if memberElement is not None:
            self.memberElement = memberElement

    def isDistinguishableFrom(self, other=None):
        """<p>Whether this <code>Membership</code> is distinguishable from a given <code>other</code> <code>Membership</code>. By default, this is true if this <code>Membership</code> has no <code>memberShortName</code> or <code>memberName</code>; or each of the <code>memberShortName</code> and <code>memberName</code> are different than both of those of the <code>other</code> <code>Membership</code>; or neither of the metaclasses of the <code>memberElement</code> of this <code>Membership</code> and the <code>memberElement</code> of the <code>other</code> <code>Membership</code> conform to the other. But this may be overridden in specializations of <code>Membership</code>.</p>"""
        raise NotImplementedError(
            "operation isDistinguishableFrom(...) not yet implemented"
        )


@abstract
class Import(Relationship):
    """<p>An <code>Import</code> is an <code>Relationship</code> between its <code>importOwningNamespace</code> and either a <code>Membership</code> (for a <code>MembershipImport</code>) or another <code>Namespace</code> (for a <code>NamespaceImport</code>), which determines a set of <code>Memberships</code> that become <code>importedMemberships</code> of the <code>importOwningNamespace</code>. If <code>isImportAll = false</code> (the default), then only public <code>Memberships</code> are considered &quot;visible&quot;. If <code>isImportAll = true</code>, then all <code>Memberships</code> are considered &quot;visible&quot;, regardless of their declared <code>visibility</code>. If <code>isRecursive = true</code>, then visible <code>Memberships</code> are also recursively imported from owned sub-<code>Namespaces</code>.</p>"""

    visibility = EAttribute(
        eType=VisibilityKind,
        unique=True,
        derived=False,
        changeable=True,
        default_value=VisibilityKind.public,
    )
    isRecursive = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    isImportAll = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    _importedElement = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="importedElement",
        transient=True,
    )
    _importOwningNamespace = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="importOwningNamespace",
        transient=True,
    )

    @property
    def importedElement(self):
        raise NotImplementedError("Missing implementation for importedElement")

    @importedElement.setter
    def importedElement(self, value):
        raise NotImplementedError("Missing implementation for importedElement")

    @property
    def importOwningNamespace(self):
        raise NotImplementedError("Missing implementation for importOwningNamespace")

    @importOwningNamespace.setter
    def importOwningNamespace(self, value):
        raise NotImplementedError("Missing implementation for importOwningNamespace")

    def __init__(
        self,
        *,
        visibility=None,
        isRecursive=None,
        isImportAll=None,
        importedElement=None,
        importOwningNamespace=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if visibility is not None:
            self.visibility = visibility

        if isRecursive is not None:
            self.isRecursive = isRecursive

        if isImportAll is not None:
            self.isImportAll = isImportAll

        if importedElement is not None:
            self.importedElement = importedElement

        if importOwningNamespace is not None:
            self.importOwningNamespace = importOwningNamespace

    def importedMemberships(self, excluded=None):
        """<p>Returns Memberships that are to become <code>importedMemberships</code> of the <code>importOwningNamespace</code>. (The <code>excluded</code> parameter is used to handle the possibility of circular Import Relationships.)</p>"""
        raise NotImplementedError(
            "operation importedMemberships(...) not yet implemented"
        )


class Comment(AnnotatingElement):
    """<p>A <code>Comment</code> is an <code>AnnotatingElement</code> whose <code>body</code> in some way describes its <code>annotatedElements</code>.</p>"""

    locale = EAttribute(eType=String, unique=True, derived=False, changeable=True)
    body = EAttribute(eType=String, unique=True, derived=False, changeable=True)

    def __init__(self, *, locale=None, body=None, **kwargs):
        super().__init__(**kwargs)

        if locale is not None:
            self.locale = locale

        if body is not None:
            self.body = body


class Annotation(Relationship):
    """<p>An <code>Annotation</code> is a Relationship between an <code>AnnotatingElement</code> and the <code>Element</code> that is annotated by that <code>AnnotatingElement</code>.</p>"""

    annotatedElement = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _owningAnnotatedElement = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningAnnotatedElement",
        transient=True,
    )
    annotatingElement = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )

    @property
    def owningAnnotatedElement(self):
        raise NotImplementedError("Missing implementation for owningAnnotatedElement")

    @owningAnnotatedElement.setter
    def owningAnnotatedElement(self, value):
        raise NotImplementedError("Missing implementation for owningAnnotatedElement")

    def __init__(
        self,
        *,
        annotatedElement=None,
        owningAnnotatedElement=None,
        annotatingElement=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if annotatedElement is not None:
            self.annotatedElement = annotatedElement

        if owningAnnotatedElement is not None:
            self.owningAnnotatedElement = owningAnnotatedElement

        if annotatingElement is not None:
            self.annotatingElement = annotatingElement


class TextualRepresentation(AnnotatingElement):
    """<p>A <code>TextualRepresentation</code> is an <code>AnnotatingElement</code> whose <code>body</code> represents the <code>representedElement</code> in a given <code>language</code>. The <code>representedElement</code> must be the <code>owner</code> of the <code>TextualRepresentation</code>. The named <code>language</code> can be a natural language, in which case the <code>body</code> is an informal representation, or an artificial language, in which case the <code>body</code> is expected to be a formal, machine-parsable representation.</p>

    <p>If the named <code>language</code> of a <code>TextualRepresentation</code> is machine-parsable, then the <code>body</code> text should be legal input text as defined for that <code>language</code>. The interpretation of the named language string shall be case insensitive. The following <code>language</code> names are defined to correspond to the given standard languages:</p>

    <table border="1" cellpadding="1" cellspacing="1" width="498">
            <thead>
            </thead>
            <tbody>
                    <tr>
                            <td style="text-align: center; width: 154px;"><code>kerml</code></td>
                            <td style="width: 332px;">Kernel Modeling Language</td>
                    </tr>
                    <tr>
                            <td style="text-align: center; width: 154px;"><code>ocl</code></td>
                            <td style="width: 332px;">Object Constraint Language</td>
                    </tr>
                    <tr>
                            <td style="text-align: center; width: 154px;"><code>alf</code></td>
                            <td style="width: 332px;">Action Language for fUML</td>
                    </tr>
            </tbody>
    </table>

    <p>Other specifications may define specific <code>language</code> strings, other than those shown above, to be used to indicate the use of languages from those specifications in KerML <code>TextualRepresentation</code>.</p>

    <p>If the <code>language</code> of a <code>TextualRepresentation</code> is &quot;<code>kerml</code>&quot;, then the <code>body</code> text shall be a legal representation of the <code>representedElement</code> in the KerML textual concrete syntax. A conforming tool can use such a <code>TextualRepresentation</code> <code>Annotation</code> to record the original KerML concrete syntax text from which an <code>Element</code> was parsed. In this case, it is a tool responsibility to ensure that the <code>body</code> of the <code>TextualRepresentation</code> remains correct (or the Annotation is removed) if the annotated <code>Element</code> changes other than by re-parsing the <code>body</code> text.</p>

    <p>An <code>Element</code> with a <code>TextualRepresentation</code> in a language other than KerML is essentially a semantically &quot;opaque&quot; <code>Element</code> specified in the other language. However, a conforming KerML tool may interpret such an element consistently with the specification of the named language.</p>
    """

    language = EAttribute(eType=String, unique=True, derived=False, changeable=True)
    body = EAttribute(eType=String, unique=True, derived=False, changeable=True)
    _representedElement = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="representedElement",
        transient=True,
    )

    @property
    def representedElement(self):
        raise NotImplementedError("Missing implementation for representedElement")

    @representedElement.setter
    def representedElement(self, value):
        raise NotImplementedError("Missing implementation for representedElement")

    def __init__(self, *, language=None, body=None, representedElement=None, **kwargs):
        super().__init__(**kwargs)

        if language is not None:
            self.language = language

        if body is not None:
            self.body = body

        if representedElement is not None:
            self.representedElement = representedElement


class Specialization(Relationship):
    """<p><code>Specialization</code> is a <code>Relationship</code> between two <code>Types</code> that requires all instances of the <code>specific</code> type to also be instances of the <code>general</code> Type (i.e., the set of instances of the <code>specific</code> Type is a <em>subset</em> of those of the <code>general</code> Type, which might be the same set).</p>

    not specific.isConjugated"""

    _owningType = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningType",
        transient=True,
    )
    general = EReference(ordered=False, unique=True, containment=False, derived=False)
    specific = EReference(ordered=False, unique=True, containment=False, derived=False)

    @property
    def owningType(self):
        raise NotImplementedError("Missing implementation for owningType")

    @owningType.setter
    def owningType(self, value):
        raise NotImplementedError("Missing implementation for owningType")

    def __init__(self, *, owningType=None, general=None, specific=None, **kwargs):
        super().__init__(**kwargs)

        if owningType is not None:
            self.owningType = owningType

        if general is not None:
            self.general = general

        if specific is not None:
            self.specific = specific


class DerivedOwnedfeaturemembership(EDerivedCollection):
    pass


class DerivedOwnedfeature(EDerivedCollection):
    pass


class DerivedOwnedendfeature(EDerivedCollection):
    pass


class DerivedFeature(EDerivedCollection):
    pass


class DerivedInput(EDerivedCollection):
    pass


class DerivedOutput(EDerivedCollection):
    pass


class DerivedInheritedmembership(EDerivedCollection):
    pass


class DerivedEndfeature(EDerivedCollection):
    pass


class DerivedInheritedfeature(EDerivedCollection):
    pass


class DerivedUnioningtype(EDerivedCollection):
    pass


class DerivedOwnedintersecting(EDerivedCollection):
    pass


class DerivedIntersectingtype(EDerivedCollection):
    pass


class DerivedOwnedunioning(EDerivedCollection):
    pass


class DerivedOwneddisjoining(EDerivedCollection):
    pass


class DerivedFeaturemembership(EDerivedCollection):
    pass


class DerivedDifferencingtype(EDerivedCollection):
    pass


class DerivedOwneddifferencing(EDerivedCollection):
    pass


class DerivedDirectedfeature(EDerivedCollection):
    pass


class DerivedOwnedspecialization(EDerivedCollection):
    pass


class Type(Namespace):
    """<p>A <code>Type</code> is a <code>Namespace</code> that is the most general kind of <code>Element</code> supporting the semantics of classification. A <code>Type</code> may be a <code>Classifier</code> or a <code>Feature</code>, defining conditions on what is classified by the <code>Type</code> (see also the description of <code>isSufficient</code>).</p>

    ownedSpecialization = ownedRelationship->selectByKind(Specialization)->
        select(s | s.special = self)

    multiplicity =
        let ownedMultiplicities: Sequence(Multiplicity) =
            ownedMember->selectByKind(Multiplicity) in
        if ownedMultiplicities->isEmpty() then null
        else ownedMultiplicities->first()
        endif
    ownedFeatureMembership = ownedRelationship->selectByKind(FeatureMembership)
    let ownedConjugators: Sequence(Conjugator) =
        ownedRelationship->selectByKind(Conjugation) in
        ownedConjugator =
            if ownedConjugators->isEmpty() then null
            else ownedConjugators->at(1) endif
    output =
        if isConjugated then
            conjugator.originalType.input
        else
            feature->select(direction = out or direction = inout)
        endif
    input =
        if isConjugated then
            conjugator.originalType.output
        else
            feature->select(direction = _'in' or direction = inout)
        endif
    inheritedMembership = inheritedMemberships(Set{})
    specializesFromLibrary('Base::Anything')
    directedFeature = feature->select(f | directionOf(f) <> null)
    feature = featureMembership.ownedMemberFeature
    featureMembership = ownedMembership->union(
        inheritedMembership->selectByKind(FeatureMembership))
    ownedFeature = ownedFeatureMembership.ownedMemberFeature
    differencingType = ownedDifferencing.differencingType
    intersectingType->excludes(self)
    differencingType->excludes(self)
    unioningType = ownedUnioning.unioningType
    unioningType->excludes(self)
    intersectingType = ownedIntersecting.intersectingType
    ownedRelationship->selectByKind(Conjugator)->size() <= 1
    ownedMember->selectByKind(Multiplicity)->size() <= 1
    endFeature = feature->select(isEnd)
    ownedRelationship->selectByKind(Disjoining)
    ownedRelationship->selectByKind(Unioning)
    ownedRelationship->selectByKind(Intersecting)
    ownedRelationship->selectByKind(Differencing)
    ownedEndFeature = ownedFeature->select(isEnd)
    inheritedFeature = inheritedMemberships->
        selectByKind(FeatureMembership).memberFeature"""

    isAbstract = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    isSufficient = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    _isConjugated = EAttribute(
        eType=Boolean,
        unique=True,
        derived=True,
        changeable=True,
        name="isConjugated",
        transient=True,
    )
    ownedFeatureMembership = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedfeaturemembership,
    )
    ownedFeature = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedfeature,
    )
    ownedEndFeature = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedendfeature,
    )
    feature = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedFeature,
    )
    input = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedInput,
    )
    output = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOutput,
    )
    inheritedMembership = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedInheritedmembership,
    )
    endFeature = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedEndfeature,
    )
    _ownedConjugator = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedConjugator",
        transient=True,
    )
    inheritedFeature = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedInheritedfeature,
    )
    _multiplicity = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="multiplicity",
        transient=True,
    )
    unioningType = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedUnioningtype,
    )
    ownedIntersecting = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedintersecting,
    )
    intersectingType = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedIntersectingtype,
    )
    ownedUnioning = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedunioning,
    )
    ownedDisjoining = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwneddisjoining,
    )
    featureMembership = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedFeaturemembership,
    )
    differencingType = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedDifferencingtype,
    )
    ownedDifferencing = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwneddifferencing,
    )
    directedFeature = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedDirectedfeature,
    )
    ownedSpecialization = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedspecialization,
    )

    @property
    def ownedConjugator(self):
        raise NotImplementedError("Missing implementation for ownedConjugator")

    @ownedConjugator.setter
    def ownedConjugator(self, value):
        raise NotImplementedError("Missing implementation for ownedConjugator")

    @property
    def isConjugated(self):
        raise NotImplementedError("Missing implementation for isConjugated")

    @isConjugated.setter
    def isConjugated(self, value):
        raise NotImplementedError("Missing implementation for isConjugated")

    @property
    def multiplicity(self):
        raise NotImplementedError("Missing implementation for multiplicity")

    @multiplicity.setter
    def multiplicity(self, value):
        raise NotImplementedError("Missing implementation for multiplicity")

    def __init__(
        self,
        *,
        ownedFeatureMembership=None,
        ownedFeature=None,
        ownedEndFeature=None,
        feature=None,
        input=None,
        output=None,
        isAbstract=None,
        inheritedMembership=None,
        endFeature=None,
        isSufficient=None,
        ownedConjugator=None,
        isConjugated=None,
        inheritedFeature=None,
        multiplicity=None,
        unioningType=None,
        ownedIntersecting=None,
        intersectingType=None,
        ownedUnioning=None,
        ownedDisjoining=None,
        featureMembership=None,
        differencingType=None,
        ownedDifferencing=None,
        directedFeature=None,
        ownedSpecialization=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if isAbstract is not None:
            self.isAbstract = isAbstract

        if isSufficient is not None:
            self.isSufficient = isSufficient

        if isConjugated is not None:
            self.isConjugated = isConjugated

        if ownedFeatureMembership:
            self.ownedFeatureMembership.extend(ownedFeatureMembership)

        if ownedFeature:
            self.ownedFeature.extend(ownedFeature)

        if ownedEndFeature:
            self.ownedEndFeature.extend(ownedEndFeature)

        if feature:
            self.feature.extend(feature)

        if input:
            self.input.extend(input)

        if output:
            self.output.extend(output)

        if inheritedMembership:
            self.inheritedMembership.extend(inheritedMembership)

        if endFeature:
            self.endFeature.extend(endFeature)

        if ownedConjugator is not None:
            self.ownedConjugator = ownedConjugator

        if inheritedFeature:
            self.inheritedFeature.extend(inheritedFeature)

        if multiplicity is not None:
            self.multiplicity = multiplicity

        if unioningType:
            self.unioningType.extend(unioningType)

        if ownedIntersecting:
            self.ownedIntersecting.extend(ownedIntersecting)

        if intersectingType:
            self.intersectingType.extend(intersectingType)

        if ownedUnioning:
            self.ownedUnioning.extend(ownedUnioning)

        if ownedDisjoining:
            self.ownedDisjoining.extend(ownedDisjoining)

        if featureMembership:
            self.featureMembership.extend(featureMembership)

        if differencingType:
            self.differencingType.extend(differencingType)

        if ownedDifferencing:
            self.ownedDifferencing.extend(ownedDifferencing)

        if directedFeature:
            self.directedFeature.extend(directedFeature)

        if ownedSpecialization:
            self.ownedSpecialization.extend(ownedSpecialization)

    def inheritedMemberships(self, excluded=None):
        """<p>Return the inherited <code>Memberships</code> of this <code>Type</code>, excluding those supertypes in the <code>excluded</code> set.</p>"""
        raise NotImplementedError(
            "operation inheritedMemberships(...) not yet implemented"
        )

    def directionOf(self, feature=None):
        """<p>If the given <code>feature</code> is a <code>feature</code> of this <code>Type</code>, then return its direction relative to this <code>Type</code>, taking conjugation into account.</p>"""
        raise NotImplementedError("operation directionOf(...) not yet implemented")

    def allSupertypes(self):
        """<p>Return all <code>Types</code> related to this <code>Type</code> as supertypes directly or transitively by <code>Specialization</code> <code>Relationships</code>.</p>"""
        raise NotImplementedError("operation allSupertypes(...) not yet implemented")

    def specializes(self, supertype=None):
        """<p>Check whether this <code>Type</code> is a direct or indirect specialization of the given <code>supertype<code>.</p>"""
        raise NotImplementedError("operation specializes(...) not yet implemented")

    def specializesFromLibrary(self, libraryTypeName=None):
        """<p>Check whether this <code>Type</code> is a direct or indirect specialization of the named library <code>Type</code>. <code>libraryTypeName</code> must conform to the syntax of a KerML qualified name and must resolve to a <code>Type</code> in global scope.</p>"""
        raise NotImplementedError(
            "operation specializesFromLibrary(...) not yet implemented"
        )


@abstract
class Featuring(Relationship):
    """<p><code>Featuring</code> is a <code>Relationship</code> between a <code>Type</code> and a <code>Feature</code> that is featured by that <code>Type</code>. It asserts that every instance in the domain of the <code>feature</code> must be classified by the <code>type</code>.</p>

    <p><code>Featuring</code> is abstract and does not commit to which of <code>feature</code> or <code>type</code> are the <code>source</code> or <code>target</code> of the <code>Relationship</code>. This commitment is made in the subclasses of <code>Featuring</code>, <code>TypeFeaturing</code> and <code>FeatureMembership</code>, which have opposite directions.</p>
    """

    type = EReference(ordered=False, unique=True, containment=False, derived=False)
    feature = EReference(ordered=False, unique=True, containment=False, derived=False)

    def __init__(self, *, type=None, feature=None, **kwargs):
        super().__init__(**kwargs)

        if type is not None:
            self.type = type

        if feature is not None:
            self.feature = feature


class FeatureInverting(Relationship):
    """<p>A <code>FeatureInverting</code> is a <code>Relationship</code> between <code>Features</code> asserting that their interpretations (sequences) are the reverse of each other, identified as <code>featureInverted</code> and <code>invertingFeature</code>. For example, a <code>Feature</code> identifying each person&#39;s parents is the inverse of a <code>Feature</code> identifying each person&#39;s children. A person identified as a parent of another will identify that other as one of their children.</p>"""

    featureInverted = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    invertingFeature = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _owningFeature = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningFeature",
        transient=True,
    )

    @property
    def owningFeature(self):
        raise NotImplementedError("Missing implementation for owningFeature")

    @owningFeature.setter
    def owningFeature(self, value):
        raise NotImplementedError("Missing implementation for owningFeature")

    def __init__(
        self,
        *,
        featureInverted=None,
        invertingFeature=None,
        owningFeature=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if featureInverted is not None:
            self.featureInverted = featureInverted

        if invertingFeature is not None:
            self.invertingFeature = invertingFeature

        if owningFeature is not None:
            self.owningFeature = owningFeature


class FeatureChaining(Relationship):
    """<p><code>FeatureChaining</code> is a <code>Relationship</code> that makes its target <code>Feature</code> one of the <code>chainingFeatures</code> of its owning <code>Feature</code>.</p>"""

    chainingFeature = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _featureChained = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="featureChained",
        transient=True,
    )

    @property
    def featureChained(self):
        raise NotImplementedError("Missing implementation for featureChained")

    @featureChained.setter
    def featureChained(self, value):
        raise NotImplementedError("Missing implementation for featureChained")

    def __init__(self, *, chainingFeature=None, featureChained=None, **kwargs):
        super().__init__(**kwargs)

        if chainingFeature is not None:
            self.chainingFeature = chainingFeature

        if featureChained is not None:
            self.featureChained = featureChained


class Conjugation(Relationship):
    """<p><code>Conjugation</code> is a <code>Relationship</code> between two types in which the <code>conjugatedType</code> inherits all the <code>Features</code> of the <code>originalType</code>, but with all <code>input</code> and <code>output</code> <code>Features</code> reversed. That is, any <code>Features</code> with a <code>FeatureMembership</code> with <code>direction</code> <em>in</em> relative to the <code>originalType</code> are considered to have an effective <code>direction</code> of <em>out</em> relative to the <code>conjugatedType</code> and, similarly, <code>Features</code> with <code>direction</code> <em>out</em> in the <code>originalType</code> are considered to have an effective <code>direction</code> of <em>in</em> in the <code>originalType</code>. <code>Features</code> with <code>direction</code> <em>inout</em>, or with no <code>direction</code>, in the <code>originalType</code>, are inherited without change.</p>

    <p>A <code>Type</code> may participate as a <code>conjugatedType</code> in at most one <code>Conjugation</code> relationship, and such a <code>Type</code> may not also be the <code>specific</code> <code>Type</code> in any <code>Specialization</code> relationship.</p>
    """

    originalType = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    conjugatedType = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _owningType = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningType",
        transient=True,
    )

    @property
    def owningType(self):
        raise NotImplementedError("Missing implementation for owningType")

    @owningType.setter
    def owningType(self, value):
        raise NotImplementedError("Missing implementation for owningType")

    def __init__(
        self, *, originalType=None, conjugatedType=None, owningType=None, **kwargs
    ):
        super().__init__(**kwargs)

        if originalType is not None:
            self.originalType = originalType

        if conjugatedType is not None:
            self.conjugatedType = conjugatedType

        if owningType is not None:
            self.owningType = owningType


class Intersecting(Relationship):
    """<p><code>Intersecting</code> is a <code>Relationship</code> that makes its <code>intersectingType</code> one of the <code>intersectingTypes</code> of its <code>typeIntersected</code>.</p>"""

    intersectingType = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _typeIntersected = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="typeIntersected",
        transient=True,
    )

    @property
    def typeIntersected(self):
        raise NotImplementedError("Missing implementation for typeIntersected")

    @typeIntersected.setter
    def typeIntersected(self, value):
        raise NotImplementedError("Missing implementation for typeIntersected")

    def __init__(self, *, intersectingType=None, typeIntersected=None, **kwargs):
        super().__init__(**kwargs)

        if intersectingType is not None:
            self.intersectingType = intersectingType

        if typeIntersected is not None:
            self.typeIntersected = typeIntersected


class Unioning(Relationship):
    """<p><code>Unioning</code> is a <code>Relationship</code> that makes its <code>unioningType</code> one of the <code>unioningTypes</code> of its <code>typeUnioned</code>.</p>"""

    unioningType = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _typeUnioned = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="typeUnioned",
        transient=True,
    )

    @property
    def typeUnioned(self):
        raise NotImplementedError("Missing implementation for typeUnioned")

    @typeUnioned.setter
    def typeUnioned(self, value):
        raise NotImplementedError("Missing implementation for typeUnioned")

    def __init__(self, *, unioningType=None, typeUnioned=None, **kwargs):
        super().__init__(**kwargs)

        if unioningType is not None:
            self.unioningType = unioningType

        if typeUnioned is not None:
            self.typeUnioned = typeUnioned


class Disjoining(Relationship):
    """<p>A <code>Disjoining</code> is a <code>Relationship</code> between <code>Types</code> asserted to have interpretations that are not shared (disjoint) between them, identified as <code>typeDisjoined</code> and <code>disjoiningType</code>. For example, a <code>Classifier</code> for mammals is disjoint from a <code>Classifier</code> for minerals, and a <code>Feature</code> for people&#39;s parents is disjoint from a <code>Feature</code> for their children.</p>"""

    typeDisjoined = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    disjoiningType = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _owningType = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningType",
        transient=True,
    )

    @property
    def owningType(self):
        raise NotImplementedError("Missing implementation for owningType")

    @owningType.setter
    def owningType(self, value):
        raise NotImplementedError("Missing implementation for owningType")

    def __init__(
        self, *, typeDisjoined=None, disjoiningType=None, owningType=None, **kwargs
    ):
        super().__init__(**kwargs)

        if typeDisjoined is not None:
            self.typeDisjoined = typeDisjoined

        if disjoiningType is not None:
            self.disjoiningType = disjoiningType

        if owningType is not None:
            self.owningType = owningType


class Differencing(Relationship):
    """<p><code>Differencing</code> is a <code>Relationship</code> that makes its <code>differencingType</code> one of the <code>differencingTypes</code> of its <code>typeDifferenced</code>.</p>"""

    differencingType = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _typeDifferenced = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="typeDifferenced",
        transient=True,
    )

    @property
    def typeDifferenced(self):
        raise NotImplementedError("Missing implementation for typeDifferenced")

    @typeDifferenced.setter
    def typeDifferenced(self, value):
        raise NotImplementedError("Missing implementation for typeDifferenced")

    def __init__(self, *, differencingType=None, typeDifferenced=None, **kwargs):
        super().__init__(**kwargs)

        if differencingType is not None:
            self.differencingType = differencingType

        if typeDifferenced is not None:
            self.typeDifferenced = typeDifferenced


class DerivedFiltercondition(EDerivedCollection):
    pass


class Package(Namespace):
    """<p>A <code>Package</code> is a <code>Namespace</code> used to group <code>Elements</code>, without any instance-level semantics. It may have one or more model-level evaluable <code>filterCondition</code> <code>Expressions</code> used to filter its <code>importedMemberships</code>. Any imported <code>member</code> must meet all of the <code>filterConditions</code>.</p>
    filterCondition = ownedMembership->
        selectByKind(ElementFilterMembership).condition"""

    filterCondition = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedFiltercondition,
    )

    def __init__(self, *, filterCondition=None, **kwargs):
        super().__init__(**kwargs)

        if filterCondition:
            self.filterCondition.extend(filterCondition)

    def includeAsMember(self, element=None):
        """<p>Determine whether the given <code>element</code> meets all the <code>filterConditions</code>.</p>"""
        raise NotImplementedError("operation includeAsMember(...) not yet implemented")


class OwningMembership(Membership):
    """<p>An <code>OwningMembership</code> is a <code>Membership</code> that owns its <code>memberElement</code> as a <code>ownedRelatedElement</code>. The <code>ownedMemberElementM</code> becomes an <code>ownedMember</code> of the <code>membershipOwningNamespace</code>.</p>

    ownedMemberName = ownedMemberElement.name
    ownedMemberShortName = ownedMemberElement.shortName"""

    _ownedMemberElementId = EAttribute(
        eType=String,
        unique=True,
        derived=True,
        changeable=True,
        name="ownedMemberElementId",
        transient=True,
    )
    _ownedMemberShortName = EAttribute(
        eType=String,
        unique=True,
        derived=True,
        changeable=True,
        name="ownedMemberShortName",
        transient=True,
    )
    _ownedMemberName = EAttribute(
        eType=String,
        unique=True,
        derived=True,
        changeable=True,
        name="ownedMemberName",
        transient=True,
    )
    _ownedMemberElement = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedMemberElement",
        transient=True,
    )

    @property
    def ownedMemberElementId(self):
        raise NotImplementedError("Missing implementation for ownedMemberElementId")

    @ownedMemberElementId.setter
    def ownedMemberElementId(self, value):
        raise NotImplementedError("Missing implementation for ownedMemberElementId")

    @property
    def ownedMemberShortName(self):
        raise NotImplementedError("Missing implementation for ownedMemberShortName")

    @ownedMemberShortName.setter
    def ownedMemberShortName(self, value):
        raise NotImplementedError("Missing implementation for ownedMemberShortName")

    @property
    def ownedMemberName(self):
        raise NotImplementedError("Missing implementation for ownedMemberName")

    @ownedMemberName.setter
    def ownedMemberName(self, value):
        raise NotImplementedError("Missing implementation for ownedMemberName")

    @property
    def ownedMemberElement(self):
        raise NotImplementedError("Missing implementation for ownedMemberElement")

    @ownedMemberElement.setter
    def ownedMemberElement(self, value):
        raise NotImplementedError("Missing implementation for ownedMemberElement")

    def __init__(
        self,
        *,
        ownedMemberElementId=None,
        ownedMemberShortName=None,
        ownedMemberName=None,
        ownedMemberElement=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if ownedMemberElementId is not None:
            self.ownedMemberElementId = ownedMemberElementId

        if ownedMemberShortName is not None:
            self.ownedMemberShortName = ownedMemberShortName

        if ownedMemberName is not None:
            self.ownedMemberName = ownedMemberName

        if ownedMemberElement is not None:
            self.ownedMemberElement = ownedMemberElement


class Documentation(Comment):
    """<p><code>Documentation</code> is a <code>Comment</code> that specifically documents a <code>documentedElement</code>, which must be its <code>owner</code>.</p>"""

    _documentedElement = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="documentedElement",
        transient=True,
    )

    @property
    def documentedElement(self):
        raise NotImplementedError("Missing implementation for documentedElement")

    @documentedElement.setter
    def documentedElement(self, value):
        raise NotImplementedError("Missing implementation for documentedElement")

    def __init__(self, *, documentedElement=None, **kwargs):
        super().__init__(**kwargs)

        if documentedElement is not None:
            self.documentedElement = documentedElement


class NamespaceImport(Import):
    """<p>A <code>NamespaceImport</code> is an Import that imports <code>Memberships</code> from its <code>importedNamespace</code> into the <code>importOwningNamespace</code>. If <code> isRecursive = false</code>, then only the visible <code>Memberships</code> of the <code>importOwningNamespace</code> are imported. If <code> isRecursive = true</code>, then, in addition, <code>Memberships</code> are recursively imported from any <code>ownedMembers</code> of the <code>importedNamespace</code> that are <code>Namespaces</code>.</p>

    importedElement = importedNamespace"""

    importedNamespace = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )

    def __init__(self, *, importedNamespace=None, **kwargs):
        super().__init__(**kwargs)

        if importedNamespace is not None:
            self.importedNamespace = importedNamespace


class MembershipImport(Import):
    """<p>A <code>MembershipImport</code> is an <code>Import</code> that imports its <code>importedMembership</code> into the <code>importOwningNamespace</code>. If <code>isRecursive = true</code> and the <code>memberElement</code> of the <code>importedMembership</code> is a <code>Namespace</code>, then the equivalent of a recursive <code>NamespaceImport</code> is also performed on that <code>Namespace</code>.</p>

    importedElement = importedMembership.memberElement"""

    importedMembership = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )

    def __init__(self, *, importedMembership=None, **kwargs):
        super().__init__(**kwargs)

        if importedMembership is not None:
            self.importedMembership = importedMembership


class Subclassification(Specialization):
    """<p><code>Subclassification</code> is <code>Specialization</code> in which both the <code>specific</code> and <code>general</code> <code>Types</code> are <code>Classifier</code>. This means all instances of the specific <code>Classifier</code> are also instances of the general <code>Classifier</code>.</p>"""

    superclassifier = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _owningClassifier = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningClassifier",
        transient=True,
    )
    subclassifier = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )

    @property
    def owningClassifier(self):
        raise NotImplementedError("Missing implementation for owningClassifier")

    @owningClassifier.setter
    def owningClassifier(self, value):
        raise NotImplementedError("Missing implementation for owningClassifier")

    def __init__(
        self,
        *,
        superclassifier=None,
        owningClassifier=None,
        subclassifier=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if superclassifier is not None:
            self.superclassifier = superclassifier

        if owningClassifier is not None:
            self.owningClassifier = owningClassifier

        if subclassifier is not None:
            self.subclassifier = subclassifier


class DerivedType(EDerivedCollection):
    pass


class DerivedOwnedredefinition(EDerivedCollection):
    pass


class DerivedOwnedsubsetting(EDerivedCollection):
    pass


class DerivedOwnedtyping(EDerivedCollection):
    pass


class DerivedFeaturingtype(EDerivedCollection):
    pass


class DerivedOwnedtypefeaturing(EDerivedCollection):
    pass


class DerivedChainingfeature(EDerivedCollection):
    pass


class DerivedOwnedfeatureinverting(EDerivedCollection):
    pass


class DerivedOwnedfeaturechaining(EDerivedCollection):
    pass


class Feature(Type):
    """<p>A <code>Feature</code> is a <code>Type</code> that classifies relations between multiple things (in the universe). The domain of the relation is the intersection of the <code>featuringTypes</code> of the <code>Feature</code>. (The domain of a <code>Feature</code> with no <code>featuringTyps</code> is implicitly the most general <code>Type</code> <em><code>Base::Anything</code></em> from the Kernel Semantic Library.) The co-domain of the relation is the intersection of the <code>types</code> of the <code>Feature</code>.

    <p>In the simplest cases, the <code>featuringTypes</code> and <code>types</code> are <code>Classifiers</code> and the <code>Feature</code> relates two things, one from the domain and one from the range. Examples include cars paired with wheels, people paired with other people, and cars paired with numbers representing the car length.</p>

    <p>Since <code>Features</code> are <code>Types</code>, their <code>featuringTypes</code> and <code>types</code> can be <code>Features</code>. In this case, the <code>Feature</code> effectively classifies relations between relations, which can be interpreted as the sequence of things related by the domain <code>Feature</code> concatenated with the sequence of things related by the co-domain <code>Feature</code>.</p>

    <p>The <em>values</em> of a <code>Feature</code> for a given instance of its domain are all the instances of its co-domain that are related to that domain instance by the <code>Feature</code>. The values of a <code>Feature</code> with <code>chainingFeatures</code> are the same as values of the last <code>Feature</code> in the chain, which can be found by starting with values of the first <code>Feature</code>, then using those values as domain instances to obtain valus of the second <code>Feature</code>, and so on, to values of the last <code>Feature</code>.</p>

    ownedRedefinition = ownedSubsetting->selectByKind(Redefinition)
    ownedTypeFeaturing = ownedRelationship->selectByKind(TypeFeaturing)->
        select(tf | tf.featureOfType = self)
    ownedSubsetting = ownedSpecialization->selectByKind(Subsetting)
    ownedTyping = ownedGeneralization->selectByKind(FeatureTyping)
    type =
        let types : OrderedSet(Type) = typing.type->
            union(subsetting.subsettedFeature.type)->
            asOrderedSet() in
        if chainingFeature->isEmpty() then types
        else
            types->union(chainingFeature->last().type)->
            asOrderedSet()
        endif
    multiplicity <> null implies multiplicity.featuringType = featuringType
    specializesFromLibrary("Base::things")
    chainingFeatures->excludes(self)
    ownedFeatureChaining = ownedRelationship->selectByKind(FeatureChaining)
    chainingFeature = ownedFeatureChaining.chainingFeature
    chainingFeatures->size() <> 1
    isEnd and owningType <> null implies
        let i : Integer =
            owningType.ownedFeature->select(isEnd) in
        owningType.ownedSpecialization.general->
            forAll(supertype |
                let ownedEndFeatures : Sequence(Feature) =
                    supertype.ownedFeature->select(isEnd) in
                ownedEndFeatures->size() >= i implies
                    redefines(ownedEndFeatures->at(i))
    ownedMembership->
        selectByKind(FeatureValue)->
        forAll(fv | specializes(fv.value.result))
    isEnd and owningType <> null and
    owningType.oclIsKindOf(Association) implies
        specializesFromLibrary("Links::Link::participants")
    isComposite and
    ownedTyping.type->includes(oclIsKindOf(Structure)) and
    owningType <> null and
    (owningType.oclIsKindOf(Structure) or
     owningType.type->includes(oclIsKindOf(Structure))) implies
        specializesFromLibrary("Occurrence::Occurrence::suboccurrences")
    owningType <> null and
    (owningType.oclIsKindOf(LiteralExpression) or
     owningType.oclIsKindOf(FeatureReferenceExpression)) implies
        if owningType.oclIsKindOf(LiteralString) then
            specializesFromLibrary("ScalarValues::String")
        else if owningType.oclIsKindOf(LiteralBoolean) then
            specializesFromLibrary("ScalarValues::Boolean")
        else if owningType.oclIsKindOf(LiteralInteger) then
            specializesFromLibrary("ScalarValues::Rational")
        else if owningType.oclIsKindOf(LiteralBoolean) then
            specializesFromLibrary("ScalarValues::Rational")
        else if owningType.oclIsKindOf(LiteralBoolean) then
            specializesFromLibrary("ScalarValues::Real")
        else specializes(
            owningType.oclAsType(FeatureReferenceExpression).referent)
        endif endif endif endif endif

    ownedTyping.type->exists(selectByKind(Class)) implies
        specializesFromLibrary("Occurrences::occurrences")
    isComposite and
    ownedTyping.type->includes(oclIsKindOf(Class)) and
    owningType <> null and
    (owningType.oclIsKindOf(Class) or
     owningType.oclIsKindOf(Feature) and
        owningType.oclAsType(Feature).type->
            exists(oclIsKindOf(Class))) implies
        specializesFromLibrary("Occurrence::Occurrence::suboccurrences")
    ownedTyping.type->exists(selectByKind(DataType)) implies
        specializesFromLibary("Base::dataValues")
    owningType <> null and
    owningType.oclIsKindOf(ItemFlowEnd) and
    owningType.ownedFeature->at(1) = self implies
        let flowType : Type = owningType.owningType in
        flowType <> null implies
            let i : Integer =
                flowType.ownedFeature.indexOf(owningType) in
            (i = 1 implies
                redefinesFromLibrary("Transfers::Transfer::source::sourceOutput")) and
            (i = 2 implies
                redefinesFromLibrary("Transfers::Transfer::source::targetInput"))

    owningType <> null and
    (owningType.oclIsKindOf(Behavior) or
     owningType.oclIsKindOf(Step)) implies
        let i : Integer =
            owningType.ownedFeature->select(direction <> null) in
        owningType.ownedSpecialization.general->
            forAll(supertype |
                let ownedParameters : Sequence(Feature) =
                    supertype.ownedFeature->select(direction <> null) in
                ownedParameters->size() >= i implies
                    redefines(ownedParameters->at(i))
    ownedTyping.type->exists(selectByKind(Structure)) implies
        specializesFromLibary("Objects::objects")
    owningType <> null and
    (owningType.oclIsKindOf(Function) and
        self = owningType.oclAsType(Function).result or
     owningType.oclIsKindOf(Expression) and
        self = owningType.oclAsType(Expression).result) implies
        owningType.ownedSpecialization.general->
            select(oclIsKindOf(Function) or oclIsKindOf(Expression))->
            forAll(supertype |
                redefines(
                    if superType.oclIsKindOf(Function) then
                        superType.oclAsType(Function).result
                    else
                        superType.oclAsType(Expression).result
                    endif)
    ownedFeatureInverting = ownedRelationship->selectByKind(FeatureInverting)->
        select(fi | fi.featureInverted = self)
    featuringType =
        let featuringTypes : OrderedSet(Type) =
            typeFeaturing.featuringType->asOrderedSet() in
        if chainingFeature->isEmpty() then featuringTypes
        else
            featuringTypes->
                union(chainingFeature->first().featuringType)->
                asOrderedSet()
        endif
    ownedReferenceSubsetting =
        let referenceSubsettings : OrderedSet(ReferenceSubsetting) =
            ownedSubsetting->selectByKind(ReferenceSubsetting) in
        if referenceSubsettings->isEmpty() then null
        else referenceSubsettings->first() endif
    ownedSubsetting->selectByKind(ReferenceSubsetting)->size() <= 1"""

    isUnique = EAttribute(
        eType=Boolean, unique=True, derived=False, changeable=True, default_value="true"
    )
    isOrdered = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    isComposite = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    isEnd = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    isDerived = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    isReadOnly = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    isPortion = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    direction = EAttribute(
        eType=FeatureDirectionKind, unique=True, derived=False, changeable=True
    )
    _isNonunique = EAttribute(
        eType=Boolean,
        unique=True,
        derived=True,
        changeable=True,
        name="isNonunique",
        default_value="false",
        transient=True,
    )
    _owningType = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningType",
        transient=True,
    )
    type = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedType,
    )
    ownedRedefinition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedredefinition,
    )
    ownedSubsetting = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedsubsetting,
    )
    _owningFeatureMembership = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningFeatureMembership",
        transient=True,
    )
    _endOwningType = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="endOwningType",
        transient=True,
    )
    ownedTyping = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedtyping,
    )
    featuringType = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedFeaturingtype,
    )
    ownedTypeFeaturing = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedtypefeaturing,
    )
    chainingFeature = EReference(
        ordered=True,
        unique=False,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedChainingfeature,
    )
    ownedFeatureInverting = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedfeatureinverting,
    )
    ownedFeatureChaining = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedfeaturechaining,
    )
    _ownedReferenceSubsetting = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedReferenceSubsetting",
        transient=True,
    )

    @property
    def owningType(self):
        raise NotImplementedError("Missing implementation for owningType")

    @owningType.setter
    def owningType(self, value):
        raise NotImplementedError("Missing implementation for owningType")

    @property
    def owningFeatureMembership(self):
        raise NotImplementedError("Missing implementation for owningFeatureMembership")

    @owningFeatureMembership.setter
    def owningFeatureMembership(self, value):
        raise NotImplementedError("Missing implementation for owningFeatureMembership")

    @property
    def endOwningType(self):
        raise NotImplementedError("Missing implementation for endOwningType")

    @endOwningType.setter
    def endOwningType(self, value):
        raise NotImplementedError("Missing implementation for endOwningType")

    @property
    def ownedReferenceSubsetting(self):
        raise NotImplementedError("Missing implementation for ownedReferenceSubsetting")

    @ownedReferenceSubsetting.setter
    def ownedReferenceSubsetting(self, value):
        raise NotImplementedError("Missing implementation for ownedReferenceSubsetting")

    @property
    def isNonunique(self):
        raise NotImplementedError("Missing implementation for isNonunique")

    @isNonunique.setter
    def isNonunique(self, value):
        raise NotImplementedError("Missing implementation for isNonunique")

    def __init__(
        self,
        *,
        owningType=None,
        isUnique=None,
        isOrdered=None,
        type=None,
        ownedRedefinition=None,
        ownedSubsetting=None,
        owningFeatureMembership=None,
        isComposite=None,
        isEnd=None,
        endOwningType=None,
        ownedTyping=None,
        featuringType=None,
        ownedTypeFeaturing=None,
        isDerived=None,
        chainingFeature=None,
        ownedFeatureInverting=None,
        ownedFeatureChaining=None,
        isReadOnly=None,
        isPortion=None,
        direction=None,
        ownedReferenceSubsetting=None,
        isNonunique=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if isUnique is not None:
            self.isUnique = isUnique

        if isOrdered is not None:
            self.isOrdered = isOrdered

        if isComposite is not None:
            self.isComposite = isComposite

        if isEnd is not None:
            self.isEnd = isEnd

        if isDerived is not None:
            self.isDerived = isDerived

        if isReadOnly is not None:
            self.isReadOnly = isReadOnly

        if isPortion is not None:
            self.isPortion = isPortion

        if direction is not None:
            self.direction = direction

        if isNonunique is not None:
            self.isNonunique = isNonunique

        if owningType is not None:
            self.owningType = owningType

        if type:
            self.type.extend(type)

        if ownedRedefinition:
            self.ownedRedefinition.extend(ownedRedefinition)

        if ownedSubsetting:
            self.ownedSubsetting.extend(ownedSubsetting)

        if owningFeatureMembership is not None:
            self.owningFeatureMembership = owningFeatureMembership

        if endOwningType is not None:
            self.endOwningType = endOwningType

        if ownedTyping:
            self.ownedTyping.extend(ownedTyping)

        if featuringType:
            self.featuringType.extend(featuringType)

        if ownedTypeFeaturing:
            self.ownedTypeFeaturing.extend(ownedTypeFeaturing)

        if chainingFeature:
            self.chainingFeature.extend(chainingFeature)

        if ownedFeatureInverting:
            self.ownedFeatureInverting.extend(ownedFeatureInverting)

        if ownedFeatureChaining:
            self.ownedFeatureChaining.extend(ownedFeatureChaining)

        if ownedReferenceSubsetting is not None:
            self.ownedReferenceSubsetting = ownedReferenceSubsetting

    def directionFor(self, type=None):
        """<p>Return the <code>directionOf</code> this <code>Feature</code> relative to the given <code>type</code>.</p>"""
        raise NotImplementedError("operation directionFor(...) not yet implemented")

    def isFeaturedWithin(self, type=None):
        """<p>Return whether this Feature has the given <code>type</code> as a direct or indirect <code>featuringType</code>. If <code>type</code> is null, then check if this Feature is implicitly directly or indirectly featured in <em>Base::Anything</em>.</p>"""
        raise NotImplementedError("operation isFeaturedWithin(...) not yet implemented")

    def namingFeature(self):
        """<p>By default, the naming <code>Feature</code> of a <code>Feature</code> is given by its first <code>redefinedFeature</code> of its first <code>ownedRedefinition</code>, if any.</p>"""
        raise NotImplementedError("operation namingFeature(...) not yet implemented")

    def redefines(self, redefinedFeature=None):
        """<p>Check whether this <code>Feature</code> <em>directly</em> redefines the given <code>redefinedFeature</code>.</p>"""
        raise NotImplementedError("operation redefines(...) not yet implemented")

    def redefinesFromLibrary(self, libraryFeatureName=None):
        """<p>Check whether this <code>Feature</code> <em>directly</em> redefines the named library <code>Feature</code>. <code>libraryFeatureName</code> must conform to the syntax of a KerML qualified name and must resolve to a <code>Feature</code> in global scope.</p>"""
        raise NotImplementedError(
            "operation redefinesFromLibrary(...) not yet implemented"
        )

    def subsetsChain(self, first=None, second=None):
        """<p>Check whether this <code>Feature</code> directly or indirectly specializes a <code>Feature</code> whose last two <code>chainingFeatures</code> are the given <code>Features</code> <code>first</code> and <code>second</code>.</p>"""
        raise NotImplementedError("operation subsetsChain(...) not yet implemented")


class Subsetting(Specialization):
    """<p><code>Subsetting</code> is <code>Specialization</code> in which the <code>specific</code> and <code>general</code> <code>Types</code> are <code>Features</code>. This means all values of the <code>subsettingFeature</code> (on instances of its domain, i.e., the intersection of its <code>featuringTypes</code>) are values of the <code>subsettedFeature</code> on instances of its domain. To support this the domain of the <code>subsettingFeature</code> must be the same or specialize (at least indirectly) the domain of the <code>subsettedFeature</code> (via <code>Specialization</code>), and the co-domain (intersection of the <code>types</code>) of the <code>subsettingFeature</code> must specialize the co-domain of the <code>subsettedFeature</code>.</p>

    let subsettingFeaturingTypes: OrderedSet(Type) =
        subsettingFeature.featuringTypes in
    let subsettedFeaturingTypes: OrderedSet(Type) =
        subsettedFeature.featuringTypes in
    let anythingType: Element =
        subsettingFeature.resolveGlobal('Base::Anything') in
    subsettedFeaturingTypes->forAll(t |
        subsettingFeaturingTypes->isEmpty() and t = anythingType or
        subsettingFeaturingTypes->exists(specializes(t))"""

    subsettedFeature = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    subsettingFeature = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _owningFeature = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningFeature",
        transient=True,
    )

    @property
    def owningFeature(self):
        raise NotImplementedError("Missing implementation for owningFeature")

    @owningFeature.setter
    def owningFeature(self, value):
        raise NotImplementedError("Missing implementation for owningFeature")

    def __init__(
        self,
        *,
        subsettedFeature=None,
        subsettingFeature=None,
        owningFeature=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if subsettedFeature is not None:
            self.subsettedFeature = subsettedFeature

        if subsettingFeature is not None:
            self.subsettingFeature = subsettingFeature

        if owningFeature is not None:
            self.owningFeature = owningFeature


class FeatureTyping(Specialization):
    """<p><code>FeatureTyping</code> is <code>Specialization</code> in which the <code>specific</code> <code>Type</code> is a <code>Feature</code>. This means the set of instances of the (specific) <code>typedFeature</code> is a subset of the set of instances of the (general) <code>type</code>. In the simplest case, the <code>type</code> is a <code>Classifier</code>, whereupon the <code>typedFeature</code> has values that are instances of the <code>Classifier</code>.</p>"""

    typedFeature = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    type = EReference(ordered=False, unique=True, containment=False, derived=False)
    _owningFeature = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningFeature",
        transient=True,
    )

    @property
    def owningFeature(self):
        raise NotImplementedError("Missing implementation for owningFeature")

    @owningFeature.setter
    def owningFeature(self, value):
        raise NotImplementedError("Missing implementation for owningFeature")

    def __init__(self, *, typedFeature=None, type=None, owningFeature=None, **kwargs):
        super().__init__(**kwargs)

        if typedFeature is not None:
            self.typedFeature = typedFeature

        if type is not None:
            self.type = type

        if owningFeature is not None:
            self.owningFeature = owningFeature


class TypeFeaturing(Featuring):
    """<p>A <code>TypeFeaturing</code> is a <code>Featuring</code> <code>Relationship</code> in which the <code>featureOfType</code> is the <code>source</code> and the <code>featuringType</code> is the <code>target</code>.</p>"""

    featureOfType = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    featuringType = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _owningFeatureOfType = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningFeatureOfType",
        transient=True,
    )

    @property
    def owningFeatureOfType(self):
        raise NotImplementedError("Missing implementation for owningFeatureOfType")

    @owningFeatureOfType.setter
    def owningFeatureOfType(self, value):
        raise NotImplementedError("Missing implementation for owningFeatureOfType")

    def __init__(
        self,
        *,
        featureOfType=None,
        featuringType=None,
        owningFeatureOfType=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if featureOfType is not None:
            self.featureOfType = featureOfType

        if featuringType is not None:
            self.featuringType = featuringType

        if owningFeatureOfType is not None:
            self.owningFeatureOfType = owningFeatureOfType


class DerivedOwnedsubclassification(EDerivedCollection):
    pass


class Classifier(Type):
    """<p>A <code>Classifier</code> is a <code>Type</code> that classifies:</p>

    <ul>
            <li>Things (in the universe) regardless of how <code>Features</code> relate them. (These are interpreted semantically as sequences of exactly one thing.)</li>
            <li>How the above things are related by <code>Features.</code> (These are interpreted semantically as sequences of multiple things, such that the last thing in the sequence is also classified by the <code>Classifier</code>. Note that his means that a <code>Classifier</code> modeled as specializing a <code>Feature</code> cannot classify anything.)</li>
    </ul>


    ownedSubclassification =
        ownedSpecialization->selectByKind(Superclassification)
    multiplicity <> null implies multiplicity.featuringType->isEmpty()"""

    ownedSubclassification = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedOwnedsubclassification,
    )

    def __init__(self, *, ownedSubclassification=None, **kwargs):
        super().__init__(**kwargs)

        if ownedSubclassification:
            self.ownedSubclassification.extend(ownedSubclassification)


class LibraryPackage(Package):
    """<p>A <code>LibraryPackage</code> is a <code>Package</code> that is the container for a model library. A <code>LibraryPackage</code> is itself a library <code>Element</code> as are all <code>Elements</code> that are directly or indirectly contained in it.</p>"""

    isStandard = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )

    def __init__(self, *, isStandard=None, **kwargs):
        super().__init__(**kwargs)

        if isStandard is not None:
            self.isStandard = isStandard


class Redefinition(Subsetting):
    """<p><code>Redefinition</code> is a kind of <code>Subsetting</code> that requires the <code>redefinedFeature</code> and the <code>redefiningFeature</code> to have the same values (on each instance of the domain of the <code>redefiningFeature</code>). This means any restrictions on the <code>redefiningFeature</code>, such as <code>type</code> or <code>multiplicity</code>, also apply to the <code>redefinedFeature</code> (on each instance of the domain of the <code>redefiningFeature</code>), and vice versa. The <code>redefinedFeature</code> might have values for instances of the domain of the <code>redefiningFeature</code>, but only as instances of the domain of the <code>redefinedFeature</code> that happen to also be instances of the domain of the <code>redefiningFeature</code>. This is supported by the constraints inherited from <code>Subsetting</code> on the domains of the <code>redefiningFeature</code> and <code>redefinedFeature</code>. However, these constraints are narrowed for <code>Redefinition</code> to require the <code>owningTypes</code> of the <code>redefiningFeature</code> and <code>redefinedFeature</code> to be different and the <code>redefinedFeature</code> to not be inherited into the <code>owningNamespace</code> of the <code>redefiningFeature</code>.This enables the <code>redefiningFeature</code> to have the same name as the <code>redefinedFeature</code>, if desired.</p>

    let anythingType: Type =
        subsettingFeature.resolveGlobal('Base::Anything').oclAsType(Type) in
    -- Including "Anything" accounts for implicit featuringType of Features
    -- with no explicit featuringType.
    let subsettingFeaturingTypes: Set(Type) =
        subsettingFeature.featuringTypes->asSet()->including(anythingType) in
    let subsettedFeaturingTypes: Set(Type) =
        subsettedFeature.featuringTypes->asSet()->including(anythingType) in
    subsettingFeaturingTypes <> subsettedFeaturingType"""

    redefiningFeature = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    redefinedFeature = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )

    def __init__(self, *, redefiningFeature=None, redefinedFeature=None, **kwargs):
        super().__init__(**kwargs)

        if redefiningFeature is not None:
            self.redefiningFeature = redefiningFeature

        if redefinedFeature is not None:
            self.redefinedFeature = redefinedFeature


class ReferenceSubsetting(Subsetting):
    """<p><code>ReferenceSubsetting</code> is a kind of <code>Subsetting</code> in which the <code>referencedFeature</code> is syntactically distinguished from other <code>Features</code> subsetted by the <code>referencingFeature</code>. <code>ReferenceSubsetting</code> has the same semantics as <code>Subsetting</code>, but the <code>referenceFeature</code> may have a special purpose relative to the <code>referencingFeature</code>. For instance, <code>ReferenceSubsetting</code> is used to identify the <code>relatedFeatures</code> of a <code>Connector</code>.</p>

    <p><code>ReferenceSubsetting</code> is always an <code>ownedRelationship</code> of its <code>referencingFeature</code>. A <code>Feature</code> can have at most one <code>ownedReferenceSubsetting</code>.</p>
    """

    referencedFeature = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )
    _referencingFeature = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="referencingFeature",
        transient=True,
    )

    @property
    def referencingFeature(self):
        raise NotImplementedError("Missing implementation for referencingFeature")

    @referencingFeature.setter
    def referencingFeature(self, value):
        raise NotImplementedError("Missing implementation for referencingFeature")

    def __init__(self, *, referencedFeature=None, referencingFeature=None, **kwargs):
        super().__init__(**kwargs)

        if referencedFeature is not None:
            self.referencedFeature = referencedFeature

        if referencingFeature is not None:
            self.referencingFeature = referencingFeature


class Multiplicity(Feature):
    """<p>A <code>Multiplicity</code> is a <code>Feature</code> whose co-domain is a set of natural numbers giving the allowed cardinalities of each <code>typeWithMultiplicity</code>. The <em>cardinality</em> of a <code>Type</code> is defined as follows, depending on whether the <code>Type</code> is a <code>Classifier</code> or <code>Feature</code>.
    <ul>
    <li><code>Classifier</code> – The number of basic instances of the <code>Classifier</code>, that is, those instances representing things, which are not instances of any subtypes of the <code>Classifier</code> that are <code>Features</code>.
    <li><code>Features</code> – The number of instances with the same featuring instances. In the case of a <code>Feature</code> with a <code>Classifier</code> as its <code>featuringType</code>, this is the number of values of <code>Feature</code> for each basic instance of the <code>Classifier</code>. Note that, for non-unique <code>Features</code>, all duplicate values are included in this count.</li>
    </ul>

    <p><code>Multiplicity</code> co-domains (in models) can be specified by <code>Expression</code> that might vary in their results. If the <code>typeWithMultiplicity</code> is a <code>Classifier</code>, the domain of the <code>Multiplicity</code> shall be <em><code>Base::Anything</code></em>.  If the <code>typeWithMultiplicity</code> is a <code>Feature</code>,  the <code>Multiplicity</code> shall have the same domain as the <code>typeWithMultiplicity</code>.</p>

    if owningType <> null and owningType.oclIsKindOf(Feature) then
        featuringType =
            owningType.oclAsType(Feature).featuringType
    else
        featuringType->isEmpty()
    endif
    specializesFromLibrary("Base::naturals")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Class(Classifier):
    """<p>A <code>Class</code> is a <code>Classifier</code> of things (in the universe) that can be distinguished without regard to how they are related to other things (via <code>Features</code>). This means multiple things classified by the same <code>Class</code> can be distinguished, even when they are related other things in exactly the same way.</p>

    specializesFromLibrary('Occurrences::Occurrence')
    ownedSpecialization.general->
        forAll(not oclIsKindOf(DataType)) and
    not oclIsKindOf(AssociationStructure) implies
        ownedSpecialization.general->
            forAll(not oclIsKindOf(Association))"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DataType(Classifier):
    """<p>A <code>DataType</code> is a <code>Classifier</code> of things (in the universe) that can only be distinguished by how they are related to other things (via Features). This means multiple things classified by the same <code>DataType</code></p>

    <ul>
            <li>Cannot be distinguished when they are related to other things in exactly the same way, even when they are intended to be about different things.</li>
            <li>Can be distinguished when they are related to other things in different ways, even when they are intended to be about the same thing.</li>
    </ul>

    specializesFromLibrary('Base::DataValue')
    ownedSpecialization.general->
        forAll(not oclIsKindOf(Class) and
               not oclIsKindOf(Association))"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DerivedBehavior(EDerivedCollection):
    pass


class DerivedParameter(EDerivedCollection):
    pass


class Step(Feature):
    """<p>A <code>Step</code> is a <code>Feature</code> that is typed by one or more <code>Behaviors</code>. <code>Steps</code> may be used by one <code>Behavior</code> to coordinate the performance of other <code>Behaviors</code>, supporting a steady refinement of behavioral descriptions. <code>Steps</code> can be ordered in time and can be connected using <code>ItemFlows</code> to specify things flowing between their <code>parameters</code>.</p>

    allSupertypes()->includes(resolveGlobal("Performances::performances"))
    owningType <> null and
        (owningType.oclIsKindOf(Behavior) or
         owningType.oclIsKindOf(Step)) implies
        specializesFromLibrary('Performances::Performance::enclosedPerformance')
    isComposite and owningType <> null and
    (owningType.oclIsKindOf(Structure) or
     owningType.oclIsKindOf(Feature) and
     owningType.oclAsType(Feature).type->
        exists(oclIsKindOf(Structure)) implies
        specializesFromLibrary('Objects::Object::ownedPerformance')
    owningType <> null and
        (owningType.oclIsKindOf(Behavior) or
         owningType.oclIsKindOf(Step)) and
        self.isComposite implies
        specializesFromLibrary('Performances::Performance::subperformance')
    behavior = type->selectByKind(Behavior)"""

    behavior = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedBehavior,
    )
    parameter = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedParameter,
    )

    def __init__(self, *, behavior=None, parameter=None, **kwargs):
        super().__init__(**kwargs)

        if behavior:
            self.behavior.extend(behavior)

        if parameter:
            self.parameter.extend(parameter)


class ElementFilterMembership(OwningMembership):
    """<p><code>ElementFilterMembership</code> is a <code>Membership</code> between a <code>Namespace</code> and a model-level evaluable <code><em>Boolean</em></code>-valued <code>Expression</code>, asserting that imported <code>members</code> of the <code>Namespace</code> should be filtered using the <code>condition</code> <code>Expression</code>. A general <code>Namespace</code> does not define any specific filtering behavior, but such behavior may be defined for various specialized kinds of <code>Namespaces</code>.</p>

    condition.isModelLevelEvaluable
    condition.result.specializesFromLibrary('ScalarValues::Boolean')"""

    _condition = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="condition",
        transient=True,
    )

    @property
    def condition(self):
        raise NotImplementedError("Missing implementation for condition")

    @condition.setter
    def condition(self, value):
        raise NotImplementedError("Missing implementation for condition")

    def __init__(self, *, condition=None, **kwargs):
        super().__init__(**kwargs)

        if condition is not None:
            self.condition = condition


class FeatureValue(OwningMembership):
    """<p>A <code>FeatureValue</code> is a <code>Membership</code> that identifies a particular member <code>Expression</code> that provides the value of the <code>Feature</code> that owns the <code>FeatureValue</code>. The value is specified as either a bound value or an initial value, and as either a concrete or default value. A <code>Feature</code> can have at most one <code>FeatureValue</code>.</p>

    <p>The result of the <code>value</code> <code>Expression</code> is bound to the <code>featureWithValue</code> using a <code>BindingConnector</code>. If <code>isInitial = false</code>, then the <code>featuringType</code> of the <code>BindingConnector</code> is the same as the <code>featuringType</code> of the <code>featureWithValue</code>. If <code>isInitial = true</code>, then the <code>featuringType</code> of the <code>BindingConnector</code> is restricted to its <code>startShot</code>.

    <p>If <code>isDefault = false</code>, then the above semantics of the <code>FeatureValue</code> are realized for the given <code>featureWithValue</code>. Otherwise, the semantics are realized for any individual of the <code>featuringType</code> of the <code>featureWithValue</code>, unless another value is explicitly given for the <code>featureWithValue</code> for that individual.</p>

    not isDefault implies
        featureWithValue.ownedMember->
            selectByKind(BindingConnector)->exists(b |
                b.relatedFeature->includes(featureWithValue) and
                b.relatedFeature->includes(value.result) and
                if not isInitial then
                    b.featuringType = featureWithValue.featuringType
                else
                    b.featuringType->exists(t |
                        t.oclIsKindOf(Feature) and
                        t.oclAsType(Feature).chainingFeature =
                            Sequence{
                                resolveGlobal("Base::things::that"),
                                resolveGlobal("Occurrences::Occurrence::startShot")
                            }
                    )
                endif)"""

    isInitial = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    isDefault = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    _featureWithValue = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="featureWithValue",
        transient=True,
    )
    _value = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="value",
        transient=True,
    )

    @property
    def featureWithValue(self):
        raise NotImplementedError("Missing implementation for featureWithValue")

    @featureWithValue.setter
    def featureWithValue(self, value):
        raise NotImplementedError("Missing implementation for featureWithValue")

    @property
    def value(self):
        raise NotImplementedError("Missing implementation for value")

    @value.setter
    def value(self, value):
        raise NotImplementedError("Missing implementation for value")

    def __init__(
        self,
        *,
        featureWithValue=None,
        value=None,
        isInitial=None,
        isDefault=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if isInitial is not None:
            self.isInitial = isInitial

        if isDefault is not None:
            self.isDefault = isDefault

        if featureWithValue is not None:
            self.featureWithValue = featureWithValue

        if value is not None:
            self.value = value


class ItemFlowEnd(Feature):
    """<p>An <code>ItemFlowEnd</code> is a <code>Feature</code> that is one of the <code>connectorEnds</code> giving the <code><em>source</em></code> or <code><em>target</em></code> of an <code>ItemFlow</code>. For <code>ItemFlows</code> typed by <code><em>FlowTransfer</em></code> or its specializations, <code>ItemFlowEnds</code> must have exactly one <code>ownedFeature</code>, which redefines <code><em>Transfer::source::sourceOutput</em></code> or <code><em>Transfer::target::targetInput</em></code> and redefines the corresponding feature of the <code>relatedElement</code> for its end.</p>
    isEnd
    ownedFeature->size() = 1
    owningType <> null and owningType.oclIsKindOf(ItemFlow)"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ItemFeature(Feature):
    """<p>An <code>ItemFeature</code> is the <code>ownedFeature</code> of an <code>ItemFlow</code> that identifies the things carried by the kinds of transfers that are instances of the <code>ItemFlow</code>.</p>
    ownedRedefinition.redefinedFeature->
        redefinesFromLibrary("Transfers::Transfer::item")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FeatureMembership(OwningMembership, Featuring):
    """<p>A <code>FeatureMembership</code> is an <code>OwningMembership</code> between a <code>Feature</code> in an <code>owningType</code> that is also a <code>Featuring</code> <code>Relationship<code? between the <code>Feature</code> and the <code>Type</code>, in which the <code>featuringType</code> is the <code>source</code> and the <code>featureOfType</code> is the <code>target</code>. A <code>FeatureMembership</code> is always owned by its <code>owningType</code>, which is the <code>featuringType</code> for the <code>FeatureMembership</code> considered as a <code>Featuring</code>.</p>"""

    _ownedMemberFeature = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedMemberFeature",
        transient=True,
    )
    _owningType = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="owningType",
        transient=True,
    )

    @property
    def ownedMemberFeature(self):
        raise NotImplementedError("Missing implementation for ownedMemberFeature")

    @ownedMemberFeature.setter
    def ownedMemberFeature(self, value):
        raise NotImplementedError("Missing implementation for ownedMemberFeature")

    @property
    def owningType(self):
        raise NotImplementedError("Missing implementation for owningType")

    @owningType.setter
    def owningType(self, value):
        raise NotImplementedError("Missing implementation for owningType")

    def __init__(self, *, ownedMemberFeature=None, owningType=None, **kwargs):
        super().__init__(**kwargs)

        if ownedMemberFeature is not None:
            self.ownedMemberFeature = ownedMemberFeature

        if owningType is not None:
            self.owningType = owningType


class Structure(Class):
    """<p>A <code>Structure</code> is a <code>Class</code> of objects in the modeled universe that are primarily structural in nature. While such an object is not itself behavioral, it may be involved in and acted on by <code>Behaviors</code>, and it may be the performer of some of them.</p>

    specializesFromLibrary('Objects::Object')"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Expression(Step):
    """<p>An <code>Expression</code> is a <code>Step</code> that is typed by a <code>Function</code>. An <code>Expression</code> that also has a <code>Function</code> as its <code>featuringType</code> is a computational step within that <code>Function</code>. An <code>Expression</code> always has a single <code>result</code> parameter, which redefines the <code>result</code> parameter of its defining <code>function</code>. This allows <code>Expressions</code> to be interconnected in tree structures, in which inputs to each <code>Expression</code> in the tree are determined as the results of other <code>Expression</code> in the tree.</p>

    isModelLevelEvaluable = modelLevelEvaluable(Set(Element){})
    specializesFromLibrary("Performances::evaluations")
    owningMembership <> null and
    owningMembership.oclIsKindOf(FeatureValue) implies
        let featureWithValue : Feature =
            owningMembership.oclAsType(FeatureValue).featureWithValue in
        featuringType = featureWithValue.featuringType
    ownedMembership.selectByKind(ResultExpressionMembership)->
        forAll(mem | ownedFeature.selectByKind(BindingConnector)->
            exists(binding |
                binding.relatedFeature->includes(result) and
                binding.relatedFeature->includes(mem.ownedResultExpression.result)))
    result =
        let resultParams : Sequence(Feature) =
            ownedFeatureMemberships->
                selectByKind(ReturnParameterMembership).
                ownedParameterMember in
        if resultParams->notEmpty() then resultParams->first()
        else if function <> null then function.result
        else null
        endif endif
    ownedFeatureMembership->
        selectByKind(ReturnParameterMembership)->
        size() <= 1"""

    _isModelLevelEvaluable = EAttribute(
        eType=Boolean,
        unique=True,
        derived=True,
        changeable=True,
        name="isModelLevelEvaluable",
        transient=True,
    )
    _function = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="function",
        transient=True,
    )
    _result = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="result",
        transient=True,
    )

    @property
    def function(self):
        raise NotImplementedError("Missing implementation for function")

    @function.setter
    def function(self, value):
        raise NotImplementedError("Missing implementation for function")

    @property
    def result(self):
        raise NotImplementedError("Missing implementation for result")

    @result.setter
    def result(self, value):
        raise NotImplementedError("Missing implementation for result")

    @property
    def isModelLevelEvaluable(self):
        raise NotImplementedError("Missing implementation for isModelLevelEvaluable")

    @isModelLevelEvaluable.setter
    def isModelLevelEvaluable(self, value):
        raise NotImplementedError("Missing implementation for isModelLevelEvaluable")

    def __init__(
        self, *, function=None, result=None, isModelLevelEvaluable=None, **kwargs
    ):
        super().__init__(**kwargs)

        if isModelLevelEvaluable is not None:
            self.isModelLevelEvaluable = isModelLevelEvaluable

        if function is not None:
            self.function = function

        if result is not None:
            self.result = result

    def modelLevelEvaluable(self, visited=None):
        """<p>Return whether this <code>Expression</code> is model-level evaluable. The <code>visited</code> parameter is used to track possible circular <code>Feature</code> references. Such circular references are not allowed in model-level evaluable expressions.</p>

        <p>An <code>Expression</code> that is not otherwise specialized is model-level evaluable if all of it has no <code>ownedSpecialziations</code> and all its (non-implicit) <code>features</code> are either <code>in</code> parameters, the <code>result</code> <code>parameter</code> or a result <code>Expression</code> owned via a <code>ResultExpressionMembership</code>. The <code>parameters</code>  must not have any <code>ownedFeatures</code> or a <code>FeatureValue</code>, and the result <code>Expression</code> must be model-level evaluable.</p>
        """
        raise NotImplementedError(
            "operation modelLevelEvaluable(...) not yet implemented"
        )

    def evaluate(self, target=None):
        """<p>If this <code>Expression</code> <code>isModelLevelEvaluable</code>, then evaluate it using the <code>target</code> as the context <code>Element</code> for resolving <code>Feature</code> names and testing classification. The result is a collection of <code>Elements</code>, which, for a fully evaluable <code>Expression</code>, will be a <code>LiteralExpression</code> or a <code>Feature</code> that is not an <code>Expression</code>.</p>"""
        raise NotImplementedError("operation evaluate(...) not yet implemented")

    def checkCondition(self, target=None):
        """<p>Model-level evaluate this <code>Expression</code> with the given <code>target</code>. If the result is a <code>LiteralBoolean</code>, return its <code>value</code>. Otherwise return <code>false</code>.</p>"""
        raise NotImplementedError("operation checkCondition(...) not yet implemented")


class DerivedStep(EDerivedCollection):
    pass


class Behavior(Class):
    """<p>A <code>Behavior </code>coordinates occurrences of other <code>Behaviors</code>, as well as changes in objects. <code>Behaviors</code> can be decomposed into <code>Steps</code> and be characterized by <code>parameters</code>.</p>

    specializesFromLibrary("Performances::Performance")
    step = feature->selectByKind(Step)"""

    step = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedStep,
    )
    parameter = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedParameter,
    )

    def __init__(self, *, step=None, parameter=None, **kwargs):
        super().__init__(**kwargs)

        if step:
            self.step.extend(step)

        if parameter:
            self.parameter.extend(parameter)


class MetadataFeature(Feature, AnnotatingElement):
    """<p>A <code>MetadataFeature</code> is a <code>Feature</code> that is an <code>AnnotatingElement</code> used to annotate another <code>Element</code> with metadata. It is typed by a <code>Metaclass</code>. All its <code>ownedFeatures</code> must redefine <code>features</code> of its <code>metaclass</code> and any feature bindings must be model-level evaluable.</p>


    specializesFromLibrary("Metaobjects::metaobjects")
    isSemantic() implies
        let annotatedTypes : Sequence(Type) =
            annotatedElement->selectAsKind(Type) in
        let baseTypes : Sequence(MetadataFeature) =
            evaluateFeature(resolveGlobal(
                'Metaobjects::SemanticMetadata::baseType').
                oclAsType(Feature))->
            selectAsKind(MetadataFeature) in
        annotatedTypes->notEmpty() and
        baseTypes()->notEmpty() and
        baseTypes()->first().isSyntactic() implies
            let annotatedType : Type = annotatedTypes->first() in
            let baseType : Element = baseTypes->first().syntaxElement() in
            if annotatedType.oclIsKindOf(Classifier) and
                baseType.oclIsKindOf(Feature) then
                baseType.oclAsType(Feature).type->
                    forAll(t | annotatedType.specializes(t))
            else if baseType.oclIsKindOf(Type) then
                annotatedType.specializes(baseType.oclAsType(Type))
            else
                true
            endif"""

    _metaclass = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="metaclass",
        transient=True,
    )

    @property
    def metaclass(self):
        raise NotImplementedError("Missing implementation for metaclass")

    @metaclass.setter
    def metaclass(self, value):
        raise NotImplementedError("Missing implementation for metaclass")

    def __init__(self, *, metaclass=None, **kwargs):
        super().__init__(**kwargs)

        if metaclass is not None:
            self.metaclass = metaclass

    def evaluateFeature(self, baseFeature=None):
        """<p>If the given <code>baseFeature</code> is a <code>feature</code> of this <code>MetadataFeature</code>, or is directly or indirectly redefined by a <code>feature</code>, then return the result of evaluating the appropriate (model-level evaluable) <code>value</code> <code>Expression</code> for it (if any), with the MetadataFeature as the target.</p>"""
        raise NotImplementedError("operation evaluateFeature(...) not yet implemented")

    def isSemantic(self):
        """<p>Check if this <code>MetadataFeature</code> has a <code>metaclass</code> which is a kind of <code><em>SemanticMetadata</code>.<p>"""
        raise NotImplementedError("operation isSemantic(...) not yet implemented")

    def isSyntactic(self):
        """<p>Check if this <code>MetadataFeature</code> has a <code>metaclass</code> that is a kind of <code><em>KerML::Element<em></code> (that is, it is from the reflective abstract syntax model).</p>"""
        raise NotImplementedError("operation isSyntactic(...) not yet implemented")

    def syntaxElement(self):
        """<p>If this <code>MetadataFeature</code> reflectively represents a model element, then return the corresponding <code>Element<code> instance from the MOF abstract syntax representation of the model.</p>"""
        raise NotImplementedError("operation syntaxElement(...) not yet implemented")


class DerivedRelatedtype(EDerivedCollection):
    pass


class DerivedTargettype(EDerivedCollection):
    pass


class DerivedAssociationend(EDerivedCollection):
    pass


class Association(Classifier, Relationship):
    """<p>An <code>Association</code> is a <code>Relationship</code> and a <code>Classifier</code> to enable classification of links between things (in the universe). The co-domains (<code>types</code>) of the <code>associationEnd</code> <code>Features</code> are the <code>relatedTypes</code>, as co-domain and participants (linked things) of an <code>Association</code> identify each other.</p>

    relatedType = associationEnd.type
    specializesFromLibrary("Links::Link")
    oclIsKindOf(Structure) = oclIsKindOf(AssociationStructure)
    ownedEndFeature->size() = 2 implies
        specializesFromLibrary("Links::BinaryLink)
    not isAbstract implies relatedType->size() >= 2
    associationEnds->size() > 2 implies
        not specializesFromLibrary("Links::BinaryLink")
    sourceType =
        if relatedType->isEmpty() then null
        else relatedType->first() endif
    targetType =
        if relatedType->size() < 2 then OrderedSet{}
        else
            relatedType->
                subSequence(2, relatedType->size())->
                asOrderedSet()
        endif"""

    relatedType = EReference(
        ordered=True,
        unique=False,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedRelatedtype,
    )
    _sourceType = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="sourceType",
        transient=True,
    )
    targetType = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedTargettype,
    )
    associationEnd = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedAssociationend,
    )

    @property
    def sourceType(self):
        raise NotImplementedError("Missing implementation for sourceType")

    @sourceType.setter
    def sourceType(self, value):
        raise NotImplementedError("Missing implementation for sourceType")

    def __init__(
        self,
        *,
        relatedType=None,
        sourceType=None,
        targetType=None,
        associationEnd=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if relatedType:
            self.relatedType.extend(relatedType)

        if sourceType is not None:
            self.sourceType = sourceType

        if targetType:
            self.targetType.extend(targetType)

        if associationEnd:
            self.associationEnd.extend(associationEnd)


class DerivedRelatedfeature(EDerivedCollection):
    pass


class DerivedAssociation(EDerivedCollection):
    pass


class DerivedConnectorend(EDerivedCollection):
    pass


class DerivedTargetfeature(EDerivedCollection):
    pass


class Connector(Feature, Relationship):
    """<p>A <code>Connector</code> is a usage of <code>Associations</code>, with links restricted according to instances of the <code>Type</code> in which they are used (domain of the <code>Connector</code>). The <code>associations</code> of the <code>Connector</code> restrict what kinds of things might be linked. The <code>Connector</code> further restricts these links to be between values of <code>Features</code> on instances of its domain.</p>

    relatedFeature = connectorEnd.ownedReferenceSubsetting->
        select(s | s <> null).subsettedFeature
    relatedFeature->forAll(f |
        if featuringType->isEmpty() then f.isFeaturedWithin(null)
        else featuringType->exists(t | f.isFeaturedWithin(t))
        endif)
    sourceFeature =
        if relatedFeature->isEmpty() then null
        else relatedFeature->first()
        endif
    targetFeature =
        if relatedFeature->size() < 2 then OrderedSet{}
        else
            relatedFeature->
                subSequence(2, relatedFeature->size())->
                asOrderedSet()
        endif
    not isAbstract implies relatedFeature->size() >= 2
    specializesFromLibrary("Links::links")
    association->exists(oclIsKindOf(AssociationStructure)) implies
        specializesFromLibrary("Objects::linkObjects")
    connectorEnds->size() = 2 and
    association->exists(oclIsKindOf(AssocationStructure)) implies
        specializesFromLibrary("Objects::binaryLinkObjects")
    connectorEnd->size() = 2 implies
        specializesFromLibrary("Links::binaryLinks")
    connectorEnds->size() > 2 implies
        not specializesFromLibrary("Links::BinaryLink")"""

    isDirected = EAttribute(
        eType=Boolean,
        unique=True,
        derived=False,
        changeable=True,
        default_value="false",
    )
    relatedFeature = EReference(
        ordered=True,
        unique=False,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedRelatedfeature,
    )
    association = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedAssociation,
    )
    connectorEnd = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedConnectorend,
    )
    _sourceFeature = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        name="sourceFeature",
        transient=True,
    )
    targetFeature = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedTargetfeature,
    )

    @property
    def sourceFeature(self):
        raise NotImplementedError("Missing implementation for sourceFeature")

    @sourceFeature.setter
    def sourceFeature(self, value):
        raise NotImplementedError("Missing implementation for sourceFeature")

    def __init__(
        self,
        *,
        relatedFeature=None,
        association=None,
        isDirected=None,
        connectorEnd=None,
        sourceFeature=None,
        targetFeature=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if isDirected is not None:
            self.isDirected = isDirected

        if relatedFeature:
            self.relatedFeature.extend(relatedFeature)

        if association:
            self.association.extend(association)

        if connectorEnd:
            self.connectorEnd.extend(connectorEnd)

        if sourceFeature is not None:
            self.sourceFeature = sourceFeature

        if targetFeature:
            self.targetFeature.extend(targetFeature)


class DerivedBound(EDerivedCollection):
    pass


class MultiplicityRange(Multiplicity):
    """<p>A <code>MultiplicityRange</code> is a <code>Multiplicity</code> whose value is defined to be the (inclusive) range of natural numbers given by the result of a <code>lowerBound</code> <code>Expression</code> and the result of an <code>upperBound</code> <code>Expression</code>. The result of these <code>Expressions</code> shall be of type <code><em>Natural</em></code>. If the result of the <code>upperBound</code> <code>Expression</code> is the unbounded value <code>*</code>, then the specified range includes all natural numbers greater than or equal to the <code>lowerBound</code> value. If no <code>lowerBound</code> <code>Expression</code>, then the default is that the lower bound has the same value as the upper bound, except if the <code>upperBound</code> evaluates to <code>*</code>, in which case the default for the lower bound is 0.</p>

    bound->forAll(b | b.featuringType = self.featuringType)
    bound.result->forAll(specializesFromLibrary('ScalarValues::Natural'))
    lowerBound =
        let ownedMembers : Sequence(Element) =
            ownedMembership->selectByKind(OwningMembership).ownedMember in
        if ownedMembers->size() < 2 or
            not ownedMembers->first().oclIsKindOf(Expression) then null
        else ownedMembers->first().oclAsType(Expression)
        endif
    upperBound =
        let ownedMembers : Sequence(Element) =
            ownedMembership->selectByKind(OwningMembership).ownedMember in
        if ownedMembers->isEmpty() or
           not ownedMembers->last().oclIsKindOf(Expression)
        then null
        else ownedMembers->last().oclAsType(Expression)
        endif"""

    _lowerBound = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="lowerBound",
        transient=True,
    )
    _upperBound = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="upperBound",
        transient=True,
    )
    bound = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedBound,
    )

    @property
    def lowerBound(self):
        raise NotImplementedError("Missing implementation for lowerBound")

    @lowerBound.setter
    def lowerBound(self, value):
        raise NotImplementedError("Missing implementation for lowerBound")

    @property
    def upperBound(self):
        raise NotImplementedError("Missing implementation for upperBound")

    @upperBound.setter
    def upperBound(self, value):
        raise NotImplementedError("Missing implementation for upperBound")

    def __init__(self, *, lowerBound=None, upperBound=None, bound=None, **kwargs):
        super().__init__(**kwargs)

        if lowerBound is not None:
            self.lowerBound = lowerBound

        if upperBound is not None:
            self.upperBound = upperBound

        if bound:
            self.bound.extend(bound)

    def hasBounds(self, lower=None, upper=None):
        """<p>Check whether this <code>MultiplicityRange</code> represents the range bounded by the given values <code>lower</code> and <code>upper</code>, presuming the <code>lowerBound</code> and <code>upperBound</code> <code>Expressions</code> are model-level evaluable.</p>"""
        raise NotImplementedError("operation hasBounds(...) not yet implemented")

    def valueOf(self, bound=None):
        """<p>Evaluate the given <code>bound</code> <code>Expression</code> (at model level) and return the result represented as a MOF <code>UnlimitedNatural</code> value.</p>"""
        raise NotImplementedError("operation valueOf(...) not yet implemented")


class EndFeatureMembership(FeatureMembership):
    """<p><code>EndFeatureMembership</code> is a <code>FeatureMembership</code> that requires its <code>memberFeature</code> be owned and have <code>isEnd = true</code>.</p>

    ownedMemberFeature.isEnd"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DerivedExpression(EDerivedCollection):
    pass


class Function(Behavior):
    """<p>A <code>Function</code> is a <code>Behavior</code> that has an <code>out</code> <code>parameter</code> that is identified as its <code>result</code>. A <code>Function</code> represents the performance of a calculation that produces the values of its <code>result</code> <code>parameter</code>. This calculation may be decomposed into <code>Expressions</code? that are <code>steps</code> of the <code>Function</code>.</p>

    ownedMembership.selectByKind(ResultExpressionMembership)->
        forAll(mem | ownedFeature.selectByKind(BindingConnector)->
            exists(binding |
                binding.relatedFeature->includes(result) and
                binding.relatedFeature->includes(mem.ownedResultExpression.result)))
    specializesFromLibrary("Performances::Evaluation")
    result =
        let resultParams : Sequence(Feature) =
            ownedFeatureMemberships->
                selectByKind(ReturnParameterMembership).
                ownedParameterMember in
        if resultParams->notEmpty() then resultParams->first()
        else null
        endif
    ownedFeatureMembership->
        selectByKind(ReturnParameterMembership)->
        size() <= 1"""

    _isModelLevelEvaluable = EAttribute(
        eType=Boolean,
        unique=True,
        derived=True,
        changeable=True,
        name="isModelLevelEvaluable",
        transient=True,
    )
    expression = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedExpression,
    )
    _result = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="result",
        transient=True,
    )

    @property
    def result(self):
        raise NotImplementedError("Missing implementation for result")

    @result.setter
    def result(self, value):
        raise NotImplementedError("Missing implementation for result")

    @property
    def isModelLevelEvaluable(self):
        raise NotImplementedError("Missing implementation for isModelLevelEvaluable")

    @isModelLevelEvaluable.setter
    def isModelLevelEvaluable(self, value):
        raise NotImplementedError("Missing implementation for isModelLevelEvaluable")

    def __init__(
        self, *, expression=None, result=None, isModelLevelEvaluable=None, **kwargs
    ):
        super().__init__(**kwargs)

        if isModelLevelEvaluable is not None:
            self.isModelLevelEvaluable = isModelLevelEvaluable

        if expression:
            self.expression.extend(expression)

        if result is not None:
            self.result = result


class LiteralExpression(Expression):
    """<p>A <code>LiteralExpression</code> is an <code>Expression</code> that provides a basic <code><em>DataValue</em></code> as a result.</p>

    isModelLevelEvaluable = true
    specializesFromLibrary("Performances::literalEvaluations")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FeatureReferenceExpression(Expression):
    """<p>A <code>FeatureReferenceExpression</code> is an <code>Expression</code> whose <code>result</code> is bound to a <code>referent</code> <code>Feature</code>.</p>
    referent =
        let nonParameterMemberships : Sequence(Membership) = ownedMembership->
            reject(oclIsKindOf(ParameterMembership)) in
        if nonParameterMemberships->isEmpty() or
           not nonParameterMemberships->first().memberElement.oclIsKindOf(Feature)
        then null
        else nonParameterMemberships->first().memberElement.oclAsType(Feature)
        endif
    ownedMember->selectByKind(BindingConnector)->exists(b |
        b.relatedFeatures->includes(targetFeature) and
        b.relatedFeatures->includes(result))"""

    _referent = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="referent",
        transient=True,
    )

    @property
    def referent(self):
        raise NotImplementedError("Missing implementation for referent")

    @referent.setter
    def referent(self, value):
        raise NotImplementedError("Missing implementation for referent")

    def __init__(self, *, referent=None, **kwargs):
        super().__init__(**kwargs)

        if referent is not None:
            self.referent = referent


class DerivedArgument(EDerivedCollection):
    pass


class InvocationExpression(Expression):
    """<p>An <code>InvocationExpression</code> is an <code>Expression</code> each of whose input <code>parameters</code> are bound to the <code>result</code> of an <code>argument</code> Expression.</p>

    not ownedTyping->exists(oclIsKindOf(Behavior)) and
    not ownedSubsetting.subsettedFeature.type->exists(oclIsKindOf(Behavior)) implies
        ownedFeature.selectByKind(BindingConnector)->exists(
            relatedFeature->includes(self) and
            relatedFeature->includes(result))

    TBD
    ownedFeature->
        select(direction = _'in').valuation->
        select(v | v <> null).value"""

    argument = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedArgument,
    )

    def __init__(self, *, argument=None, **kwargs):
        super().__init__(**kwargs)

        if argument:
            self.argument.extend(argument)


class NullExpression(Expression):
    """<p>A <code>NullExpression</code> is an <code>Expression</code> that results in a null value.</p>

    specializesFromLibrary("Performances::nullEvaluations")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MetadataAccessExpression(Expression):
    """<p>A <code>MetadataAccessExpression</code> is an <code>Expression</code> whose <code>result</code> is a sequence of instances of <code>Metaclasses</code> representing all the <code>MetadataFeature</code> annotations of the <code>referencedElement</code>. In addition, the sequence includes an instance of the reflective <code>Metaclass</code> corresponding to the MOF class of the <code>referencedElement</code>, with values for all the abstract syntax properties of the <code>referencedElement</code>.</p>
    specializesFromLibrary("Performances::metadataAccessEvaluations")"""

    referencedElement = EReference(
        ordered=False, unique=True, containment=False, derived=False
    )

    def __init__(self, *, referencedElement=None, **kwargs):
        super().__init__(**kwargs)

        if referencedElement is not None:
            self.referencedElement = referencedElement

    def metaclassFeature(self):
        """<p>Return a <code>MetadataFeature</code> whose <code>annotatedElement</code> is the <code>referencedElement</code>, whose <code>metaclass</code> is the reflective <code>Metaclass</code> corresponding to the MOF class of the <code>referencedElement</code> and whose <code>ownedFeatures</code> are bound to the MOF properties of the <code>referencedElement</code>.</p>"""
        raise NotImplementedError("operation metaclassFeature(...) not yet implemented")


class Metaclass(Structure):
    """<p>A <code>Metaclass</code> is a <code>Structure</code> used to type <code>MetadataFeatures</code>.</p>
    specializesFromLibrary("Metaobjects::Metaobject")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ParameterMembership(FeatureMembership):
    """<p>A <code>ParameterMembership</code> is a <code>FeatureMembership</code> that identifies its <code>memberFeature</code> as a parameter, which is always owned, and must have a <code>direction</code>. A <code>ParameterMembership</code> must be owned by a <code>Behavior</code> or a <code>Step</code>.</p>
    ownedMemberParameter.direction <> null
    owningType.oclIsKindOf(Behavior) or owningType.oclIsKindOf(Step)"""

    _ownedMemberParameter = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedMemberParameter",
        transient=True,
    )

    @property
    def ownedMemberParameter(self):
        raise NotImplementedError("Missing implementation for ownedMemberParameter")

    @ownedMemberParameter.setter
    def ownedMemberParameter(self, value):
        raise NotImplementedError("Missing implementation for ownedMemberParameter")

    def __init__(self, *, ownedMemberParameter=None, **kwargs):
        super().__init__(**kwargs)

        if ownedMemberParameter is not None:
            self.ownedMemberParameter = ownedMemberParameter


class BooleanExpression(Expression):
    """<p>A <code>BooleanExpression</code> is a <em><code>Boolean</code></em>-valued <code>Expression</code> whose type is a <code>Predicate</code>. It represents a logical condition resulting from the evaluation of the <code>Predicate</code>.</p>

    specializesFromLibrary("Performances::booleanEvaluations")"""

    _predicate = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="predicate",
        transient=True,
    )

    @property
    def predicate(self):
        raise NotImplementedError("Missing implementation for predicate")

    @predicate.setter
    def predicate(self, value):
        raise NotImplementedError("Missing implementation for predicate")

    def __init__(self, *, predicate=None, **kwargs):
        super().__init__(**kwargs)

        if predicate is not None:
            self.predicate = predicate


class ResultExpressionMembership(FeatureMembership):
    """<p>A <code>ResultExpressionMembership</code> is a <code>FeatureMembership</code> that indicates that the <code>ownedResultExpression</code> provides the result values for the <code>Function</code> or <code>Expression</code> that owns it. The owning <code>Function</code> or <code>Expression</code> must contain a <code>BindingConnector</code> between the <code>result</code> <code>parameter</code> of the <code>ownedResultExpression</code> and the <code>result</code> <code>parameter</code> of the owning <code>Function</code> or <code>Expression</code>.</p>

    owningType.oclIsKindOf(Function) or owningType.oclIsKindOf(Expression)"""

    _ownedResultExpression = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="ownedResultExpression",
        transient=True,
    )

    @property
    def ownedResultExpression(self):
        raise NotImplementedError("Missing implementation for ownedResultExpression")

    @ownedResultExpression.setter
    def ownedResultExpression(self, value):
        raise NotImplementedError("Missing implementation for ownedResultExpression")

    def __init__(self, *, ownedResultExpression=None, **kwargs):
        super().__init__(**kwargs)

        if ownedResultExpression is not None:
            self.ownedResultExpression = ownedResultExpression


class DerivedTriggerstep(EDerivedCollection):
    pass


class DerivedEffectstep(EDerivedCollection):
    pass


class DerivedGuardexpression(EDerivedCollection):
    pass


class Succession(Connector):
    """<p>A <code>Succession</code> is a binary <code>Connector</code> that requires its <code>relatedFeatures</code> to happen separately in time.</p>

    specializesFromLibrary("Occurences::happensBeforeLinks")
    transitionStep =
        if owningNamespace.oclIsKindOf(Step) and
            owningNamespace.oclAsType(Step).
                specializesFromLibrary('TransitionPerformances::TransitionPerformance') then
            owningNamespace.oclAsType(Step)
        else null
        endif
    triggerStep =
        if transitionStep = null or
           transitionStep.ownedFeature.size() < 2 or
           not transitionStep.ownedFeature->at(2).oclIsKindOf(Step)
        then Set{}
        else Set{transitionStep.ownedFeature->at(2).oclAsType(Step)}
        endif
    effectStep =
        if transitionStep = null or
           transitionStep.ownedFeature.size() < 4 or
           not transitionStep.ownedFeature->at(4).oclIsKindOf(Step)
        then Set{}
        else Set{transitionStep.ownedFeature->at(4).oclAsType(Step)}
        endif
    guardExpression =
        if transitionStep = null or
           transitionStep.ownedFeature.size() < 3 or
           not transitionStep.ownedFeature->at(3).oclIsKindOf(Expression)
        then Set{}
        else Set{transitionStep.ownedFeature->at(3).oclAsType(Expression)}
        endif"""

    _transitionStep = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="transitionStep",
        transient=True,
    )
    triggerStep = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedTriggerstep,
    )
    effectStep = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedEffectstep,
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

    @property
    def transitionStep(self):
        raise NotImplementedError("Missing implementation for transitionStep")

    @transitionStep.setter
    def transitionStep(self, value):
        raise NotImplementedError("Missing implementation for transitionStep")

    def __init__(
        self,
        *,
        transitionStep=None,
        triggerStep=None,
        effectStep=None,
        guardExpression=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if transitionStep is not None:
            self.transitionStep = transitionStep

        if triggerStep:
            self.triggerStep.extend(triggerStep)

        if effectStep:
            self.effectStep.extend(effectStep)

        if guardExpression:
            self.guardExpression.extend(guardExpression)


class BindingConnector(Connector):
    """<p>A <code>BindingConnector</code> is a binary <code>Connector</code> that requires its <code>relatedFeatures</code> to identify the same things (have the same values).</p>

    specializesFromLibrary("Links::selfLinks")
    relatedFeature->size() = 2"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class LiteralString(LiteralExpression):
    """<p>A <code>LiteralString</code> is a <code>LiteralExpression</code> that provides a <code><em>String</em></code> value as a result. Its <code>result</code> <code>parameter</code> must have the type <code><em>String</em></code>.</p>"""

    value = EAttribute(eType=String, unique=True, derived=False, changeable=True)

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


class LiteralInteger(LiteralExpression):
    """<p>A <code>LiteralInteger</code> is a <code>LiteralExpression</code> that provides an <code><em>Integer</em></code> value as a result. Its <code>result</code> <code>parameter</code> must have the type <code><em>Integer</em></code>.</p>"""

    value = EAttribute(eType=Integer, unique=True, derived=False, changeable=True)

    def __init__(self, *, value=None, **kwargs):
        super().__init__(**kwargs)

        if value is not None:
            self.value = value


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


class LiteralInfinity(LiteralExpression):
    """<p>A <code>LiteralInfinity</code> is a <code>LiteralExpression</code> that provides the positive infinity value (<code>*</code>). It's <code>result</code> must have the type <code><em>Positive</em></code>.</p>"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Predicate(Function):
    """<p>A <code>Predicate</code> is a <code>Function</code> whose <code>result</code> <code>parameter</code> has type <code><em>Boolean</em></code> and multiplicity <code>1..1</code>.</p>

    specializesFromLibrary("Performances::BooleanEvaluation")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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


class ReturnParameterMembership(ParameterMembership):
    """<p>A <code>ReturnParameterMembership</code> is a <code>ParameterMembership</code> that indicates that the <code>ownedMemberParameter</code> is the <code>result</code> <code>parameter</code> of a <code>Function</code> or <code>Expression</code>. The <code>direction</code> of the <code>ownedMemberParameter</code> must be <code>out</code>.</p>

    owningType.oclIsKindOf(Function) or owningType.oclIsKindOf(Expression)
    ownedMemberParameter.direction = ParameterDirectionKind::out"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DerivedItemtype(EDerivedCollection):
    pass


class DerivedItemflowend(EDerivedCollection):
    pass


class DerivedInteraction(EDerivedCollection):
    pass


class ItemFlow(Connector, Step):
    """<p>An <code>ItemFlow</code> is a <code>Step</code> that represents the transfer of objects or data values from one <code>Feature</code> to another. <code>ItemFlows</code> can take non-zero time to complete.</p>

    if itemFlowEnds->isEmpty() then
        specializesFromLibrary("Transfers::transfers")
    else
        specializesFromLibrary("Transfers::flowTransfers")
    endif
    itemType =
        if itemFeature = null then Sequence{}
        else itemFeature.type
        endif
    sourceOutputFeature =
        if connectorEnd->isEmpty() or
            connectorEnd.ownedFeature->isEmpty()
        then null
        else connectorEnd.ownedFeature->first()
        endif
    targetInputFeature =
        if connectorEnd->size() < 2 or
            connectorEnd->at(2).ownedFeature->isEmpty()
        then null
        else connectorEnd->at(2).ownedFeature->first()
        endif
    itemFlowEnd = connectorEnd->selectByKind(ItemFlowEnd)
    itemFeature =
        let itemFeatures : Sequence(ItemFeature) =
            ownedFeature->selectByKind(ItemFeature) in
        if itemFeatures->isEmpty() then null
        else itemFeatures->first()
        endif
    ownedFeature->selectByKind(ItemFeature)->size() <= 1"""

    itemType = EReference(
        ordered=True,
        unique=False,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedItemtype,
    )
    _targetInputFeature = EReference(
        ordered=True,
        unique=False,
        containment=False,
        derived=True,
        name="targetInputFeature",
        transient=True,
    )
    _sourceOutputFeature = EReference(
        ordered=True,
        unique=False,
        containment=False,
        derived=True,
        name="sourceOutputFeature",
        transient=True,
    )
    itemFlowEnd = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedItemflowend,
    )
    _itemFeature = EReference(
        ordered=False,
        unique=True,
        containment=False,
        derived=True,
        name="itemFeature",
        transient=True,
    )
    interaction = EReference(
        ordered=True,
        unique=True,
        containment=False,
        derived=True,
        upper=-1,
        transient=True,
        derived_class=DerivedInteraction,
    )

    @property
    def targetInputFeature(self):
        raise NotImplementedError("Missing implementation for targetInputFeature")

    @targetInputFeature.setter
    def targetInputFeature(self, value):
        raise NotImplementedError("Missing implementation for targetInputFeature")

    @property
    def sourceOutputFeature(self):
        raise NotImplementedError("Missing implementation for sourceOutputFeature")

    @sourceOutputFeature.setter
    def sourceOutputFeature(self, value):
        raise NotImplementedError("Missing implementation for sourceOutputFeature")

    @property
    def itemFeature(self):
        raise NotImplementedError("Missing implementation for itemFeature")

    @itemFeature.setter
    def itemFeature(self, value):
        raise NotImplementedError("Missing implementation for itemFeature")

    def __init__(
        self,
        *,
        itemType=None,
        targetInputFeature=None,
        sourceOutputFeature=None,
        itemFlowEnd=None,
        itemFeature=None,
        interaction=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        if itemType:
            self.itemType.extend(itemType)

        if targetInputFeature is not None:
            self.targetInputFeature = targetInputFeature

        if sourceOutputFeature is not None:
            self.sourceOutputFeature = sourceOutputFeature

        if itemFlowEnd:
            self.itemFlowEnd.extend(itemFlowEnd)

        if itemFeature is not None:
            self.itemFeature = itemFeature

        if interaction:
            self.interaction.extend(interaction)


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
        """<p>Return the first <code>ownedFeature</code> of the first owned input <code>parameter</code> of this <code>FeatureChainExpression</code> (if any).</p>"""
        raise NotImplementedError(
            "operation sourceTargetFeature(...) not yet implemented"
        )


class AssociationStructure(Association, Structure):
    """<p>An <code>AssociationStructure</code> is an <code>Association</code> that is also a <code>Structure</code>, classifying link objects that are both links and objects. As objects, link objects can be created and destroyed, and their non-end <code>Features</code> can change over time. However, the values of the end <code>Features</code> of a link object are fixed and cannot change over its lifetime.</p>
    specializesFromLibrary("Objects::ObjectLink")
    endFeature->size() = 2 implies
        specializesFromLibrary("Objects::BinaryLinkObject")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Interaction(Association, Behavior):
    """<p>An <code>Interaction</code> is a <code>Behavior</code> that is also an <code>Association</code>, providing a context for multiple objects that have behaviors that impact one another.</p>"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SuccessionItemFlow(ItemFlow, Succession):
    """<p>A <code>SuccessionItemFlow</code> is an <code>ItemFlow</code> that also provides temporal ordering. It classifies <code><em>Transfers</em></code> that cannot start until the source <code><em>Occurrence</em></code> has completed and that must complete before the target <code><em>Occurrence</em></code> can start.</p>
    specializesFromLibrary("Transfers::flowTransfersBefore")"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
