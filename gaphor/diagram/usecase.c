/*
 * UseCase
 *
 * This is LGPL'ed code.
 */

#include "usecase.h"
#include "common.h"
#include <diacanvas/dia-shape.h>
#include <diacanvas/dia-canvas-i18n.h>

enum {
	PROP_FONT = 1,
	PROP_NAME,
	PROP_TEXT_HEIGHT
};

#define SHAPE_ELLIPSE(use_case)	(((DiaCanvasItem*)use_case)->shapes->data)
#define SHAPE_TEXT(use_case)	(((DiaCanvasItem*)use_case)->shapes->next->data)

#define MARGIN_X	(35.0)
#define MARGIN_Y	(15.0)

static void use_case_class_init (UseCaseClass *klass);
static void use_case_init (UseCase *item);
static void use_case_dispose (GObject *object);
static void use_case_set_property (GObject *object,
					     guint property_id,
					     const GValue *value,
					     GParamSpec *pspec);
static void use_case_get_property (GObject *object,
					     guint property_id,
					     GValue *value,
					     GParamSpec *pspec);
static void use_case_update (DiaCanvasItem *item, gdouble affine[6]);
static void use_case_handle_motion (DiaCanvasItem *item, DiaHandle *handle,                                         gdouble *wx, gdouble *wy,
				    DiaEventMask mask);
static gboolean use_case_event (DiaCanvasItem *item, DiaEvent *event);
static void use_case_element_update (ModelElement *element, const gchar *key);

static void do_auto_resize (DiaCanvasItem *item, DiaShape *shape_text);

static ClassifierClass *parent_class = NULL;

GType
use_case_get_type (void)
{
	static GType object_type = 0;

	if (!object_type) {
		static const GTypeInfo object_info = {
			sizeof (UseCaseClass),
			(GBaseInitFunc) NULL,
			(GBaseFinalizeFunc) NULL,
			(GClassInitFunc) use_case_class_init,
			(GClassFinalizeFunc) NULL,
			(gconstpointer) NULL, /* class_data */
			sizeof (UseCase),
			(guint16) 0, /* n_preallocs */
			(GInstanceInitFunc) use_case_init,
		};

		object_type = g_type_register_static (TYPE_CLASSIFIER,
						      "UseCase",
						      &object_info, 0);
	}

	return object_type;
}


static void
use_case_class_init (UseCaseClass *klass)
{
	GObjectClass *object_class;
	DiaCanvasItemClass *item_class;
	ModelElementClass *model_class;

	object_class = (GObjectClass*) klass;
	item_class = DIA_CANVAS_ITEM_CLASS (klass);
	model_class = (ModelElementClass*) klass;

	parent_class = g_type_class_peek_parent (klass);

	object_class->dispose = use_case_dispose;
	object_class->get_property = use_case_get_property;
	object_class->set_property = use_case_set_property;
	
	item_class->update = use_case_update;
	item_class->handle_motion = use_case_handle_motion;
	item_class->event = use_case_event;
	model_class->element_update = use_case_element_update;

	g_object_class_install_property (object_class,
					 PROP_FONT,
					 g_param_spec_boxed ("font",
						_("Font description"),
						_(""),
						PANGO_TYPE_FONT_DESCRIPTION,
						G_PARAM_WRITABLE));
	g_object_class_install_property (object_class,
					 PROP_NAME,
					 g_param_spec_string ("name",
						_("Name"),
						_("Name"),
						NULL,
						G_PARAM_READWRITE));
	g_object_class_install_property (object_class,
					 PROP_TEXT_HEIGHT,
					 g_param_spec_double ("text_height",
						_("Text height"),
						_("text height, for internal use."),
						0.0, G_MAXDOUBLE, 0.0,
						G_PARAM_READWRITE));
}


static void
use_case_init (UseCase *item)
{
	item->cursor_index = 0;
	item->text_height = 10.0;
	DIA_CANVAS_ELEMENT(item)->height = 50.0;
	DIA_CANVAS_ELEMENT(item)->min_width = 10.0;
	DIA_CANVAS_ELEMENT(item)->min_height = 10.0;

	APPEND_SHAPE (item, DIA_SHAPE_ELLIPSE);
	APPEND_SHAPE (item, DIA_SHAPE_TEXT);
	dia_shape_ellipse_set_line_width (SHAPE_ELLIPSE(item), 2.0);
	dia_shape_text (SHAPE_TEXT (item),
			pango_font_description_from_string ("sans bold 10"),
			"");
	dia_shape_text_set_alignment (SHAPE_TEXT (item), PANGO_ALIGN_CENTER);
}


