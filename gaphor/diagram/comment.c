/*
 * Comment
 *
 * This is LGPL'ed code.
 */

#include "comment.h"
#include "common.h"
#include <diacanvas/dia-shape.h>
#include <diacanvas/dia-canvas-i18n.h>

enum {
	PROP_FONT = 1,
	PROP_BODY
};

#define EAR (15.0)
#define OFS (5.0)

#define SHAPE_TEXT(comment) (((DiaCanvasItem*) comment)->shapes->next->data)

static void comment_class_init (CommentClass *klass);
static void comment_init (Comment *item);
static void comment_dispose (GObject *object);
static void comment_set_property (GObject *object,
				  guint property_id,
				  const GValue *value,
				  GParamSpec *pspec);
static void comment_get_property (GObject *object,
				  guint property_id,
				  GValue *value,
				  GParamSpec *pspec);
static void comment_update (DiaCanvasItem *item, gdouble affine[6]);
static gboolean comment_event (DiaCanvasItem *item, DiaEvent *event);
static void comment_element_update (ModelElement *element, const gchar *key);

static void do_auto_resize (DiaCanvasItem *item, DiaShape *shape_text);

static ModelElementClass *parent_class = NULL;

GType
comment_get_type (void)
{
	static GType object_type = 0;

	if (!object_type) {
		static const GTypeInfo object_info = {
			sizeof (CommentClass),
			(GBaseInitFunc) NULL,
			(GBaseFinalizeFunc) NULL,
			(GClassInitFunc) comment_class_init,
			(GClassFinalizeFunc) NULL,
			(gconstpointer) NULL, /* class_data */
			sizeof (Comment),
			(guint16) 0, /* n_preallocs */
			(GInstanceInitFunc) comment_init,
		};

		object_type = g_type_register_static (TYPE_MODEL_ELEMENT,
						      "Comment",
						      &object_info, 0);
	}

	return object_type;
}


static void
comment_class_init (CommentClass *klass)
{
	GObjectClass *object_class;
	DiaCanvasItemClass *item_class;
	ModelElementClass *model_class;

	object_class = (GObjectClass*) klass;
	item_class = DIA_CANVAS_ITEM_CLASS (klass);
	model_class = (ModelElementClass*) klass;
	
	parent_class = g_type_class_peek_parent (klass);

	object_class->dispose = comment_dispose;
	object_class->get_property = comment_get_property;
	object_class->set_property = comment_set_property;
	
	item_class->update = comment_update;
	item_class->event = comment_event;
	model_class->element_update = comment_element_update;

	g_object_class_install_property (object_class,
					 PROP_FONT,
					 g_param_spec_boxed ("font",
						_("Font description"),
						_(""),
						PANGO_TYPE_FONT_DESCRIPTION,
						G_PARAM_WRITABLE));
	g_object_class_install_property (object_class,
					 PROP_BODY,
					 g_param_spec_string ("body",
						_(""),
						_(""),
						NULL,
						G_PARAM_READWRITE));
}


static void
comment_init (Comment *item)
{
	DiaPoint pos = { OFS, OFS };

	item->cursor_index = 0;
	DIA_CANVAS_ELEMENT(item)->min_width = EAR;
	DIA_CANVAS_ELEMENT(item)->min_height = EAR;

	APPEND_SHAPE (item, DIA_SHAPE_PATH);
	APPEND_SHAPE (item, DIA_SHAPE_TEXT);
	dia_shape_text (SHAPE_TEXT (item),
			pango_font_description_from_string ("sans 10"), "");
	dia_shape_text_set_pos (SHAPE_TEXT (item), &pos);
}


