/*
 * Some common functions.
 *
 * This is GPL'ed code.
 */

#include "common.h"
#include "model-element.h"
#include <diacanvas/dia-canvas-i18n.h>
#include <gdk/gdkkeysyms.h>


static gint
move_cursor_vertical (DiaShape *shape, gint cursor_index, gint direction)
{
	gint linenr = -1;
	GSList *sl;
	PangoLayout *layout = dia_shape_text_to_pango_layout (shape, TRUE);
	PangoLayoutLine *line;
	gint x, index, trailing;

	for (sl = pango_layout_get_lines (layout); sl != NULL; sl = sl->next) {
		line = sl->data;
		if (line->start_index > cursor_index)
			break;
		linenr++;
	}

	line = pango_layout_get_line (layout, linenr);
	if (!line)
		return cursor_index;

	pango_layout_line_index_to_x (line, cursor_index, FALSE, &x);

	linenr += direction;
	if (linenr < 0)
		return cursor_index;

	line = pango_layout_get_line (layout, linenr);
	if (!line)
		return cursor_index;

	pango_layout_line_x_to_index (line, x, &index, &trailing);

	g_object_unref (layout);

	return index + trailing;
}

#define COMMON_MODEL_ELEMENT_SPECIFIC \
	if (IS_MODEL_ELEMENT(item) && MODEL_ELEMENT(item)->auto_resize) \
		MODEL_ELEMENT(item)->need_resize = TRUE;

gboolean
handle_key_event (DiaCanvasItem *item, DiaEventKey *event,
		  GString *str, DiaShape *text_shape, gint *cursor_index)
{
	gboolean result = FALSE;

	switch (event->keyval) {
	case GDK_BackSpace:
		if (*cursor_index > 0) {
			(*cursor_index)--;
			g_string_erase (str, *cursor_index, 1);
		}
		dia_canvas_item_request_update (item);
		COMMON_MODEL_ELEMENT_SPECIFIC;
		result = TRUE;
		break;
	case GDK_Delete:
	case GDK_KP_Delete:
		if (*cursor_index < str->len)
			g_string_erase (str, *cursor_index, 1);
		dia_canvas_item_request_update (item);
		COMMON_MODEL_ELEMENT_SPECIFIC;
		result = TRUE;
		break;
	case GDK_Left:
	case GDK_KP_Left:
		if (*cursor_index > 0)
			(*cursor_index)--;
		dia_canvas_item_request_update (item);
		result = TRUE;
		break;
	case GDK_Right:
	case GDK_KP_Right:
		if (*cursor_index < str->len)
			(*cursor_index)++;
		dia_canvas_item_request_update (item);
		result = TRUE;
		break;
	case GDK_Up:
	case GDK_KP_Up:
		*cursor_index = move_cursor_vertical (text_shape,
						      *cursor_index, -1);
		dia_canvas_item_request_update (item);
		result = TRUE;
		break;
	case GDK_Down:
	case GDK_KP_Down:
		*cursor_index = move_cursor_vertical (text_shape,
						      *cursor_index, +1);
		dia_canvas_item_request_update (item);
		result = TRUE;
		break;
	case GDK_KP_Enter:
	case GDK_Return:
		g_string_insert_c (str, (*cursor_index)++, '\n');
		dia_canvas_item_request_update (item);
		result = TRUE;
		COMMON_MODEL_ELEMENT_SPECIFIC;
		break;
	default:
		if (event->length > 0 && event->string[0] >= ' ') {
			g_string_insert_len (str,
					     (*cursor_index)++,
					     event->string,
					     event->length);
			dia_canvas_item_request_update (item);
			result = TRUE;
			COMMON_MODEL_ELEMENT_SPECIFIC;
		}
	}
	return result;
}

gboolean
handle_key_event_for_subject (DiaCanvasItem *item, DiaEventKey *event,
			      PyObject *subject, const gchar *attr_name,
			      DiaShape *text_shape, gint *cursor_index)
{
	PyObject *str_obj;
	GString *str;
	gboolean result;

	str_obj = PyObject_GetAttrString (subject, (char*) attr_name);
	if (str_obj && PyString_Check (str_obj))
		str = g_string_new (PyString_AsString (str_obj));
	else
		str = g_string_new (NULL);

	Py_XDECREF (str_obj);
	
	result = handle_key_event (item, event, str, text_shape, cursor_index);

	if (result) {
		/* Store undo information: */
		dia_canvas_item_preserve_property (item, attr_name);
		
		//dia_shape_text_set_text (text_shape, str->str);
		str_obj = PyString_FromStringAndSize (str->str, str->len);
		PyObject_SetAttrString (subject, (char*) attr_name, str_obj);
		Py_DECREF (str_obj);
	}
	g_string_free (str, TRUE);

	return result;
}