static void
use_case_set_property (GObject *object, guint property_id,
				 const GValue *value, GParamSpec *pspec)
{
	PyObject *pyobj;

	switch (property_id) {
	case PROP_FONT:
		dia_shape_text_set_font_description (SHAPE_TEXT(object),
			(PangoFontDescription*) (g_value_get_boxed (value)));
		dia_canvas_item_request_update (DIA_CANVAS_ITEM (object));
		break;
	case PROP_NAME:
		if (!MODEL_ELEMENT (object)->subject) {
			g_warning (_("Object does not have a subject!"));
			break;
		}
		pyobj = PyString_FromString (g_value_get_string (value));
		PyObject_SetAttrString (MODEL_ELEMENT (object)->subject,
					"name", pyobj);
		Py_DECREF (pyobj);
		break;
	case PROP_TEXT_HEIGHT:
		USE_CASE(object)->text_height = g_value_get_double (value);
		dia_canvas_item_request_update (DIA_CANVAS_ITEM (object));
		break;
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
use_case_get_property (GObject *object, guint property_id,
				 GValue *value, GParamSpec *pspec)
{
	PyObject *pyobj;

	switch (property_id) {
	case PROP_FONT:
		g_value_set_boxed (value, ((DiaShapeText*) SHAPE_TEXT (object))->font_desc);
		break;
	case PROP_NAME:
		if (!MODEL_ELEMENT (object)->subject) {
			g_warning (_("Object does not have a subject!"));
			return;
		}
		//pyobj = PyObject_GetAttrString (MODEL_ELEMENT(object)->subject,
		//				"name");
		//if (pyobj) {
		//	g_value_set_string (value, PyString_AsString (pyobj));
		//	Py_DECREF (pyobj);
		//}
		g_value_set_string (value, subject_get_string (MODEL_ELEMENT(object)->subject, "name"));
		break;
	case PROP_TEXT_HEIGHT:
		g_value_set_double (value, USE_CASE(object)->text_height);
		break;
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
use_case_dispose (GObject *object)
{
	G_OBJECT_CLASS (parent_class)->dispose (object);
}

/* For comments, only change the height of the comment box. */
static void
do_auto_resize (DiaCanvasItem *item, DiaShape *shape_text)
{
	gint h, w;
	gdouble new_h, new_w;
	PangoLayout *layout;

	layout = dia_shape_text_to_pango_layout (shape_text, TRUE);

	pango_layout_get_size (layout, &w, &h);
	dia_canvas_item_preserve_property (item, "width");
	DIA_CANVAS_ELEMENT(item)->width = (gdouble) w / (gdouble) PANGO_SCALE + 2*MARGIN_X;
	dia_canvas_item_preserve_property (item, "text_height");
	USE_CASE(item)->text_height = (gdouble) h / (gdouble) PANGO_SCALE;
	dia_canvas_item_preserve_property (item, "height");
	DIA_CANVAS_ELEMENT(item)->height = USE_CASE (item)->text_height + 2*MARGIN_Y;
	g_object_unref (layout);
	//DIA_SET_FLAGS (item, DIA_NEED_ALIGN_HANDLES);
	dia_canvas_element_align_handles (DIA_CANVAS_ELEMENT (item));
}

static void
use_case_update (DiaCanvasItem *item, gdouble affine[6])
{
	DiaShape *shape_ellipse, *shape_text;
	DiaCanvasElement *elem = (DiaCanvasElement*) item;
	UseCase *use_case = (UseCase*) item;
	DiaPoint p[3];
	DiaPoint pos;
	gdouble cx;

	shape_ellipse = SHAPE_ELLIPSE (item);
	shape_text = SHAPE_TEXT (item);

	cx = elem->width / 2.0;

	/* Add use_case text to the box */
	dia_shape_text_set_cursor (shape_text, use_case->cursor_index);
	dia_shape_request_update (shape_text);
	
	if (MODEL_ELEMENT(item)->need_resize)
		do_auto_resize (item, shape_text);

	pos.x = 0;
	pos.y = (elem->height - use_case->text_height) / 2;
	pos.y = MAX (0.0, pos.y);
	dia_shape_text_set_pos (shape_text, &pos);
	dia_shape_text_set_text_width (shape_text, elem->width);
	dia_shape_text_set_max_width (shape_text, elem->width);
	dia_shape_text_set_max_height (shape_text, elem->height);

	DIA_CANVAS_ITEM_CLASS (parent_class)->update (item, affine);

	/* Ellipse */
	p[0].x = elem->width / 2.0; p[0].y = elem->height / 2.0;
	dia_shape_ellipse (shape_ellipse, &p[0], elem->width, elem->height);
	dia_shape_request_update (shape_ellipse);

	/* Adjust the bounding box */
	item->bounds.left -= 1.0;
        item->bounds.top -= 1.0;
	item->bounds.right += 1.0;
	item->bounds.bottom += 1.0;
}

static void
use_case_handle_motion (DiaCanvasItem *item, DiaHandle *handle,                                         gdouble *wx, gdouble *wy, DiaEventMask mask)
{
	DIA_CANVAS_ITEM_CLASS (parent_class)->handle_motion (item, handle,
							     wx, wy, mask);
	if (MODEL_ELEMENT(item)->auto_resize) {
		DiaShape *shape_text = SHAPE_TEXT (item);
		DiaCanvasElement *elem = (DiaCanvasElement*) item;
		gint h;
		PangoLayout *layout;
		dia_shape_text_set_text_width (shape_text, elem->width);
		dia_shape_text_set_max_width (shape_text, elem->width);
		dia_shape_text_set_max_height (shape_text, elem->height);

		layout = dia_shape_text_to_pango_layout (shape_text, TRUE);

		pango_layout_get_size (layout, NULL, &h);
		dia_canvas_item_preserve_property (item, "text_height");
		USE_CASE(item)->text_height = (gdouble) h / (gdouble) PANGO_SCALE;
		g_object_unref (layout);
	}
}

static gboolean
use_case_event (DiaCanvasItem *item, DiaEvent *event)
{
	UseCase *use_case = (UseCase*) item;
	gboolean result;
	PyObject *str_obj;
	GString *str;

	result = DIA_CANVAS_ITEM_CLASS (parent_class)->event (item, event);

	switch (event->type) {
	case DIA_EVENT_BUTTON_PRESS: {
		gdouble affine[6];
		DiaPoint pos;

		pos.x = event->button.x;
		pos.y = event->button.y;
		dia_canvas_item_affine_point_w2i (item, &pos.x, &pos.y);
		dia_shape_text_cursor_from_pos (SHAPE_TEXT (item), &pos,
						&use_case->cursor_index);
		dia_canvas_item_request_update (item);
		break;
	}
	case DIA_EVENT_KEY_PRESS: {
		DiaShape *shape_text = SHAPE_TEXT (item);
		result = handle_key_event_for_subject (item,
						       (DiaEventKey*) event,
						       MODEL_ELEMENT(item)->subject,
						       "name",
						       shape_text,
						       &use_case->cursor_index);
		if (MODEL_ELEMENT(item)->need_resize)
			do_auto_resize (item, shape_text);
		break;
	}
	default:
		break;
	}
	return result;
}

static void
use_case_element_update (ModelElement *element, const gchar *key)
{
	if (g_str_equal (key, "name")) {
		//PyObject *str_obj;
		//str_obj = PyObject_GetAttrString (element->subject, "name");
		dia_shape_text_set_text (SHAPE_TEXT (element),
					 subject_get_string (element->subject,
							     "name"));
					 //PyString_AsString (str_obj));
		do_auto_resize ((DiaCanvasItem*) element, SHAPE_TEXT (element));
		dia_canvas_item_request_update ((DiaCanvasItem*) element);
		//Py_DECREF (str_obj);
	} else {
		MODEL_ELEMENT_CLASS (parent_class)->element_update (element, key);
	}
}

