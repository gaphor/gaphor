#!/usr/bin/env python

# vim:sw=4

def register (item_class, uml_class):
    '''Register a canvas item.'''
    from gobject import type_register
    from UML import Diagram
    type_register(item_class)
    Diagram.diagram2UML[item_class] = uml_class

