/*
 * CommentLine
 *
 * This is LGPL'ed code.
 */

#include "comment-line.h"
#include "comment.h"
#include "relationship.h"
#include "common.h"
#include <diacanvas/dia-handle.h>
#include <diacanvas/dia-canvas-i18n.h>

static void comment_line_class_init (CommentLineClass *klass);
static void comment_line_init (CommentLine *item);
static void comment_line_set_property (GObject *object,
				  guint property_id,
				  const GValue *value,
				  GParamSpec *pspec);
static void comment_line_get_property (GObject *object,
				  guint property_id,
				  GValue *value,
				  GParamSpec *pspec);
static gdouble comment_line_glue (DiaCanvasItem *item, DiaHandle *handle,
				  gdouble *wx, gdouble *wy);
static gboolean comment_line_connect (DiaCanvasItem *item, DiaHandle *handle);
static gboolean comment_line_disconnect (DiaCanvasItem *item, DiaHandle *handle);
static gboolean comment_line_handle_disconnect (DiaCanvasItem *connecting_to,
						DiaHandle *handle,
						CommentLine *line);
static void comment_line_parent_notify (ModelElement *me);

static DiaCanvasLineClass *parent_class = NULL;

GType
comment_line_get_type (void)
{
	static GType object_type = 0;

	if (!object_type) {
		static const GTypeInfo object_info = {
			sizeof (CommentLineClass),
			(GBaseInitFunc) NULL,
			(GBaseFinalizeFunc) NULL,
			(GClassInitFunc) comment_line_class_init,
			(GClassFinalizeFunc) NULL,
			(gconstpointer) NULL, /* class_data */
			sizeof (CommentLine),
			(guint16) 0, /* n_preallocs */
			(GInstanceInitFunc) comment_line_init,
		};

		object_type = g_type_register_static (DIA_TYPE_CANVAS_LINE,
						      "CommentLine",
						      &object_info, 0);
	}

	return object_type;
}


static void
comment_line_class_init (CommentLineClass *klass)
{
	GObjectClass *object_class;
	DiaCanvasItemClass *item_class;
	
	object_class = (GObjectClass*) klass;
	item_class = DIA_CANVAS_ITEM_CLASS (klass);
	
	parent_class = g_type_class_peek_parent (klass);

	item_class->glue = comment_line_glue;
	item_class->connect = comment_line_connect;
	item_class->disconnect = comment_line_disconnect;
}


static void
comment_line_init (CommentLine *item)
{
	gdouble *dash;
	dash = g_new (gdouble, 2);
	dash[0] = 7.0;
	dash[1] = 5.0;
	DIA_CANVAS_LINE(item)->n_dash = 2;
	DIA_CANVAS_LINE(item)->dash = dash;
	item->head_disconnect_id = 0;
	item->head_disconnect_id = 0;

	//g_signal_connect (item, "notify::parent",
	//		  G_CALLBACK (comment_line_parent_notify), NULL);
}


static gdouble
comment_line_glue (DiaCanvasItem *item, DiaHandle *handle,
		   gdouble *wx, gdouble *wy)
{
	return G_MAXDOUBLE;
}

static gboolean
comment_line_connect (DiaCanvasItem *item, DiaHandle *handle)
{
	return FALSE;
}

static gboolean
comment_line_disconnect (DiaCanvasItem *item, DiaHandle *handle)
{
	return FALSE;
}

#if 0
/**
 * comment_line_parent_notify:
 * @me: 
 *
 * If the parent is changed (which happens when an object is removed from the
 * canvas), we force a 'disconnect' of the first handle in the list. This
 * will ensure that the comment<->modelElement relationship is removed and
 * restored if the comment line is removed and undone...
 **/
static void
comment_line_parent_notify (ModelElement *me)
{
	PyObject *wrapper;

	if (!me->subject)
		return;

	wrapper = pygobject_new (G_OBJECT (me));
	g_assert (wrapper != NULL && wrapper != Py_None);

	if (DIA_CANVAS_ITEM (me)->parent
	    && DIA_CANVAS_ITEM (me)->canvas->in_undo) {
		DiaHandle *head_handle;

		head_handle = g_list_first (DIA_CANVAS_ITEM (me)->handles)->data;

		if (head_handle->connected_to)
			comment_line_handle_connect (COMMENT_LINE (me),
						     head_handle,
						     head_handle->connected_to);
	} else if (!(DIA_CANVAS_ITEM (me)->parent
		     && DIA_CANVAS_ITEM (me)->canvas->in_undo)) {
		DiaHandle *head_handle;
		
		head_handle = g_list_first (DIA_CANVAS_ITEM (me)->handles)->data;

		if (COMMENT_LINE (me)->head_disconnect_id)
			comment_line_handle_disconnect (head_handle->connected_to,
							head_handle,
							COMMENT_LINE (me));
	}
	Py_DECREF (wrapper);
}
#endif

static inline DiaHandle*
find_opposite_handle (DiaCanvasItem *item, DiaHandle *handle)
{
	DiaHandle *oppos_handle = g_list_first(item->handles)->data;

	if (handle == oppos_handle)
		oppos_handle = g_list_last (item->handles)->data;
	g_assert (handle != oppos_handle);
	g_assert (oppos_handle != NULL);

	return oppos_handle;
}