PyObject*
new_uml_object (gchar *type)
{
	PyObject *type_obj, *obj;

	type_obj = PyObject_GetAttrString (UML_module, type);
	obj = PyObject_CallObject (type_obj, NULL);
	Py_DECREF(type_obj);

	return obj;
}


const gchar*
subject_get_string (PyObject *subject, const gchar* name)
{
	PyObject *pystr;
	gchar *str = NULL;
	pystr = PyObject_GetAttrString (subject, (char*) name);
	if (pystr && PyString_Check (pystr)) {
		str = PyString_AsString (pystr);
		//g_message (__FUNCTION__": pystr->ob_refcnt = %d", pystr->ob_refcnt);
		Py_DECREF (pystr);
	} else {
		PyErr_Print();
		PyErr_Clear();
	}
	return str;
}

/* _set_subject() and _unset_subject():
 *
 * These function do a bit of evil wizardry... 
 * The diagram item ('item') can not be garbage collected. It will own
 * a reference to the model element though... The model element may only
 * be removed if (all) the diagram item(s) are removed. The diagram items
 * however, should free themselves as soon as the the diagram window
 * gets destroyed. This can not be done if the model elements own references
 * to the diagram items. This 'trick' is somewhat cheaper that using weak-ref
 * objects, but the effect is the same.
 */
void
_set_subject (DiaCanvasItem *item, PyObject *subject, PyObject **item_subject)
{
	PyObject *wrapper;
	PyObject *element_update;
	PyObject *result;

	g_return_if_fail (DIA_IS_CANVAS_ITEM (item));
	g_return_if_fail (subject != NULL);
	g_return_if_fail (*item_subject == NULL);

	wrapper = pygobject_new (G_OBJECT (item));
	
	Py_INCREF (subject);
	*item_subject = subject;

	result = PyObject_CallMethod (*item_subject,
				      "add_presentation",
				      "O", wrapper);
	if (result)
		Py_DECREF (result);
	else {
		PyErr_Print();
		PyErr_Clear();
		g_assert_not_reached();
	}

	/* subject.connect(wrapper.element_update)
	 * # This increments wrapper's ref */
	element_update = PyObject_GetAttrString (wrapper, "element_update");
	result = PyObject_CallMethod (subject, "connect", "O", element_update);

	Py_XDECREF (result);
	Py_DECREF (element_update);
	Py_DECREF (wrapper);
}

void
_unset_subject (DiaCanvasItem *item, PyObject **item_subject)
{
	PyObject *wrapper;
	PyObject *element_update;
	PyObject *result;
	PyObject *subject;
	int wr_cnt;

	g_return_if_fail (DIA_IS_CANVAS_ITEM (item));
	g_return_if_fail (*item_subject != NULL);

	if ((*item_subject)->ob_refcnt == 0) {
		g_warning ("Subject has zero reference count (%p).", item);
		*item_subject = NULL;
		return;
	}

	/* This might avoid deadlock: unset the subject field first... */
	subject = *item_subject;
	*item_subject = NULL;

	wrapper = pygobject_new (G_OBJECT (item));
	g_assert (wrapper != NULL && wrapper != Py_None);
	wr_cnt = wrapper->ob_refcnt;

	/* subject.disconnect(wrapper.element_update) */
	element_update = PyObject_GetAttrString (wrapper, "element_update");
	result = PyObject_CallMethod (subject, "disconnect", "O",
				      element_update);
	Py_XDECREF (result);
	Py_DECREF (element_update);

	result = PyObject_CallMethod (subject, "remove_presentation",
				      "O", wrapper);
	if (result)
		Py_DECREF (result);
	else {
		PyErr_Print();
		PyErr_Clear();
		g_assert_not_reached();
	}

	Py_DECREF (subject);
	Py_DECREF (wrapper);
	//g_assert (wrapper->ob_refcnt == wr_cnt - 2);
	//g_message (__FUNCTION__": object->ref_count = %d, wrapper->ob_refcnt = %d", G_OBJECT (item)->ref_count, wrapper->ob_refcnt);
}
