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
import gaphor
from gaphor.i18n import _

__all__ = [ 'load', 'save' ]

FILE_FORMAT_VERSION = '3.0'

def save(filename=None, factory=None, status_queue=None):
    for status in save_coroutine(filename, factory):
        status_queue(status)

def save_coroutine(filename=None, factory=None):
    """Save the current model to @filename. If no filename is given,
    standard out is used.
    """
    # Make bool work for Python 2.2
    bool_ = type(bool(0))

    def save_reference(name, value):
        """Save a value as a reference to another element in the model.
        This applies to both UML as well as canvas items.
        """
        # Save a reference to the object:
        if value.id: #, 'Referenced element %s has no id' % value
            buffer.write('<%s><ref refid="%s"/></%s>\n' % (name, value.id, name))

    def save_collection(name, value):
        """Save a list of references.
        """
        if len(value) > 0:
            buffer.write('<%s><reflist>' % name)
            for v in value:
                #save_reference(name, v)
                if v.id: #, 'Referenced element %s has no id' % v
                    buffer.write('<ref refid="%s"/>' % v.id)
            buffer.write('</reflist></%s>' % name)

    def save_value(name, value):
        """Save a value (attribute).
        If the value is a string, it is saves as a CDATA block.
        """
        if value is not None:
            buffer.write('<%s><val>' % name)
            if isinstance(value, types.StringTypes):
                buffer.write('<![CDATA[%s]]>' % value.replace(']]>', '] ]>'))
            elif isinstance(value, bool_):
                # Write booleans as 0/1.
                buffer.write(str(int(value)))
            else:
                buffer.write(escape(str(value)))
            buffer.write('</val></%s>\n' % name)

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
            buffer.write('<item id="%s" type="%s">' % (value.id, value.__class__.__name__))
            value.save(save_canvasitem)
            buffer.write('</item>')
        else:
            save_value(name, value)

    if not factory:
        factory = gaphor.resource(UML.ElementFactory)

    buffer = StringIO()
    buffer.write('<?xml version="1.0"?>\n')
    buffer.write('<gaphor version="%s" gaphor_version="%s">' % (FILE_FORMAT_VERSION, gaphor.resource('Version')))

    size = factory.size()
    n = 0
    for e in factory.values():
        clazz = e.__class__.__name__
        assert e.id
        buffer.write('<%s id="%s">' % (clazz, str(e.id)))
        e.save(save_element)
        buffer.write('</%s>' % clazz)
        n += 1
        if n % 25 == 0:
            yield (n * 100) / size

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


def load_elements(elements, factory, status_queue=None):
    for status in load_elements_coroutine(elements, factory):
        status_queue(status)

def load_elements_coroutine(elements, factory):
    """Load a file and create a model if possible.
    Exceptions: IOError, ValueError.
    """

    log.debug(_('Loading %d elements...') % len(elements))

    # The elements are iterated three times:
    size = len(elements) * 3
    def update_status_queue(_n=[0]):
        n = _n[0] = _n[0] + 1
        if n % 10 == 0:
	    return (n * 100) / size

    #log.info('0%')

    # First create elements and canvas items in the factory
    # The elements are stored as attribute 'element' on the parser objects:
    for id, elem in elements.items():
        yield update_status_queue()
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
            elem.element = diagram.create_as(cls, id)
        else:
            raise ValueError, 'Item with id "%s" and type %s can not be instantiated' % (id, type(elem))

    #log.info('0% ... 33%')

    # load attributes and create references:
    for id, elem in elements.items():
        yield update_status_queue()
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
            try:
                elem.element.load(name, value)
            except:
                log.error('Loading value %s (%s) for element %s failed.' % (name, value, elem.element))
                raise

        for name, refids in elem.references.items():
            if type(refids) == type([]):
                for refid in refids:
                    try:
                        ref = elements[refid]
                    except:
                        raise ValueError, 'Invalid ID for reference (%s) for element %s.%s' % (refid, elem.type, name)
                    else:
                        try:
                            elem.element.load(name, ref.element)
                        except:
                            log.error('Loading %s.%s with value %s failed' % (type(elem.element).__name__, name, ref.element.id))
                            raise
            else:
                try:
                    ref = elements[refids]
                except:
                    raise ValueError, 'Invalid ID for reference (%s)' % refids
                else:
                    try:
                        elem.element.load(name, ref.element)
                    except:
                        log.error('Loading %s.%s with value %s failed' % (type(elem.element).__name__, name, ref.element.id))
                        raise

                
    # do a postload:
    for id, elem in elements.items():
        yield update_status_queue()
        elem.element.postload()

    factory.notify_model()


def load(filename, factory=None, status_queue=None):
    '''Load a file and create a model if possible.
    Optionally, a status queue function can be given, to which the
    progress is written (as status_queue(progress)).
    Exceptions: GaphorError.
    '''
    log.info('Loading file %s' % os.path.basename(filename))
    try:
        elements = parser.parse(filename) #dom.parse (filename)
        if status_queue:
            status_queue(100)
    except Exception, e:
        print e
        log.error('File could no be parsed')
        raise

    try:
        if not factory:
            factory = gaphor.resource(UML.ElementFactory)
        factory.flush()
        gc.collect()
        load_elements(elements, factory, status_queue)
        gc.collect()
    except Exception, e:
        log.info('file %s could not be loaded' % filename)
        import traceback
        traceback.print_exc()
        raise
    
