#!/usr/bin/env python

# Copyright (C) 2002-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#                         syt <noreply@example.com>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Load and save Gaphor models to Gaphors own XML format.

Three functions are exported:
load(filename)
    load a model from a file
save(filename)
    store the current model in a file
"""

from __future__ import absolute_import
from __future__ import print_function

import gc
import os.path
from cStringIO import InputType

import gaphas
from six.moves import map

from gaphor import diagram
from gaphor.UML import uml2, modelfactory
from gaphor.UML.collection import collection
from gaphor.UML.elementfactory import ElementChangedEventBlocker
from gaphor.application import Application, NotInitializedError
from gaphor.diagram import items
from gaphor.i18n import _
from gaphor.storage import parser

__all__ = ['load', 'save']

FILE_FORMAT_VERSION = '3.0'
NAMESPACE_MODEL = 'http://gaphor.sourceforge.net/model'


def save(writer=None, factory=None, status_queue=None):
    for status in save_generator(writer, factory):
        if status_queue:
            status_queue(status)


def save_generator(writer, factory):
    """
    Save the current model using @writer, which is a
    gaphor.misc.xmlwriter.XMLWriter instance.
    """

    # Maintain a set of id's, one for elements, one for references.
    # Write only to file if references is a subset of elements

    def save_reference(name, value):
        """
        Save a value as a reference to another element in the model.
        This applies to both UML as well as canvas items.
        """
        # Save a reference to the object:
        if value.id:
            writer.startElement(name, {})
            writer.startElement('ref', {'refid': value.id})
            writer.endElement('ref')
            writer.endElement(name)

    def save_collection(name, value):
        """
        Save a list of references.
        """
        if len(value) > 0:
            writer.startElement(name, {})
            writer.startElement('reflist', {})
            for v in value:
                # save_reference(name, v)
                if v.id:
                    writer.startElement('ref', {'refid': v.id})
                    writer.endElement('ref')
            writer.endElement('reflist')
            writer.endElement(name)

    def save_value(name, value):
        """
        Save a value (attribute).
        """
        if value is not None:
            writer.startElement(name, {})
            writer.startElement('val', {})
            if isinstance(value, (str,)):
                writer.characters(value)
            elif isinstance(value, bool):
                # Write booleans as 0/1.
                writer.characters(str(int(value)))
            else:
                writer.characters(str(value))
            writer.endElement('val')
            writer.endElement(name)

    def save_element(name, value):
        """
        Save attributes and references from items in the gaphor.UML module.
        A value may be a primitive (string, int), a gaphor.UML.collection
        (which contains a list of references to other UML elements) or a
        gaphas.Canvas (which contains canvas items).
        """
        # log.debug('saving element: %s|%s %s' % (name, value, type(value)))
        if isinstance(value, (uml2.Element, gaphas.Item)):
            save_reference(name, value)
        elif isinstance(value, collection):
            save_collection(name, value)
        elif isinstance(value, gaphas.Canvas):
            writer.startElement('canvas', {})
            value.save(save_canvasitem)
            writer.endElement('canvas')
        else:
            save_value(name, value)

    def save_canvasitem(name, value, reference=False):
        """
        Save attributes and references in a gaphor.diagram.* object.
        The extra attribute reference can be used to force UML 
        """
        # log.debug('saving canvasitem: %s|%s %s' % (name, value, type(value)))
        if isinstance(value, collection) or \
                (isinstance(value, (list, tuple)) and reference):
            save_collection(name, value)
        elif reference:
            save_reference(name, value)
        elif isinstance(value, gaphas.Item):
            writer.startElement('item', {'id': value.id,
                                         'type': value.__class__.__name__})
            value.save(save_canvasitem)

            # save subitems
            for child in value.canvas.get_children(value):
                save_canvasitem(None, child)

            writer.endElement('item')

        elif isinstance(value, uml2.Element):
            save_reference(name, value)
        else:
            save_value(name, value)

    writer.startDocument()
    writer.startPrefixMapping('', NAMESPACE_MODEL)
    writer.startElementNS((NAMESPACE_MODEL, 'gaphor'), None,
                          {(NAMESPACE_MODEL, 'version'): FILE_FORMAT_VERSION,
                           (NAMESPACE_MODEL, 'gaphor-version'): Application.distribution.version})

    size = factory.size()
    n = 0
    for e in factory.values():
        clazz = e.__class__.__name__
        assert e.id
        writer.startElement(clazz, {'id': str(e.id)})
        e.save(save_element)
        writer.endElement(clazz)

        n += 1
        if n % 25 == 0:
            yield (n * 100) / size

    # writer.endElement('gaphor')
    writer.endElementNS((NAMESPACE_MODEL, 'gaphor'), None)
    writer.endPrefixMapping('')
    writer.endDocument()


def load_elements(elements, factory, status_queue=None):
    for status in load_elements_generator(elements, factory):
        if status_queue:
            status_queue(status)


def load_elements_generator(elements, factory, gaphor_version=None):
    """
    Load a file and create a model if possible.
    Exceptions: IOError, ValueError.
    """
    # TODO: restructure loading code, first load model, then add canvas items
    log.debug(_('Loading %d elements...') % len(elements))

    # The elements are iterated three times:
    size = len(elements) * 3

    def update_status_queue(_n=[0]):
        n = _n[0] = _n[0] + 1
        if n % 30 == 0:
            return (n * 100) / size

    # log.info('0%')

    # Fix version inconsistencies
    version_0_6_2(elements, factory, gaphor_version)
    version_0_7_2(elements, factory, gaphor_version)
    version_0_9_0(elements, factory, gaphor_version)
    version_0_14_0(elements, factory, gaphor_version)
    version_0_15_0_pre(elements, factory, gaphor_version)
    version_0_17_0(elements, factory, gaphor_version)

    # log.debug("Still have %d elements" % len(elements))

    # First create elements and canvas items in the factory
    # The elements are stored as attribute 'element' on the parser objects:

    def create_canvasitems(canvas, canvasitems, parent=None):
        """
        Canvas is a read gaphas.Canvas, items is a list of parser.canvasitem's
        """
        for item in canvasitems:
            cls = getattr(items, item.type)
            item.element = diagram.create_as(cls, item.id)
            canvas.add(item.element, parent=parent)
            assert canvas.get_parent(item.element) is parent
            create_canvasitems(canvas, item.canvasitems, parent=item.element)

    for id, elem in elements.items():
        st = update_status_queue()
        if st:
            yield st
        if isinstance(elem, parser.element):
            cls = getattr(uml2, elem.type)
            # log.debug('Creating UML element for %s (%s)' % (elem, elem.id))
            elem.element = factory.create_as(cls, id)
            if elem.canvas:
                elem.element.canvas.block_updates = True
                create_canvasitems(elem.element.canvas, elem.canvas.canvasitems)
        elif not isinstance(elem, parser.canvasitem):
            raise ValueError('Item with id "%s" and type %s can not be instantiated' % (id, type(elem)))

    # load attributes and create references:
    for id, elem in elements.items():
        st = update_status_queue()
        if st:
            yield st
        # Ensure that all elements have their element instance ready...
        assert hasattr(elem, 'element')

        # load attributes and references:
        for name, value in elem.values.items():
            try:
                elem.element.load(name, value)
            except:
                log.error('Loading value %s (%s) for element %s failed.' % (name, value, elem.element))
                raise

        for name, refids in elem.references.items():
            if type(refids) == list:
                for refid in refids:
                    try:
                        ref = elements[refid]
                    except:
                        raise ValueError('Invalid ID for reference (%s) for element %s.%s' % (refid, elem.type, name))
                    else:
                        try:
                            elem.element.load(name, ref.element)
                        except:
                            log.error('Loading %s.%s with value %s failed' % (
                                type(elem.element).__name__, name, ref.element.id))
                            raise
            else:
                try:
                    ref = elements[refids]
                except:
                    raise ValueError('Invalid ID for reference (%s)' % refids)
                else:
                    try:
                        elem.element.load(name, ref.element)
                    except:
                        log.error(
                            'Loading %s.%s with value %s failed' % (type(elem.element).__name__, name, ref.element.id))
                        raise

    # Fix version inconsistencies
    version_0_5_2(elements, factory, gaphor_version)
    version_0_7_1(elements, factory, gaphor_version)
    version_0_15_0_post(elements, factory, gaphor_version)

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

    for d in factory.select(lambda e: isinstance(e, uml2.Diagram)):
        # update_now() is implicitly called when lock is released
        d.canvas.block_updates = False

    # do a postload:
    for id, elem in elements.items():
        st = update_status_queue()
        if st:
            yield st
        elem.element.postload()

    factory.notify_model()


def load(filename, factory, status_queue=None):
    """
    Load a file and create a model if possible.
    Optionally, a status queue function can be given, to which the
    progress is written (as status_queue(progress)).
    """
    for status in load_generator(filename, factory):
        if status_queue:
            status_queue(status)


def load_generator(filename, factory):
    """
    Load a file and create a model if possible.
    This function is a generator. It will yield values from 0 to 100 (%)
    to indicate its progression.
    """
    if isinstance(filename, (file, InputType)):
        log.info('Loading file from file descriptor')
    else:
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
        # elements = parser.parse(filename)
        # yield 100
    except Exception as e:
        log.error('File could no be parsed', exc_info=True)
        raise

    try:
        component_registry = Application.get_service('component_registry')
    except NotInitializedError:
        component_registry = None

    try:
        factory.flush()
        gc.collect()
        log.info("Read %d elements from file" % len(elements))
        if component_registry:
            component_registry.register_subscription_adapter(ElementChangedEventBlocker)
        try:
            for percentage in load_elements_generator(elements, factory, gaphor_version):
                if percentage:
                    yield percentage / 2 + 50
                else:
                    yield percentage
        except Exception as e:
            raise
        finally:
            if component_registry:
                component_registry.unregister_subscription_adapter(ElementChangedEventBlocker)

        gc.collect()
        yield 100
    except Exception as e:
        log.info('file %s could not be loaded' % filename)
        raise


def version_lower_than(gaphor_version, version):
    """
    if version_lower_than('0.3.0', (0, 15, 0)):
       ...
    """
    parts = gaphor_version.split('.')
    try:
        return tuple(map(int, parts)) < version
    except ValueError:
        # We're having a -dev, -pre, -beta, -alpha or whatever version
        parts = parts[:-1]
        return tuple(map(int, parts)) <= version


def version_0_15_0_pre(elements, factory, gaphor_version):
    """
    Fix association navigability UML metamodel to comply with UML 2.2
    using Association.navigableOwnedEnd among others (see model factory
    for details).

    Convert tagged values into comment items as tagged values are no longer
    supported by UML specification (stereotypes attributes shall be used
    instead). Comment item contains information about used tagged values.
    It means, that full conversion of tagged values into stereotype
    attributes is not supported at the moment.

    This function is called before the actual elements are constructed.
    """
    ATTRS = set(['class_', 'interface_', 'actor', 'useCase', 'owningAssociation'])
    if version_lower_than(gaphor_version, (0, 14, 99)):
        # update associations
        values = (v for v in elements.values()
                  if type(v) is parser.element
                  and v.type == 'Property'
                  and 'association' in v.references)
        for et in values:
            # get association
            assoc = elements[et.references['association']]

            attrs = set(set(ATTRS) & set(et.references))
            if attrs:
                assert len(attrs) == 1

                attr = attrs.pop()

                if attr == 'owningAssociation':
                    assoc.references['ownedEnd'].remove(et.id)
                    if not assoc.references['ownedEnd']:
                        del assoc.references['ownedEnd']
                elif attr in ('actor', 'useCase'):
                    if 'navigableOwnedEnd' not in assoc.references:
                        assoc.references['navigableOwnedEnd'] = []
                    assoc.references['navigableOwnedEnd'].append(et.id)

                    el = elements[et.references[attr]]
                    el.references['ownedAttribute'].remove(et.id)
                    if not el.references['ownedAttribute']:
                        del el.references['ownedAttribute']

                del et.references[attr]
            else:
                if 'ownedEnd' not in assoc.references:
                    assoc.references['ownedEnd'] = []
                assoc.references['ownedEnd'].append(et.id)

        # - get rid of tagged values
        for e in elements.values():
            if 'taggedValue' in e.references:
                taggedvalue = [elements[i].values['value'] for i in e.references['taggedValue'] if
                               elements[i].values.get('value')]
                # convert_tagged_value(e, elements, factory)
                if taggedvalue:
                    e.taggedvalue = taggedvalue

                # Remove obsolete elements
                for t in e.references['taggedValue']:
                    del elements[t]
                del e.references['taggedValue']

        # - rename EventOccurrence to MessageOccurrenceSpecification
        values = (v for v in elements.values()
                  if type(v) is parser.element
                  and v.type == 'EventOccurrence')
        for et in values:
            et.type = 'MessageOccurrenceSpecification'


def version_0_15_0_post(elements, factory, gaphor_version):
    """
    Part two: create stereotypes and what more for the elements that have a
    taggedvalue property.
    """

    def update_elements(element):
        e = elements[element.id] = parser.element(element.id, element.__class__.__name__)
        e.element = element

    if version_lower_than(gaphor_version, (0, 14, 99)):
        stereotypes = {}
        profile = None
        for e in elements.values():
            if hasattr(e, 'taggedvalue'):
                if not profile:
                    profile = factory.create(uml2.Profile)
                    profile.name = 'version 0.15 conversion'
                    update_elements(profile)
                st = stereotypes.get(e.type)
                if not st:
                    st = stereotypes[e.type] = factory.create(uml2.Stereotype)
                    st.name = 'Tagged'
                    st.package = profile
                    update_elements(st)
                    cl = factory.create(uml2.Class)
                    cl.name = str(e.type)
                    cl.package = profile
                    update_elements(cl)
                    ext = modelfactory.extend_with_stereotype(factory, cl, st)
                    update_elements(ext)
                    for me in ext.memberEnd:
                        update_elements(me)
                # Create instance specification for the stereotype:
                instspec = modelfactory.apply_stereotype(factory, e.element, st)
                update_elements(instspec)

                def create_slot(key, val):
                    for attr in st.ownedAttribute:
                        if attr.name == key:
                            break
                    else:
                        attr = st.ownedAttribute = factory.create(uml2.Property)
                        attr.name = str(key)
                        update_elements(attr)
                    slot = modelfactory.add_slot(factory, instspec, attr)
                    slot.value.value = str(val)
                    update_elements(slot)

                tviter = iter(e.taggedvalue or [])
                for tv in tviter:
                    try:
                        try:
                            key, val = tv.split('=', 1)
                            key = key.strip()
                        except ValueError:
                            log.info('Tagged value "%s" has no key=value format, trying key_value ' % tv)
                            try:
                                key, val = tv.split(' ', 1)
                                key = key.strip()
                            except ValueError:
                                # Fallback, deal with it as if it were a boolean
                                key = tv.strip()
                                val = 'true'

                            # This syntax is used with the uml2 meta model:
                            if key in ('subsets', 'redefines'):
                                rest = ', '.join(tviter)
                                val = ', '.join([val, rest]) if rest else val
                                val = val.replace('\n', ' ')
                                log.info('Special case: UML metamodel "%s %s"' % (key, val))
                        create_slot(key, val)
                    except Exception as e:
                        log.warning('Unable to process tagged value "%s" as key=value pair' % tv, exc_info=True)

        def find(messages, attr):
            occurrences = set(getattr(m, attr) for m in messages
                              if hasattr(m, attr) and getattr(m, attr))
            assert len(occurrences) <= 1
            if occurrences:
                return occurrences.pop()
            else:
                return None

        def update_msg(msg, sl, rl):
            if sl:
                s = factory.create(uml2.MessageOccurrenceSpecification)
                s.covered = sl
                m.sendEvent = s
            if rl:
                r = factory.create(uml2.MessageOccurrenceSpecification)
                r.covered = rl
                m.receiveEvent = r

        for e in elements.values():
            if e.type == 'MessageItem':
                msg = e.element
                send = msg.subject.sendEvent
                receive = msg.subject.receiveEvent

                if not send:
                    send = find(list(msg._messages.keys()), 'sendEvent')
                if not receive:
                    receive = find(list(msg._messages.keys()), 'receiveEvent')
                if not send:
                    send = find(list(msg._inverted_messages.keys()), 'reveiveEvent')
                if not receive:
                    receive = find(list(msg._inverted_messages.keys()), 'sendEvent')

                sl = send.covered if send else None
                rl = receive.covered if receive else None

                for m in msg._messages:
                    update_msg(m, sl, rl)
                for m in msg._inverted_messages:
                    update_msg(m, rl, sl)
                msg.subject.sendEvent = send
                msg.subject.receiveEvent = receive


def convert_tagged_value(element, elements, factory):
    """
    Convert ``element.taggedValue`` to something supported by the
    UML 2.2 model (since Gaphor version 0.15).

    For each item having a Tagged value a Stereotype is linked. This is done
    like this:

      item -> InstanceSpecification -> Stereotype

    Each tagged value will be replaced by a Slot:

      item -> InstanceSpecification -> Slot -> Attribute -> Stereotype
    """
    import uuid
    diagrams = [e for e in elements.values() if e.type == 'Diagram']

    presentation = element.get('presentation') or []
    tv = [elements[i] for i in element.references['taggedValue']]
    for et in presentation:
        et = elements[et]
        m = eval(et.values['matrix'])
        w = eval(et.values['width'])

        tagged = 'upgrade to stereotype attributes' \
                 ' following tagged values:\n%s' % '\n'.join(t.values['value'] for t in tv)

        item = parser.canvasitem(str(uuid.uuid1()), 'CommentItem')
        comment = parser.element(str(uuid.uuid1()), 'Comment')

        item.references['subject'] = comment.id
        item.values['matrix'] = str((1.0, 0.0, 0.0, 1.0, m[4] + w + 10.0, m[5]))

        comment.references['presentation'] = [item.id]
        comment.values['body'] = tagged

        elements[item.id] = item
        elements[comment.id] = comment

        # Where to place the comment? How to find the Diagram?
        for d in diagrams:
            for ci in d.canvas.canvasitems:
                if ci.id == et.id:
                    d.canvas.canvasitems.append(item)
                    break


def version_0_17_0(elements, factory, gaphor_version):
    """
    As of version 0.17.0, ValueSpecification and subclasses is dealt
    with as if it were attributes.

    This function is called before the actual elements are constructed.
    """
    valspec_types = ['ValueSpecification', 'OpaqueExpression', 'Expression',
                     'InstanceValue', 'LiteralSpecification', 'LiteralUnlimitedNatural',
                     'LiteralInteger', 'LiteralString', 'LiteralBoolean', 'LiteralNull']

    print('version', gaphor_version)
    if version_lower_than(gaphor_version, (0, 17, 0)):
        valspecs = dict((v.id, v) for v in elements.values() if v.type in valspec_types)

        for id in valspecs.keys():
            del elements[id]

        for e in elements.values():
            for name, ref in list(e.references.items()):
                # ValueSpecifications are always defined in 1:1 relationships
                if type(ref) != list and ref in valspecs:
                    del e.references[name]
                    assert name not in e.values
                    try:
                        e.values[name] = valspecs[ref].values['value']
                    except KeyError:
                        pass  # Empty LiteralSpecification


def version_0_14_0(elements, factory, gaphor_version):
    """
    Fix applied stereotypes UML metamodel. Before Gaphor 0.14.0 applied
    stereotypes was a collection of stereotypes classes, but now the list
    needs to be replaced with collection of stereotypes instances.

    This function is called before the actual elements are constructed.
    """
    import uuid
    if version_lower_than(gaphor_version, (0, 14, 0)):
        values = (v for v in elements.values() if type(v) is parser.element)
        for et in values:
            try:
                if 'appliedStereotype' in et.references:
                    data = tuple(et.references['appliedStereotype'])
                    applied = []
                    # collect stereotypes instances in `applied` list
                    for refid in data:
                        st = elements[refid]
                        obj = parser.element(str(uuid.uuid1()),
                                             'InstanceSpecification')
                        obj.references['classifier'] = [st.id]
                        elements[obj.id] = obj
                        applied.append(obj.id)

                        assert obj.id in applied and obj.id in elements

                    # replace stereotypes with their instances
                    assert len(applied) == len(data)
                    et.references['appliedStereotype'] = applied

            except Exception as e:
                log.error('Error while updating stereotypes', exc_info=True)


def version_0_9_0(elements, factory, gaphor_version):
    """
    Before 0.9.0, we used DiaCanvas2 as diagram widget in the GUI. As of 0.9.0
    Gaphas was introduced. Some properties of <item /> elements have changed,
    renamed or been removed at all.

    This function is called before the actual elements are constructed.
    """
    if version_lower_than(gaphor_version, (0, 9, 0)):
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

            except Exception as e:
                log.error('Error while updating from DiaCanvas2', exc_info=True)


def version_0_7_2(elements, factory, gaphor_version):
    """
    Before 0.7.2, only Property and Parameter elements had taggedValues.
    Since 0.7.2 all NamedElements are able to have taggedValues. However,
    the multiplicity of taggedValue has changed from 0..1 to *, so all elements
    should be converted to a list.
    """
    import uuid

    if version_lower_than(gaphor_version, (0, 7, 2)):
        for elem in elements.values():
            try:
                if type(elem) is parser.element \
                        and elem.type in ('Property', 'Parameter') \
                        and elem.taggedValue:
                    tvlist = []
                    tv = elements[elem.taggedValue]
                    if tv.value:
                        for t in map(str.strip, str(tv.value).split(',')):
                            # log.debug("Tagged value: %s" % t)
                            newtv = parser.element(str(uuid.uuid1()),
                                                   'LiteralSpecification')
                            newtv.values['value'] = t
                            elements[newtv.id] = newtv
                            tvlist.append(newtv.id)
                        elem.references['taggedValue'] = tvlist
            except Exception as e:
                log.error('Error while updating taggedValues', exc_info=True)


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
        if isinstance(end2.type, uml2.Interface):
            type = end1.interface_
        else:  # isinstance(end2.type, uml2.Class):
            type = end1.class_

        # if the end of association is not navigable (in terms of UML 1.x)
        # then set navigability to unknown (in terms of UML 2.0)
        if not (type and end1 in type.ownedAttribute):
            del end1.owningAssociation

    if version_lower_than(gaphor_version, (0, 7, 1)):
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
            except Exception as e:
                log.error('Error while updating Association', exc_info=True)


def version_0_6_2(elements, factory, gaphor_version):
    """
    Before 0.6.2 an Interface could be represented by a ClassItem and
    a InterfaceItem. Now only InterfaceItems are used.
    """
    if version_lower_than(gaphor_version, (0, 6, 2)):
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
            except Exception as e:
                log.error('Error while updating InterfaceItems', exc_info=True)


def version_0_5_2(elements, factory, gaphor_version):
    """
    Before version 0.5.2, the wrong memberEnd of the association was
    holding the aggregation information.
    """
    if version_lower_than(gaphor_version, (0, 5, 2)):
        log.info('Fix composition on Associations (file version: %s)' % gaphor_version)
        for elem in elements.values():
            try:
                if elem.type == 'Association':
                    a = elem.element
                    agg1 = a.memberEnd[0].aggregation
                    agg2 = a.memberEnd[1].aggregation
                    a.memberEnd[0].aggregation = agg2
                    a.memberEnd[1].aggregation = agg1
            except Exception as e:
                log.error('Error while updating Association', exc_info=True)

# vim: sw=4:et:ai
