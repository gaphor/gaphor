# vim: sw=4

import UML, diacanvas, diagramitems, types


# Forward declaration
loadsavetable = None

_transtable = { } # table to translate 'cid' to object

def get_transtable ():
    global _transtable
    tt = _transtable
    _transtable = { }
    return tt

def set_transtable (tt):
    global _transtable
    _transtable = tt

def flush_transtable ():
    global _transtable
    _transtable = { }
    
def save (item, parent, ns):
    global loadsavetable
    rec = loadsavetable[item.__class__]
    return rec[0] (item, parent, ns)

def load (item, factory, node):
    global loadsavetable
    rec = loadsavetable[item.__class__]
    rec[1] (item, factory, node)

def postload (item, node):
    global loadsavetable
    rec = loadsavetable[item.__class__]
    if len (rec) > 2:
	rec[2] (item, node)


#def save_attr (item, node, attr):
    #node.setProp (attr, repr (item.get_property (attr)))
#    child = node.newChild (ns, 'Value', repr (item.get_property (attr)))
#    child.setProp ('name', attr)

def save_value (node, ns, name, val):
    if not isinstance (val, types.StringType):
        val = repr (val)
    child = node.newChild (ns, 'Value', None)
    child.setProp ('name', name)
    child.setProp ('value', val)

def load_value (node, name):
    child = node.children
    while child:
        #print child
        if child.name == 'Value' and child.prop('name') == name:
	    return child.prop ('value')
	child = child.next
    raise ValueError, 'No value found with name %s' % name

def cid (item):
    '''Create a unique ID for the canvas item based on it's memory address.'''
    return str (item)[-9:-1]

#
# CanvasItem
#
def canvas_item_save (item, parent, ns):
    node = parent.newChild (ns, 'CanvasItem', None)
    node.setProp ('type', item.__class__.__name__)
    # The 'cid' (canvas id) is the memory address of the item
    node.setProp ('cid', cid (item))
    save_value (node, ns, 'affine', item.get_property ('affine'))
    return node

def canvas_item_load (item, factory, node):
    cid = node.prop ('cid')
    _transtable[cid] = item
    #load_attr (item, node, 'affine')
    item.set_property ('affine', eval (load_value (node, 'affine')))

#
# CanvasElement
#
def canvas_element_save (item, parent, ns):
    node = canvas_item_save (item, parent, ns)
    save_value (node, ns, 'width', item.get_property ('width'))
    save_value (node, ns, 'height', item.get_property ('height'))
    return node

def canvas_element_load (item, factory, node):
    canvas_item_load (item, factory, node)
    item.set_property ('width', eval (load_value (node, 'width')))
    item.set_property ('height', eval (load_value (node, 'height')))

#
# CanvasLine
#
def canvas_line_save (item, parent, ns):
    node = canvas_item_save (item, parent, ns)
    points = [ ]
    for h in item.handles:
	pos = h.get_property ('pos_i')
	#print 'pos:', pos
	points.append (pos)
    save_value (node, ns, 'points', points)
    c = item.handles[0].connected_to
    if c:
	save_value (node, ns, 'head_connection', cid (c))
    c = item.handles[-1].connected_to
    if c:
	save_value (node, ns, 'tail_connection', cid (c))
    return node

def canvas_line_load (item, factory, node):
    canvas_item_load (item, factory, node)
    #childnode = node.firstChild
    #points = [ ]
    attr = load_value (node, 'points')
    if attr:
        points = eval(attr)
	if len (points) > 0:
	    assert len (points) >= 2
	    item.set_property ('head_pos', points[0])
	    item.set_property ('tail_pos', points[1])
	    for p in points[2:]:
		item.set_property ('add_point', p)

def canvas_line_postload (item, node):
    attr = load_value (node, 'head_connection')
    if attr:
	the_item = _transtable[attr]
	the_item.handle_connect (item.handles[0])
    attr = load_value (node, 'tail_connection')
    if attr:
	the_item = _transtable[attr]
	the_item.handle_connect (item.handles[-1])

#
# ModelElement
#
def model_element_save (item, parent, ns):
    node = canvas_element_save (item, parent, ns)
    save_value (node, ns, 'auto_resize', item.get_property ('auto_resize'))
    save_value (node, ns, 'subject', item.subject.id)
    return node

def model_element_load (item, factory, node):
    canvas_element_load (item, factory, node)
    attr = load_value (node, 'subject')
    if attr:
	factory = UML.ElementFactory ()
	subject = factory.lookup (eval (attr))
	if subject:
	    item.set_subject (subject)
	else:
	    raise ValueError, 'Item has subject, but no such object found'
    # Do not set auto_resize now, so we can update the items content without
    # changing the stored width and height.
    item.set_property ('auto_resize', 0)

def model_element_postload (item, node):
    item.set_property ('auto_resize', eval(load_value (node, 'auto_resize')))
    
#
# Relationship
#
def relationship_save (item, parent, ns):
    node = canvas_line_save (item, parent, ns)
    save_value (node, ns, 'subject', item.subject.id)
    return node

def relationship_load (item, factory, node):
    canvas_line_load (item, factory, node)
    attr = load_value (node, 'subject')
    if attr:
	#print item, 'Have a subject'
	factory = UML.ElementFactory ()
	subject = factory.lookup (eval (attr))
	if subject:
	    #print item, 'Set a subject', subject
	    item.set_subject (subject)
	else:
	    raise ValueError, 'Item has subject, but no such object found'

#
# Update items through specific load functions
#
def actor_load (item, factory, node):
    model_element_load (item, factory, node)
    item.element_update ('name')

def comment_load (item, factory, node):
    model_element_load (item, factory, node)
    item.element_update ('body')

def usecase_load (item, factory, node):
    model_element_load (item, factory, node)
    item.element_update ('name')

def generalization_load (item, factory, node):
    relationship_load (item, factory, node)

loadsavetable = {
	diacanvas.CanvasGroup: (canvas_item_save, canvas_item_load ),
	diagramitems.Actor: (model_element_save, actor_load, model_element_postload ),
	diagramitems.Comment: (model_element_save, comment_load, model_element_postload ),
	diagramitems.UseCase: (model_element_save, usecase_load, model_element_postload ),
	diagramitems.CommentLine: ( canvas_line_save, canvas_line_load, canvas_line_postload ),
	diagramitems.Generalization: ( relationship_save, generalization_load, canvas_line_postload ),
	diagramitems.Dependency: ( relationship_save, relationship_load, canvas_line_postload ),
	diagramitems.Realization: ( relationship_save, relationship_load, canvas_line_postload ),
	diagramitems.Include: ( relationship_save, relationship_load, canvas_line_postload ),
	diagramitems.Extend: ( relationship_save, relationship_load, canvas_line_postload )
}