static void
comment_set_property (GObject *object, guint property_id,
				 const GValue *value, GParamSpec *pspec)
{
	PyObject *pyobj;

	switch (property_id) {
	case PROP_FONT:
		dia_shape_text_set_font_description (SHAPE_TEXT (object),
						     g_value_get_boxed (value));
							    
		dia_canvas_item_request_update (DIA_CANVAS_ITEM (object));
		break;
	case PROP_BODY:
		if (!MODEL_ELEMENT (object)->subject) {
			g_warning (_("Object does not have a subject!"));
			break;
		}
		pyobj = PyString_FromString (g_value_get_string (value));
		PyObject_SetAttrString (MODEL_ELEMENT (object)->subject,
					"body", pyobj);
		Py_DECREF (pyobj);
		break;
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
comment_get_property (GObject *object, guint property_id,
				 GValue *value, GParamSpec *pspec)
{
	PyObject *pyobj;

	switch (property_id) {
	case PROP_FONT:
		g_value_set_boxed (value, ((DiaShapeText*) SHAPE_TEXT (object))->font_desc);
		break;
	case PROP_BODY:
		if (!MODEL_ELEMENT (object)->subject) {
			g_warning (_("Object does not have a subject!"));
			return;
		}
		//pyobj = PyObject_GetAttrString (MODEL_ELEMENT(object)->subject,
		//				"body");
		//g_value_set_string (value, PyString_AsString (pyobj));
		g_value_set_string (value, subject_get_string (MODEL_ELEMENT(object)->subject, "body"));
		//Py_DECREF (pyobj);
		break;
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
comment_dispose (GObject *object)
{
	G_OBJECT_CLASS (parent_class)->dispose (object);
}

/* For comments, only change the height of the comment box. */
static void
do_auto_resize (DiaCanvasItem *item, DiaShape *shape_text)
{
	gint h, w;
	gdouble dw;
	PangoLayout *layout;

	if (!MODEL_ELEMENT (item)->auto_resize)
		return;

	//g_message (__FUNCTION__);
	layout = dia_shape_text_to_pango_layout (shape_text,
						 TRUE);

	pango_layout_get_size (layout, &w, &h);
	dia_canvas_item_preserve_property (item, "height");
	DIA_CANVAS_ELEMENT (item)->height =
		(gdouble) h / (gdouble) PANGO_SCALE + 2 * OFS;

	dw = (gdouble) w / (gdouble) PANGO_SCALE + OFS + EAR;
	if (dw > DIA_CANVAS_ELEMENT (item)->width) {
		dia_canvas_item_preserve_property (item,
						   "width");
		DIA_CANVAS_ELEMENT (item)->width = dw;
	}

	g_object_unref (layout);
	//DIA_SET_FLAGS (item, DIA_NEED_ALIGN_HANDLES);
	dia_canvas_element_align_handles (DIA_CANVAS_ELEMENT (item));
	MODEL_ELEMENT (item)->need_resize = FALSE;
}

static void
comment_update (DiaCanvasItem *item, gdouble affine[6])
{
	DiaShape *shape_text, *shape_border;
	DiaCanvasElement *elem = (DiaCanvasElement*) item;
	Comment *text = (Comment*) item;
	DiaPoint p[8];

	shape_border = item->shapes->data;
	shape_text = SHAPE_TEXT (item);

	/* Add comment text to the box */
	dia_shape_text_set_cursor (shape_text, text->cursor_index);
	dia_shape_request_update (shape_text);
		
	if (MODEL_ELEMENT (item)->need_resize)
		do_auto_resize (item, shape_text);

	/* Now we can set width and height for the text: */
	dia_shape_text_set_text_width (shape_text,
				       MAX (0.0, elem->width - OFS - EAR));
	dia_shape_text_set_max_width (shape_text,
				      MAX (0.0, elem->width - OFS - EAR));
	dia_shape_text_set_max_height (shape_text,
				       MAX (0.0, elem->height - 2*OFS));

	DIA_CANVAS_ITEM_CLASS (parent_class)->update (item, affine);
	
	/* Create the comment border */
	p[0].x = elem->width - EAR;
	p[0].y = 0.0;
	p[1].x = elem->width - EAR;
	p[1].y = EAR;
	p[2].x = elem->width;
	p[2].y = EAR;
	p[3].x = elem->width - EAR;
	p[3].y = 0.0;
	p[4].x = 0.0;
	p[4].y = 0.0;
	p[5].x = 0.0;
	p[5].y = elem->height;
	p[6].x = elem->width;
	p[6].y = elem->height;
	p[7].x = elem->width;
	p[7].y = EAR;

	dia_shape_polyline (shape_border, 8, p);
	dia_shape_path_set_line_width (shape_border, 2.0);
	dia_shape_request_update (shape_border);

	/* Adjust the bounding box */
	item->bounds.left -= 1.0;
        item->bounds.top -= 1.0;
	item->bounds.right += 1.0;
	item->bounds.bottom += 1.0;
}

static gboolean
comment_event (DiaCanvasItem *item, DiaEvent *event)
{
	Comment *text = (Comment*) item;
	gboolean result;

	result = DIA_CANVAS_ITEM_CLASS (parent_class)->event (item, event);

	switch (event->type) {
	case DIA_EVENT_BUTTON_PRESS: {
		gdouble affine[6];
		DiaPoint pos;
		
		pos.x = event->button.x;
		pos.y = event->button.y;
		dia_canvas_item_affine_point_w2i (item, &pos.x, &pos.y);
		dia_shape_text_cursor_from_pos (SHAPE_TEXT (item), &pos,
						&text->cursor_index);
		dia_canvas_item_request_update (item);
		break;
	}
	case DIA_EVENT_KEY_PRESS: {
		DiaShape *shape_text = SHAPE_TEXT (item);
		result = handle_key_event_for_subject (item,
						       (DiaEventKey*) event,
						       MODEL_ELEMENT(item)->subject,
						       "body",
						       shape_text,
						       &text->cursor_index);
		if (MODEL_ELEMENT (item)->need_resize)
			do_auto_resize (item, shape_text);
		break;
	}
	default:
		break;
	}
	return result;
}

static void
comment_element_update (ModelElement *element, const gchar *key)
{
	if (g_str_equal (key, "body")) {
		//PyObject *str_obj;
		//str_obj = PyObject_GetAttrString (element->subject, "body");
		dia_shape_text_set_text (SHAPE_TEXT (element),
					 subject_get_string (element->subject, "body"));
		//			 PyString_AsString (str_obj));
		//do_auto_resize ((DiaCanvasItem*) element, SHAPE_TEXT (element));
		element->need_resize = TRUE;
		dia_canvas_item_request_update ((DiaCanvasItem*) element);
		//Py_DECREF (str_obj);
	} else {
		MODEL_ELEMENT_CLASS (parent_class)->element_update (element, key);
	}
}

