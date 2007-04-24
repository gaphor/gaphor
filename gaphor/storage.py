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
import sys
import os.path
import gc

import gaphas

from gaphor import UML
from gaphor import parser
from gaphor import diagram
from gaphor.application import Application
from gaphor.diagram import items
from gaphor.i18n import _
#from gaphor.misc.xmlwriter import XMLWriter

__all__ = [ 'load', 'save' ]

FILE_FORMAT_VERSION = '3.0'

def save(writer=None, factory=None, status_queue=None):
    for status in save_generator(writer, factory):
        if status_queue:
            status_queue(status)

def save_generator(writer, factory):
    """Save the current model using @writer, which is a
    gaphor.misc.xmlwriter.XMLWriter instance (or at least a SAX serializer
    with CDATA support).
    """
    # Make bool work for Python 2.2
    bool_ = type(bool(0))

    def save_reference(name, value):
        """Save a value as a reference to another element in the model.
        This applies to both UML as well as canvas items.
        """
        # Save a reference to the object:
        if value.id: #, 'Referenced element %s has no id' % value
            writer.startElement(name, {})
            writer.startElement('ref', { 'refid': value.id })
            writer.endElement('ref')
            writer.endElement(name)

    def save_collection(name, value):
        """Save a list of references.
        """
        if len(value) > 0:
            writer.startElement(name, {})
            writer.startElement('reflist', {})
            for v in value:
                #save_reference(name, v)
                if v.id: #, 'Referenced element %s has no id' % v
                    writer.startElement('ref', { 'refid': v.id })
                    writer.endElement('ref')
            writer.endElement('reflist')
            writer.endElement(name)

    def save_value(name, value):
        """Save a value (attribute).
        If the value is a string, it is saves as a CDATA block.
        """
        if value is not None:
            writer.startElement(name, {})
            writer.startElement('val', {})
            if isinstance(value, types.StringTypes):
                writer.startCDATA()
                writer.characters(value)
                writer.endCDATA()
            elif isinstance(value, bool_):
                # Write booleans as 0/1.
                writer.characters(str(int(value)))
            else:
                writer.characters(str(value))
            writer.endElement('val')
            writer.endElement(name)

    def save_element(name, value):
        """Save attributes and references from items in the gaphor.UML module.
        A value may be a primitive (string, int), a gaphor.UML.collection
        (which contains a list of references to other UML elements) or a
        gaphas.Canvas (which contains canvas items).
        """
        #log.debug('saving element: %s|%s %s' % (name, value, type(value)))
        if isinstance (value, (UML.Element, gaphas.Item)):
            save_reference(name, value)
        elif isinstance(value, UML.collection):
            save_collection(name, value)
        elif isinstance(value, gaphas.Canvas):
            writer.startElement('canvas', {})
            value.save(save_canvasitem)
            writer.endElement('canvas')
        else:
            save_value(name, value)

    def save_canvasitem(name, value, reference=False):
        """Save attributes and references in a gaphor.diagram.* object.
        The extra attribute reference can be used to force UML 
        """
        #log.debug('saving canvasitem: %s|%s %s' % (name, value, type(value)))
        if reference:
            save_reference(name, value)
        elif isinstance(value, UML.collection):
            save_collection(name, value)
        elif isinstance(value, gaphas.Item):
            writer.startElement('item', { 'id': value.id,
                                          'type': value.__class__.__name__ })
            value.save(save_canvasitem)
            writer.endElement('item')
        elif isinstance(value, UML.Element):
            save_reference(name, value)
        else:
            save_value(name, value)

    writer.startDocument()
    writer.startElement('gaphor', { 'version': FILE_FORMAT_VERSION,
                                    'gaphor-version': Application.distribution.version })

    size = factory.size()
    n = 0
    for e in factory.values():
        clazz = e.__class__.__name__
        assert e.id
        writer.startElement(clazz, { 'id': str(e.id) })
        e.save(save_element)
        writer.endElement(clazz)
        n += 1
        if n % 25 == 0:
            yield (n * 100) / size

    writer.endElement('gaphor')
    writer.endDocument()


def load_elements(elements, factory, status_queue=None):
    for status in load_elements_generator(elements, factory):
        if status_queue:
            status_queue(status)