gboolean
comment_line_handle_glue (CommentLine *line, DiaHandle *handle,
			  DiaCanvasItem *gluing_to)
{
	DiaHandle *oppos_handle;

	g_return_val_if_fail (IS_COMMENT_LINE (line), FALSE);
	g_return_val_if_fail (DIA_IS_HANDLE (handle), FALSE);
	g_return_val_if_fail (IS_MODEL_ELEMENT (gluing_to)
			      || IS_RELATIONSHIP (gluing_to), FALSE);

	oppos_handle = find_opposite_handle (DIA_CANVAS_ITEM(line), handle);

	/* Only connect if at least one element is a comment */
	if (!IS_COMMENT(gluing_to)
	    && oppos_handle->connected_to
	    && !IS_COMMENT (oppos_handle->connected_to))
		return FALSE;
	
	return TRUE;
}

static gboolean
comment_line_handle_disconnect (DiaCanvasItem *connected_to, DiaHandle *handle,
				CommentLine *line)
{
	int res = 0;
	DiaHandle *oppos_handle;
	PyObject *subject = NULL, *oppos_subject = NULL;
	PyObject *annotated_element = NULL;

	g_return_val_if_fail (IS_COMMENT_LINE (line), FALSE);
	g_return_val_if_fail (DIA_IS_HANDLE (handle), FALSE);

	/* Since this signal is fired for every handle that is disconnected
	 * from @item, we should filter the object that's ours... */
	if (!g_list_find (DIA_CANVAS_ITEM (line)->handles, handle))
		return TRUE;

	g_message (__FUNCTION__": %p %p %p %d", connected_to, handle, line,
			g_list_length (DIA_CANVAS_ITEM (line)->handles));

	oppos_handle = find_opposite_handle (DIA_CANVAS_ITEM(line), handle);

	if (handle == g_list_first (DIA_CANVAS_ITEM (line)->handles)->data) {
		//g_signal_handler_disconnect (connected_to,
		//			     line->head_disconnect_id);
		line->head_disconnect_id = 0;
	} else if (handle == g_list_last (DIA_CANVAS_ITEM (line)->handles)->data) {
		//g_signal_handler_disconnect (connected_to,
		//			     line->tail_disconnect_id);
		line->tail_disconnect_id = 0;
	} else {
		g_warning ("This function is called, but the handle can not be disconnected");
		g_assert_not_reached ();
	}

	if (!handle->connected_to || !oppos_handle->connected_to)
		return TRUE;

	g_assert (handle->connected_to != NULL);
	g_assert (oppos_handle->connected_to != NULL);

	g_object_get (handle->connected_to, "subject", &subject, NULL);
	g_object_get (oppos_handle->connected_to, "subject", &oppos_subject, NULL);

	if (IS_COMMENT (handle->connected_to)) {
		annotated_element = PyObject_GetAttrString (subject,
							    "annotatedElement");
		g_assert (annotated_element != NULL && annotated_element != Py_None);
		res = PyObject_DelItem (annotated_element, oppos_subject);
		if (res != 0) {
			//PyErr_Print ();
			PyErr_Clear ();
			//g_assert_not_reached ();
		}
	} else {
		annotated_element = PyObject_GetAttrString (oppos_subject,
							    "annotatedElement");
		g_assert (annotated_element != NULL && annotated_element != Py_None);
		res = PyObject_DelItem (annotated_element, subject);
		if (res != 0) {
			//PyErr_Print ();
			PyErr_Clear ();
			//g_assert_not_reached ();
		}
	}

	Py_DECREF (subject);
	Py_DECREF (oppos_subject);
	Py_DECREF (annotated_element);

	g_message (__FUNCTION__": done");

	return TRUE;
}

gboolean
comment_line_handle_connect (CommentLine *line, DiaHandle *handle,
			     DiaCanvasItem *connecting_to)
{
	DiaHandle *oppos_handle;
	PyObject *subject = NULL, *oppos_subject = NULL;
	guint id;

	g_return_val_if_fail (IS_COMMENT_LINE (line), FALSE);
	g_return_val_if_fail (DIA_IS_HANDLE (handle), FALSE);
	g_return_val_if_fail (IS_MODEL_ELEMENT (connecting_to)
			      || IS_RELATIONSHIP (connecting_to), FALSE);
	g_assert (g_list_find (DIA_CANVAS_ITEM (line)->handles, handle));

	g_message (__FUNCTION__": start");

	oppos_handle = find_opposite_handle (DIA_CANVAS_ITEM(line), handle);

	/* Only connect if at least one element is a comment */
	if (!IS_COMMENT(connecting_to)
	    && oppos_handle->connected_to
	    && !IS_COMMENT (oppos_handle->connected_to))
		return FALSE;
	
	if (handle == g_list_first (DIA_CANVAS_ITEM (line)->handles)->data
	    && line->head_disconnect_id == 0)
		line->head_disconnect_id = g_signal_connect (connecting_to,
			"disconnect", G_CALLBACK (comment_line_handle_disconnect), line);
	else if (handle == g_list_last (DIA_CANVAS_ITEM (line)->handles)->data
	    && line->tail_disconnect_id == 0)
		line->tail_disconnect_id = g_signal_connect (connecting_to,
			"disconnect", G_CALLBACK (comment_line_handle_disconnect), line);
	else {
		g_message (__FUNCTION__": both ends are connected...");
		return TRUE;
	}

	/* Do not try to connect, but allow the handle to be connected if the
	 * opposite handle is not connected. */
	if (!oppos_handle->connected_to)
		return TRUE;

	g_object_get (connecting_to, "subject", &subject, NULL);
	g_object_get (oppos_handle->connected_to, "subject", &oppos_subject, NULL);

	/* Establish the connection: */
	if (IS_COMMENT (connecting_to))
		PyObject_SetAttrString (subject, "annotatedElement",
					oppos_subject);
	else
		PyObject_SetAttrString (oppos_subject, "annotatedElement",
					subject);
	Py_DECREF (subject);
	Py_DECREF (oppos_subject);

	return TRUE;
}

