"""
UML model support functions.

Functions collected in this module allow to

- create more complex UML model structures
- perform specific searches and manipulations

"""

import itertools

def stereotypes_str(element, stereotypes=()):
    """
    Identify stereotypes of an UML metamodel instance and return coma
    separated stereotypes as string.

    :Parameters:
     element
        Element having stereotypes, can be None.
     stereotypes
        List of additional stereotypes, can be empty.
    """
    # generate string with stereotype names separated by coma
    if element:
        applied = (stereotype_name(s) for s in element.appliedStereotype)
    else:
        applied = ()
    return ', '.join(itertools.chain(stereotypes, applied))


def stereotype_name(stereotype):
    """
    Return stereotype name suggested by UML specification. First will be
    character lowercase unless the second character is uppercase.

    :Parameters:
     stereotype
        Stereotype UML metamodel instance.
    """
    name = stereotype.name
    if len(name) > 1 and name[1].isupper():
        return name
    else:
        return name[0].lower() + name[1:]


# vim:sw=4:et
