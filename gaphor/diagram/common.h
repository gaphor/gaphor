/* common.h
 * Copyright (C) 2002  Arjan Molenaar
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

#ifndef __COMMON_H__
#define __COMMON_H__

#include <Python.h>
#include <diacanvas/dia-canvas.h>
#include <diacanvas/dia-shape.h>
#include <pygobject.h>

#define STEREOTYPE_OPEN = "«"
#define STEREOTYPE_CLOSE = "»"

/* Loaded in diagramitemsmodule.c: */
extern PyObject *UML_module;

#define TYPE_PYOBJECT  (pyobject_get_type ())

GType pyobject_get_type (void);

/*
 * Methods for model element <-> diagram item connection.
 */

void subject_add_presentation (PyObject *subject, PyObject *item);
void subject_remove_presentation (PyObject *subject, PyObject *item);
void subject_remove_presentation_undoable (PyObject *subject, PyObject *item);
void subject_undo_presentation (PyObject *subject, PyObject *item);
void subject_add_undoability (PyObject *subject);
void subject_remove_undoability (PyObject *subject);

/* Connect and disconnect the element_update callback function. */
void subject_connect_element_update (PyObject *subject, PyObject *item);
void subject_disconnect_element_update (PyObject *subject, PyObject *item);

#define APPEND_SHAPE(item, stype) \
	DIA_CANVAS_ITEM(item)->shapes = g_list_append (DIA_CANVAS_ITEM(item)->shapes, dia_shape_new (stype))

/**
 * handle_key_event: 
 * @item: Item that recieved the key press event.
 * @event: The actual event.
 * @text: Text to edit.
 * @text_shape: Shape used to represent the text, needed for up/down navigation.
 * @cursor_index: INOUT Index of the cursor, this will change if a cursor key
 * 		  is pressed.
 *
 * This is a common handler for key events. Basic things like moving around
 * and adding/removing text are handled here.
 *
 * Returns: TRUE if the event is handled, FALSE otherwise.
 **/
gboolean handle_key_event (DiaCanvasItem *item,
			   DiaEventKey *event,
			   GString *text,
			   DiaShape *text_shape,
			   gint *cursor_index);

/**
 * Do key handling for a string provided by a diagram items subject.
 **/
gboolean handle_key_event_for_subject (DiaCanvasItem *item,
				       DiaEventKey *event,
				       PyObject *subject,
				       const gchar *attr_name,
				       DiaShape *text_shape,
				       gint *cursor_index);

const gchar* subject_get_string (PyObject *subject, const gchar* name);

/* _set_subject() and _unset_subject() should be used to set and unset
 * the subject. Those functions will add themselves to the subject.presentation
 * as weak references. The subject will be referenced by 'item', so it will
 * stay alive.
 */
void _set_subject (DiaCanvasItem *item, PyObject *subject,
		   PyObject **item_subject);

void _unset_subject (DiaCanvasItem *item, PyObject **item_subject);

PyObject *create_uml_object (const gchar *name);

#endif /* __COMMON_H__ */
