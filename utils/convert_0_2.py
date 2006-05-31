# vim:sw=4:et:
"""
Convert a model from Gaphor version 0.2 to Gaphor version 0.3.
"""
import env
import operator

import gaphor.parser as parser
import gaphor.storage as storage
import gaphor.UML as UML
from gaphor.misc.uniqueid import generate_id

def get_ref(elem, key):
    try:
        return elem.references[key]
    except KeyError:
        return elem.references[properties_conversion_map[key]]

def _convert_multiplicity(elements, elem, prop):
    spec = parser.element(generate_id(), 'LiteralSpecification')
    spec.values['value'] = elem.values['multiplicity']
    elem.references['lowerValue'] = [ spec.id ]
    elements[spec.id] = spec
    del elem.values['multiplicity']

def _convert_aggregation(elements, elem, prop):
    """Strip first three characters from aggregation type (e.g. ak_none ->none)
    """
    #print elem, elem[prop]
    elem.values['aggregation'] = elem.values['aggregation'][3:]

def _convert_isNavigable(elements, elem, prop):
    if eval(elem['isNavigable']):
        # The property is navigable. This means that it is owned by the
        # class on the other end of the association.
        assoc_id = elem.references['association']
        assert len(assoc_id) == 1
        assoc = elements[assoc_id[0]]
        end_ids = get_ref(assoc, 'connection')
        other_end = elements[(end_ids[0] == elem.id) and end_ids[1] or end_ids[0]]
        clazz = elements[get_ref(other_end, 'participant')[0]]
        # Create an class_ -- ownedAttribute relationship
        attr = clazz.references.get('ownedAttribute')
        if attr is None:
            attr = clazz.references['ownedAttribute'] = []
        attr.append(elem.id)
        assert elem.references.get('class_') is None
        elem.references['class_'] = [clazz.id]
    else:
	elem.references['owningAssociation'] = elem['association']
    del elem.values['isNavigable']

def _convert_ownedElement(elements, elem, prop):
    for ref in elem.references['ownedElement']:
        if elements[ref].type == 'Diagram':
            own = 'ownedDiagram'
        elif elements[ref].type == 'Package':
            own = 'nestedPackage'
        else:
            own = 'ownedClassifier'
        l = elem.references.get(own)
        if l is None:
            l = elem.references[own] = []
        l.append(ref)

    del elem.references['ownedElement']

def remove (elements, elem, prop):
    del elem.references[prop]

# Property names are unique (unique enough anyway)
properties_conversion_map = {
    'comment': 'ownedComment',
    'namespace': 'package',
    # Association
    'connection': 'memberEnd',
    # AssociationEnd
    'aggregation': _convert_aggregation,
    'isNavigable': _convert_isNavigable,
    'multiplicity': _convert_multiplicity,
    'participant': 'type',
    # Attribute
    'Attribute.owner': 'class_',
    # Class
    'feature': 'ownedAttribute',
    'specialization': remove,
    'Class.association': remove,
    # Generalization
    'child': 'specific',
    'parent': 'general',
    # Package
    'ownedElement': _convert_ownedElement
}

classname_conversion_map = {
    'Model': 'Package',
    'Attribute': 'Property',
    'AssociationEnd': 'Property'
}

def convert_elements(elements):
    """Change the elements dictionary (as it is returned from
    gaphor.parser.parse()) and convert the entries so they can be loaded in
    the data model of the current version.
    """
    element_list = filter(lambda x: isinstance(x, parser.element), elements.values())
    # convert property names:
    for e in element_list:
        # First ensure that all AssociationEnd have isNavigable set
        # (This is the only attribute set to True by default):
        if e.type == 'AssociationEnd' and not e.values.get('isNavigable'):
            e.values['isNavigable'] = 'True'

	for p in e.values.keys() + e.references.keys():
	    func_or_str = properties_conversion_map.get('%s.%s' % (e.type, p)) \
                          or properties_conversion_map.get(p)
	    if func_or_str:
		if operator.isCallable(func_or_str):
		    func_or_str(elements, e, p)
		else:
		    if p in e.values.keys():
			e.values[func_or_str] = e.values[p]
			del e.values[p]
		    else:
			e.references[func_or_str] = e.references[p]
			del e.references[p]

    for e in element_list:
	if e.type in classname_conversion_map.keys():
	    e.type = classname_conversion_map[e.type]

    item_list = filter(lambda x: isinstance(x, parser.canvasitem), elements.values())
    for i in item_list:
        subject = i.references.get('subject')
        if subject:
            e = elements[subject[0]]
            p = e.references.get('presentation')
            if p is None:
                p = e.references['presentation'] = []
            p.append(i.id)

def convert_factory(factory):
    for a in factory.select(lambda e: isinstance(e, UML.Association)):
        # Link Association.package to the package which owns the diagram
        # the association is drawn in.
        p = a.presentation[0]
        a.package = p.canvas.diagram.namespace

        # If an association's end is not owned by a Class and is not
        # owned by the association, let it be owned by the association
        for p in a.memberEnd:
            if not p.class_ and not p.owningAssociation:
                p.owningAssociation = a

if __name__ == '__main__':
    import sys
    elements = parser.parse(sys.argv[1])
    convert_elements(elements)
    factory = UML.ElementFactory()
    storage._load(elements, factory)
    convert_factory(factory)
    storage.save('converted.gaphor', factory)