def load_elements_generator(elements, factory, gaphor_version=None):
    """Load a file and create a model if possible.
    Exceptions: IOError, ValueError.
    """
    # TODO: restructure loading code, first load model, then add canvas items
    log.debug(_('Loading %d elements...') % len(elements))

    # The elements are iterated three times:
    size = len(elements) * 3
    def update_status_queue(_n=[0]):
        n = _n[0] = _n[0] + 1
        if n % 10 == 0:
            return (n * 100) / size

    #log.info('0%')

    # Fix version inconsistencies
    version_0_6_2(elements, factory, gaphor_version)
    version_0_7_2(elements, factory, gaphor_version)
    version_0_9_0(elements, factory, gaphor_version)

    #log.debug("Still have %d elements" % len(elements))

    # First create elements and canvas items in the factory
    # The elements are stored as attribute 'element' on the parser objects:
    for id, elem in elements.items():
        yield update_status_queue()
        if isinstance(elem, parser.element):
            cls = getattr(UML, elem.type)
            #log.debug('Creating UML element for %s (%s)' % (elem, elem.id))
            elem.element = factory.create_as(cls, id)
            if elem.canvas:
                elem.element.canvas.block_updates = True
        elif isinstance(elem, parser.canvasitem):
            cls = getattr(items, elem.type)
            #log.debug('Creating canvas item for %s (%s)' % (elem, elem.id))
            elem.element = diagram.create_as(cls, id)
        else:
            raise ValueError, 'Item with id "%s" and type %s can not be instantiated' % (id, type(elem))

    #log.info('0% ... 33%')

    #log.debug("Still have %d elements" % len(elements))

    # load attributes and create references:
    for id, elem in elements.items():
        yield update_status_queue()
        # Ensure that all elements have their element instance ready...
        assert hasattr(elem, 'element')

        # establish parent/child relations on canvas items:
        if isinstance(elem, parser.element) and elem.canvas:
            for item in elem.canvas.canvasitems:
                assert item in elements.values(), 'Item %s (%s) is a canvas item, but it is not in the parsed objects table' % (item, item.id)
                elem.element.canvas.add(item.element)

        # Also create nested canvas items:
        if isinstance(elem, parser.canvasitem):
            for item in elem.canvasitems:
                assert item in elements.values(), 'Item %s (%s) is a canvas item, but it is not in the parsed objects table' % (item, item.id)
                elem.element.canvas.add(item.element, parent=elem.element)

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

    # Fix version inconsistencies
    version_0_5_2(elements, factory, gaphor_version)
    version_0_7_1(elements, factory, gaphor_version)

    # Before version 0.7.2 there was only decision node (no merge nodes).
    # This node could have many incoming and outgoing flows (edges).
    # According to UML specification decision node has no more than one
    # incoming node.
    #
    # Now, we have implemented merge node, which can have many incoming
    # flows. We also support combining of decision and merge nodes as
    # described in UML specification.
    #
    # Data model, loaded from file, is updated automatically, so there is
    # no need for special function.

    # do a postload:
    for id, elem in elements.items():
        yield update_status_queue()
        elem.element.postload()

    # Unlock canvas's for updates
    for id, elem in elements.items():
        if isinstance(elem, parser.element) and elem.canvas:
            elem.element.canvas.block_updates = False

    factory.notify_model()


def load(filename, factory, status_queue=None):
    """Load a file and create a model if possible.
    Optionally, a status queue function can be given, to which the
    progress is written (as status_queue(progress)).
    Exceptions: GaphorError.
    """
    for status in load_generator(filename, factory):
        if status_queue:
            status_queue(status)

def load_generator(filename, factory):
    """Load a file and create a model if possible.
    This function is a generator. It will yield values from 0 to 100 (%)
    to indicate its progression.

    Exceptions: GaphorError.
    """
    log.info('Loading file %s' % os.path.basename(filename))
    try:
        # Use the incremental parser and yield the percentage of the file.
        loader = parser.GaphorLoader()
        for percentage in parser.parse_generator(filename, loader):
            pass
            if percentage:
                yield percentage / 2
            else:
                yield percentage
        elements = loader.elements
        gaphor_version = loader.gaphor_version
        #elements = parser.parse(filename)
        #yield 100
    except Exception, e:
        log.error('File could no be parsed', e)
        raise

    try:
        factory.flush()
        gc.collect()
        log.info("Read %d elements from file" % len(elements))
        for percentage in load_elements_generator(elements, factory, gaphor_version):
            pass
            if percentage:
                yield percentage / 2 + 50
            else:
                yield percentage
        gc.collect()
        yield 100
    except Exception, e:
        log.info('file %s could not be loaded' % filename, e)
        raise


