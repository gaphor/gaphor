# vim: sw=4:et
"""
Load and save Gaphor models to Gaphors own XML format.
Three functions are exported:
load(filename)
    load a model from a file
save(filename)
    store the current model in a file
verify(filename)
    check the validity of the file (this does not tell us
    we have a valid model, just a valid file).
"""

import UML
import parser
import diagram
#import diacanvas
import os.path
import types
#import xml.dom.minidom as dom
import gc

FILE_FORMAT_VERSION = '2.0'

def save(filename=None, factory=None):
    '''Save the current model to @filename. If no filename is given,
    standard out is used.'''
    from cStringIO import StringIO
    from xml.sax.saxutils import escape
    #from gaphor.UML import collection
    #from element import Element

    def save_element(name, value):
        if isinstance (value, UML.Element):
            # Save a reference to the object:
            buffer.write('<reference name="%s" refid="%s"/>\n' % (name, value.id))
        elif isinstance(value, UML.collection):
            # Save a list of references:
	    #buffer.write('<reflist>')
            for v in value:
                save_element(name, v)
	    #buffer.write('</reflist>')
        elif isinstance(value, diacanvas.Canvas):
            buffer.write('<canvas>')
            value.save(save_element)
            buffer.write('</canvas>')
        elif isinstance(value, diacanvas.CanvasItem):
            buffer.write('<canvasitem>')
            value.save(save_element)
            buffer.write('</canvasitem>')
        else:
            buffer.write('<value name="%s">' % name)
            if isinstance(value, types.StringTypes):
                buffer.write('<![CDATA[%s]]>' % value.replace(']]>', '] ]>'))
            else:
                buffer.write(escape(str(value)))
            buffer.write('</value>\n')

    if not factory:
        factory = GaphorResource(UML.ElementFactory)

    buffer = StringIO()
    buffer.write('<?xml version="1.0" encoding="utf-8"?>\n')
    buffer.write('<gaphor version="%s">' % FILE_FORMAT_VERSION)

    for e in factory.values():
        buffer.write('<element id="%s" type="%s">' % (str(e.id), e.__class__.__name__))
        e.save(save_element)
        buffer.write('</element>')

    buffer.write('</gaphor>')

    buffer.reset()

    if not filename:
        print str(buffer.read())
    else:
        file = open (filename, 'w')
        if not file:
            raise IOError, 'Could not open file `%s\'' % (filename)
        try:
            file.write(buffer.read())
        finally:
            file.close()

def _load (elements, factory):
    '''Load a file and create a model if possible.
    Exceptions: IOError, ValueError.'''

    log.info('0%')

    # First create elements and canvas items in the factory:
    for id, elem in elements.items():
        if isinstance(elem, parser.element):
            type = getattr (UML, elem.type)
            elem.element = factory.create_as (type, id)
        elif isinstance(elem, parser.canvasitem):
            cls = getattr(diagram, elem.type)
            elem.element = cls()
            elem.element.set_property('id', id)
            # Add a canvas property so we can be lasy and do not check...
            elem.canvas = None

    log.info('0% ... 33%')

    # load attributes and create references:
    for id, elem in elements.items():
        # establish parent/child relations on canvas items:
        if elem.canvas:
            for item in elem.canvas.canvasitems:
                print 'item:', item.element
                item.element.set_property('parent', elem.element.canvas.root)
        if isinstance(elem, parser.canvasitem):
            for item in elem.canvasitems:
                item.element.set_property('parent', elem.element)

        # load attributes and references:
        for name, value in elem.values.items():
            elem.element.load(name, value)
        for name, refids in elem.references.items():
            for refid in refids:
                try:
                    ref = elements[refid]
                except:
                    raise ValueError, 'Invalid ID for reference (%s)' % refid
                else:
                    elem.element.load(name, ref.element)
        
    log.info('0% ... 33% ... 66%')

    # do a postload:
    for id, elem in elements.items():
        elem.element.postload()

    log.info('0% ... 33% ... 66% ... 100%')

    factory.notify_model()

def load (filename, factory=None):
    '''Load a file and create a model if possible.
    Exceptions: GaphorError.'''
    log.info('Loading file %s' % os.path.basename(filename))
    try:
        elements = parser.parse(filename) #dom.parse (filename)
    except Exception, e:
        print e
        log.error('File could no be parsed')
        raise GaphorError, 'File %s is probably no valid XML.' % filename

    try:
            # For some reason, loading the model in a temp. factory will
        # cause DiaCanvas2 to keep a idle handler around... This should
        # be fixed in DiaCanvas2 ASAP.
        #factory = UML.ElementFactory()
        #_load(doc, factory)
        #gc.collect()
        #factory.flush()
        #del factory
        #gc.collect()
        #print '===================================== pre load succeeded =='
        if not factory:
            factory = GaphorResource(UML.ElementFactory)
        factory.flush()
        gc.collect()
	_load(elements, factory)
        # DEBUG code:
#        print ''
#        print ''
#        print ''
#        for d in factory.select(lambda e: e.isKindOf(UML.Diagram)):
#            for i in d.canvas.root.children:
#                print i, i.__dict__
        gc.collect()
#        for d in factory.select(lambda e: e.isKindOf(UML.Diagram)):
#            for i in d.canvas.root.children:
#                print i, i.__dict__
#                print '   ', i.get_property('id')

    except Exception, e:
        log.info('file %s could not be loaded' % filename)
        import traceback
        traceback.print_exc()
        raise GaphorError, 'Could not load file %s (%s)' % (filename, e)

def verify (filename):
    """
    Try to load the file. If loading succeeded, this file is probably a valid
    Gaphor file.
    """
    try:
        doc = dom.parse (filename)
    except Exception, e:
        log.info('File %s is probably no valid XML.' % filename)
        return False

    factory = UML.ElementFactory()
    try:
        _load(doc, factory)
    except Exception, e:
        log.info('File %s could not be loaded' % filename)
        return False

    return True
