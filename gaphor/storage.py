# vim: sw=4:et
"""Load and save Gaphor models to Gaphors own XML format.

Three functions are exported:
load(filename)
    load a model from a file
save(filename)
    store the current model in a file
verify(filename)
    check the validity of the file (this does not tell us
    we have a valid model, just a valid file).
"""

from cStringIO import StringIO
from xml.sax.saxutils import escape
import types
import os.path
import gc
import UML
import parser
import diagram
import diacanvas

__all__ = [ 'load', 'save' ]

FILE_FORMAT_VERSION = '2.0'

def save(filename=None, factory=None):
    """Save the current model to @filename. If no filename is given,
    standard out is used.
    """

    def save_reference(name, value):
        """Save a value as a reference to another element in the model.
        This applies to both UML as well as canvas items.
        """
        # Save a reference to the object:
        if value.id:
            buffer.write('<reference name="%s" refid="%s"/>\n' % (name, value.id))

    def save_collection(name, value):
        """Save a list of references.
        """
        #buffer.write('<reflist>')
        for v in value:
            save_reference(name, v)
        #buffer.write('</reflist>')

    def save_value(name, value):
        """Save a value (attribute).
        If the value is a string, it is saves as a CDATA block.
        """
        if value is not None:
            buffer.write('<value name="%s">' % name)
            if isinstance(value, types.StringTypes):
                buffer.write('<![CDATA[%s]]>' % value.replace(']]>', '] ]>'))
            else:
                buffer.write(escape(str(value)))
            buffer.write('</value>\n')

    def save_element(name, value):
        """Save attributes and references from items in the gaphor.UML module.
        A value may be a primitive (string, int), a gaphor.UML.collection
        (which contains a list of references to other UML elements) or a
        diacanvas.Canvas (which contains canvas items).
        """
        if isinstance (value, (UML.Element, diacanvas.CanvasItem)):
            save_reference(name, value)
        elif isinstance(value, UML.collection):
            save_collection(name, value)
        elif isinstance(value, diacanvas.Canvas):
            buffer.write('<canvas>')
            value.save(save_canvasitem)
            buffer.write('</canvas>')
        else:
            save_value(name, value)

    def save_canvasitem(name, value, reference=False):
        """Save attributes and references in a gaphor.diagram.* object.
        The extra attribute reference can be used to force UML 
        """
        #log.debug('saving canvasitem: %s|%s %s' % (name, value, type(value)))
        if reference or isinstance(value, UML.Element):
            save_reference(name, value)
        elif isinstance(value, UML.collection):
            save_collection(name, value)
        elif isinstance(value, diacanvas.CanvasItem):
            buffer.write('<canvasitem id="%s" type="%s">' % (value.id, value.__class__.__name__))
            value.save(save_canvasitem)
            buffer.write('</canvasitem>')
        else:
            save_value(name, value)

    if not factory:
        factory = GaphorResource(UML.ElementFactory)

    buffer = StringIO()
    buffer.write('<?xml version="1.0"?>\n')
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

def _load(elements, factory):
    """Load a file and create a model if possible.
    Exceptions: IOError, ValueError.
    """

    log.debug('Loading %d elements...' % len(elements.keys()))

    log.info('0%')

    # First create elements and canvas items in the factory
    # The elements are stored as attribute 'element' on the parser objects:
    for id, elem in elements.items():
        if isinstance(elem, parser.element):
            try:
                cls = getattr(UML, elem.type)
                #log.debug('Creating UML element for %s' % elem)
                elem.element = factory.create_as(cls, id)
            except:
                raise
        elif isinstance(elem, parser.canvasitem):
            cls = getattr(diagram, elem.type)
            #log.debug('Creating canvas item for %s' % elem)
            elem.element = cls(id)
        else:
            raise ValueError, 'Item with id "%s" and type %s can not be instantiated' % (id, type(elem))

    log.info('0% ... 33%')

    # load attributes and create references:
    for id, elem in elements.items():
        # Ensure that all elements have their element instance ready...
        assert hasattr(elem, 'element')

        # establish parent/child relations on canvas items:
        if isinstance(elem, parser.element) and elem.canvas:
            for item in elem.canvas.canvasitems:
                assert item in elements.values(), 'Item %s (%s) is a canvas item, but it is not in the parsed objects table' % (item, item.id)
                item.element.set_property('parent', elem.element.canvas.root)
        if isinstance(elem, parser.canvasitem):
            for item in elem.canvasitems:
                assert item in elements.values(), 'Item %s (%s) is a canvas item, but it is not in the parsed objects table' % (item, item.id)
                item.element.set_property('parent', elem.element)

        # load attributes and references:
        for name, value in elem.values.items():
            log.debug('Loading value %s (%s) for element %s' % (name, value, elem.element))
            elem.element.load(name, value)
        for name, refids in elem.references.items():
            for refid in refids:
                try:
                    ref = elements[refid]
                except:
                    raise ValueError, 'Invalid ID for reference (%s)' % refid
                else:
                    log.debug('Loading %s.%s with value %s' % (type(elem.element).__name__, name, ref.element.id))
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
        raise
        #raise GaphorError, 'File %s is probably no valid XML.' % filename

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
            from gaphor import Gaphor
            factory = Gaphor.get_resource(UML.ElementFactory)
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
    """Try to load the file. If loading succeeded, this file is
    probably a valid Gaphor file.
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