def version_0_9_0(elements, factory, gaphor_version):
    """
    Before 0.9.0, we used DiaCanvas2 as diagram widget in the GUI. As of 0.9.0
    Gaphas was introduced. Some properties of <item /> elements have changed,
    renamed or been removed at all.

    This function is called before the actual elements are constructed.
    """
    if tuple(map(int, gaphor_version.split('.'))) < (0, 9, 0):
        for elem in elements.values():
            try:
                if type(elem) is parser.canvasitem:
                    # Rename affine to matrix
                    if elem.values.get('affine'):
                        elem.values['matrix'] = elem.values['affine']
                        del elem.values['affine']
                    # No more 'color' attribute:
                    if elem.values.get('color'):
                        del elem.values['color']

            except Exception, e:
                log.error('Error while updating taggedValues', e)

def version_0_7_2(elements, factory, gaphor_version):
    """
    Before 0.7.2, only Property and Parameter elements had taggedValues.
    Since 0.7.2 all NamedElements are able to have taggedValues. However,
    the multiplicity of taggedValue has changed from 0..1 to *, so all elements
    should be converted to a list.
    """
    from gaphor.misc.uniqueid import generate_id

    if tuple(map(int, gaphor_version.split('.'))) < (0, 7, 2):
        for elem in elements.values():
            try:
                if type(elem) is parser.element \
                   and elem.type in ('Property', 'Parameter') \
                   and elem.taggedValue:
                    tvlist = []
                    tv = elements[elem.taggedValue]
                    if tv.value:
                        for t in map(str.strip, str(tv.value).split(',')):
                            #log.debug("Tagged value: %s" % t)
                            newtv = parser.element(generate_id(),
                                                   'LiteralSpecification')
                            newtv.values['value'] = t
                            elements[newtv.id] = newtv
                            tvlist.append(newtv.id)
                        elem.references['taggedValue'] = tvlist
            except Exception, e:
                log.error('Error while updating taggedValues', e)


def version_0_7_1(elements, factory, gaphor_version):
    """
    Before version 0.7.1, there were two states for association
    navigability (in terms of UML 2.0): unknown and navigable.
    In case of unknown navigability Property.owningAssociation was set.

    Now, we have three states: unknown, non-navigable and navigable.
    In case of unknown navigability the Property.owningAssociation
    should not be set.
    """
    def fix(end1, end2):
        if isinstance(end2.type, UML.Interface):
            type = end1.interface_
        else: # isinstance(end2.type, UML.Class):
            type = end1.class_

        # if the end of association is not navigable (in terms of UML 1.x)
        # then set navigability to unknown (in terms of UML 2.0)
        if not (type and end1 in type.ownedAttribute):
            del end1.owningAssociation

    if tuple(map(int, gaphor_version.split('.'))) < (0, 7, 1):
        log.info('Fix navigability of Associations (file version: %s)' % gaphor_version)
        for elem in elements.values():
            try:
                if elem.type == 'Association':
                    asc = elem.element
                    end1 = asc.memberEnd[0]
                    end2 = asc.memberEnd[1]
                    if end1 and end2:
                        fix(end1, end2)
                        fix(end2, end1)
            except Exception, e:
                log.error('Error while updating Association', e)


def version_0_6_2(elements, factory, gaphor_version):
    """
    Before 0.6.2 an Interface could be represented by a ClassItem and
    a InterfaceItem. Now only InterfaceItems are used.
    """
    if tuple(map(int, gaphor_version.split('.'))) < (0, 6, 2):
        for elem in elements.values():
            try:
                if type(elem) is parser.element and elem.type == 'Interface':
                    for p_id in elem.presentation:
                        p = elements[p_id]
                        if p.type == 'ClassItem':
                            p.type = 'InterfaceItem'
                            p.values['drawing-style'] = '0'
                        elif p.type == 'InterfaceItem':
                            p.values['drawing-style'] = '2'
            except Exception, e:
                log.error('Error while updating InterfaceItems', e)


def version_0_5_2(elements, factory, gaphor_version):
    """
    Before version 0.5.2, the wrong memberEnd of the association was
    holding the aggregation information.
    """
    if tuple(map(int, gaphor_version.split('.'))) < (0, 5, 2):
        log.info('Fix composition on Associations (file version: %s)' % gaphor_version)
        for elem in elements.values():
            try:
                if elem.type == 'Association':
                    a = elem.element
                    agg1 = a.memberEnd[0].aggregation
                    agg2 = a.memberEnd[1].aggregation
                    a.memberEnd[0].aggregation = agg2
                    a.memberEnd[1].aggregation = agg1
            except Exception, e:
                log.error('Error while updating Association', e)

