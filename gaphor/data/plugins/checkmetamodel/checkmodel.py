# vim:sw=4:et

from gaphor import storage
from gaphor import UML
from gaphor.core import inject
from os import path

def report(element, message):
    print '%s: %s' % (type(element).__name__, message)

def get_subsets(tagged_value):
    subsets = []
    if tagged_value.find('subsets') != -1:
        subsets = tagged_value[tagged_value.find('subsets') + len('subsets'):]
        subsets = subsets.replace(' ', '').replace('\n', '').replace('\r', '')
        subsets = subsets.split(',')
    return subsets

def get_redefine(tagged_value):
    redefines = tag[tag.find('redefines') + len('redefines'):]
    # remove all whitespaces and stuff
    redefines = redefines.replace(' ', '').replace('\n', '').replace('\r', '')
    redefines = redefines.split(',')
    assert len(redefines) == 1
    return redefines[0]

def get_superclasses(class_):
    for superclass in class_.superClass:
        gen = 1


def check_classes():
    classes = UML.select(lambda e: e.isKindOf(UML.Class))
    names = [ c.name for c in classes ]
    for c in classes:
        if names.count(c.name) > 1:
            report(c, 'Class name %s used more than once' % c.name)
    

def check_association_end_subsets(end):
    subsets = get_subsets(end.taggedValue and end.taggedValue.value or '')
    opposite_subsets = get_subsets(end.opposite.taggedValue and end.opposite.taggedValue.value or '')
    subset_properties = UML.select(lambda e: e.isKindOf(UML.Property) and e.name in subsets)

    # TODO: check if properties belong to a superclass of the end's class

    # TODO: check if the association end is navigable when the subsets are navigable
    for p in subset_properties:
        pass

    # Check if bi-directional derived unions are bi-directional on this association
    for p in subset_properties:
        if p.opposite.name and p.opposite.name not in opposite_subsets:
            report(end, 'Subset not defined on both sides. (%s, %s)' % (p.name, p.opposite.name))

    # Check if multiplicity of the properties matches the multiplicity of the subsets
    for p in subset_properties:
        if p.upperValue:
            if not end.upperValue:
                report(end, 'Association end %s has no upper value, but the subset %s has' % (end.name, p.name))
            elif p.upperValue.value < end.upperValue.value:
                report(end, 'Association end %s has has a bigger upper value than subse %s' % (end.name, p.name))

def check_association_end(end):
    check_association_end_subsets(end)

def check_associations():
    for a in UML.select(lambda e: e.isKindOf(UML.Association)):
        assert len(a.memberEnd) == 2
        head = a.memberEnd[0]
        tail = a.memberEnd[1]
        check_association_end(head)
        check_association_end(tail)

def check_attributes():
    for a in UML.select(lambda e: e.isKindOf(UML.Property) and not e.association):
        if not a.typeValue or not a.typeValue.value:
            report(a,'Attribute has no type: %s' % a.name)
        elif a.typeValue.value.lower() not in ('string', 'boolean', 'integer', 'unlimitednatural'):
            report(a, 'Invalid attribute type: %s' % a.taggedValue.value)

# TODO: Check the sanity of the generated data model.
def check_UML_module():
    all_classes = map(getattr, [UML] * len(dir(UML)), dir(UML))
    for c in all_classes:
        if not isinstance(c, UML.Element):
            continue
        # TODO: check derived unions.

if __name__ == '__main__':
    storage.load(path.join('gaphor', 'UML', 'uml2.gaphor'))
    check_associations()
    check_attributes()

