# vim: sw=4

import UML, diacanvas, diagramitems


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
    
def save (item, document, parent):
    global loadsavetable
    rec = loadsavetable[item.__class__]
    return rec[0] (item, document, parent)

def load (item, node):
    global loadsavetable
    rec = loadsavetable[item.__class__]
    rec[1] (item, node)

def postload (item, node):
    global loadsavetable
    rec = loadsavetable[item.__class__]
    if len (rec) > 2:
	rec[2] (item, node)


def save_attr (item, node, attr):
    node.setAttribute (attr, repr (item.get_property (attr)))

def load_attr (item, node, a):
    attr = node.getAttribute (a)
    if attr:
	item.set_property (a, eval (attr))

def cid (item):
    return str (item)[-10:-1]

#
# CanvasItem
#
def canvas_item_save (item, document, parent):
    node = document.createElement ('CanvasItem')
    parent.appendChild (node)
    node.setAttribute ('type', item.__class__.__name__)
    # The 'cid' (canvas id) is the memory address of the item
    node.setAttribute ('cid', cid (item))
    save_attr (item, node, 'affine')
    return node

def canvas_item_load (item, node):
    cid = node.getAttribute ('cid')
    _transtable[cid] = item
    load_attr (item, node, 'affine')

#
# CanvasElement
#
def canvas_element_save (item, document, parent):
    node = canvas_item_save (item, document, parent)
    save_attr (item, node, 'width')
    save_attr (item, node, 'height')
    return node

def canvas_element_load (item, node):
    canvas_item_load (item, node)
    load_attr (item, node, 'width')
    load_attr (item, node, 'height')

#
# CanvasLine
#
def canvas_line_save (item, document, parent):
    node = canvas_item_save (item, document, parent)
    points = [ ]
    for h in item.handles:
	pos = h.get_property ('pos_i')
	print 'pos:', pos
	#posnode = document.createElement ('Point')
	#node.appendChild (posnode)
	#posnode.setAttribute ('value', repr (pos))
	points.append (pos)
    node.setAttribute ('points', repr (points))
    c = item.handles[0].connected_to
    if c:
	node.setAttribute ('head_connection', cid (c))
    c = item.handles[-1].connected_to
    if c:
	node.setAttribute ('tail_connection', cid (c))
    return node

def canvas_line_load (item, node):
    canvas_item_load (item, node)
    #childnode = node.firstChild
    #points = [ ]
    attr = node.getAttribute ('points')
    if attr:
        points = eval(attr)
	if len (points) > 0:
	    assert len (points) >= 2
	    item.set_property ('head_pos', points[0])
	    item.set_property ('tail_pos', points[1])
	    for p in points[2:]:
		item.set_property ('add_point', p)

#    while childnode:
#	if childnode.tagName == 'Point':
#	    value = childnode.getAttribute ('value')
#	    assert value != None
#	    points.append (eval (value))
#	childnode = childnode.nextSibling

#    if len (points) > 0:
#	assert len (points) >= 2
#	item.set_property ('head_pos', points[0])
#	item.set_property ('tail_pos', points[1])
#	for p in points[2:]:
#	    item.set_property ('add_point', p)

def canvas_line_postload (item, node):
    attr = node.getAttribute ('head_connection')
    if attr:
	the_item = _transtable[attr]
	the_item.handle_connect (item.handles[0])
    attr = node.getAttribute ('tail_connection')
    if attr:
	the_item = _transtable[attr]
	the_item.handle_connect (item.handles[-1])

#
# ModelElement
#
def model_element_save (item, document, parent):
    node = canvas_element_save (item, document, parent)
    save_attr (item, node, 'auto_resize')
    node.setAttribute ('subject', str (item.subject.id))
    return node

def model_element_load (item, node):
    canvas_element_load (item, node)
    attr = node.getAttribute ('subject')
    if attr:
	subject = UML.lookup (eval (attr))
	if subject:
	    item.set_subject (subject)
	else:
	    raise ValueError, 'Item has subject, but no such object found'
    # Do not set auto_resize now, so we can update the items content without
    # changing the stored width and height.
    item.set_property ('auto_resize', 0)

def model_element_postload (item, node):
    load_attr (item, node, 'auto_resize')
    
#
# Relationship
#
def relationship_save (item, document, parent):
    node = canvas_line_save (item, document, parent)
    node.setAttribute ('subject', str (item.subject.id))
    return node

def relationship_load (item, node):
    canvas_line_load (item, node)
    attr = node.getAttribute ('subject')
    if attr:
	print item, 'Have a subject'
	subject = UML.lookup (eval (attr))
	if subject:
	    print item, 'Set a subject', subject
	    item.set_subject (subject)
	else:
	    raise ValueError, 'Item has subject, but no such object found'

#
# Update items through specific load functions
#
def actor_load (item, node):
    model_element_load (item, node)
    item.element_update ('name')

def comment_load (item, node):
    model_element_load (item, node)
    item.element_update ('body')

def usecase_load (item, node):
    model_element_load (item, node)
    item.element_update ('name')

def generalization_load (item, node):
    relationship_load (item, node)

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
