/*
 * Actor
 *
 * This is LGPL'ed code.
 */

#include "actor.h"
#include "common.h"
#include <diacanvas/dia-shape.h>
#include <diacanvas/dia-canvas-i18n.h>

enum {
	PROP_FONT = 1,
	PROP_NAME
};

#define SHAPE_HEAD(actor) (((DiaCanvasItem*) actor)->shapes->data)
#define SHAPE_BODY(actor) (((DiaCanvasItem*) actor)->shapes->next->data)
#define SHAPE_ARMS(actor) (((DiaCanvasItem*) actor)->shapes->next->next->data)
#define SHAPE_LEGS(actor) (((DiaCanvasItem*) actor)->shapes->next->next->next->data)
#define SHAPE_TEXT(actor) (((DiaCanvasItem*) actor)->shapes->next->next->next->next->data)
//#define SHAPE_TEXT(actor) (g_list_last (((DiaCanvasItem*)actor)->shapes)->data)

#define HEAD	(11.0)
#define ARM	(19.0)
#define NECK	(10.0)
#define BODY	(20.0)

static void actor_class_init (ActorClass *klass);
static void actor_init (Actor *item);
static void actor_dispose (GObject *object);
static void actor_set_property (GObject *object,
					     guint property_id,
					     const GValue *value,
					     GParamSpec *pspec);
static void actor_get_property (GObject *object,
					     guint property_id,
					     GValue *value,
					     GParamSpec *pspec);
static void actor_update (DiaCanvasItem *item, gdouble affine[6]);
static gboolean actor_event (DiaCanvasItem *item, DiaEvent *event);
static void actor_element_update (ModelElement *element, const gchar *key);
static void do_auto_resize (DiaCanvasItem *item, DiaShape *shape_text);

static ClassifierClass *parent_class = NULL;

GType
actor_get_type (void)
{
	static GType object_type = 0;

	if (!object_type) {
		static const GTypeInfo object_info = {
			sizeof (ActorClass),
			(GBaseInitFunc) NULL,
			(GBaseFinalizeFunc) NULL,
			(GClassInitFunc) actor_class_init,
			(GClassFinalizeFunc) NULL,
			(gconstpointer) NULL, /* class_data */
			sizeof (Actor),
			(guint16) 0, /* n_preallocs */
			(GInstanceInitFunc) actor_init,
		};

		object_type = g_type_register_static (TYPE_CLASSIFIER,
						      "Actor",
						      &object_info, 0);
	}

	return object_type;
}


static void
actor_class_init (ActorClass *klass)
{
	GObjectClass *object_class;
	DiaCanvasItemClass *item_class;
	ModelElementClass *model_class;

	object_class = (GObjectClass*) klass;
	item_class = DIA_CANVAS_ITEM_CLASS (klass);
	model_class = MODEL_ELEMENT_CLASS (klass);

	parent_class = g_type_class_peek_parent (klass);

	object_class->dispose = actor_dispose;
	object_class->get_property = actor_get_property;
	object_class->set_property = actor_set_property;
	
	item_class->update = actor_update;
	item_class->event = actor_event;

	model_class->element_update = actor_element_update;

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
}


static void
actor_init (Actor *item)
{
	DiaPoint pos = { 0.0, HEAD + NECK + BODY + ARM };

	item->cursor_index = 0;
	DIA_CANVAS_ELEMENT(item)->min_width = ARM + ARM;
	DIA_CANVAS_ELEMENT(item)->width = DIA_CANVAS_ELEMENT(item)->min_width;
	DIA_CANVAS_ELEMENT(item)->min_height = HEAD + NECK + BODY + ARM;
	DIA_CANVAS_ELEMENT(item)->height = DIA_CANVAS_ELEMENT(item)->min_height + 15.0;

	APPEND_SHAPE (item, DIA_SHAPE_ELLIPSE); /* head */
	APPEND_SHAPE (item, DIA_SHAPE_PATH); /* body */
	APPEND_SHAPE (item, DIA_SHAPE_PATH); /* arms */
	APPEND_SHAPE (item, DIA_SHAPE_PATH); /* legs */
	APPEND_SHAPE (item, DIA_SHAPE_TEXT); /* name */
	dia_shape_ellipse_set_line_width (SHAPE_HEAD (item), 2.0);
	dia_shape_path_set_line_width (SHAPE_BODY (item), 2.0);
	dia_shape_path_set_line_width (SHAPE_ARMS (item), 2.0);
	dia_shape_path_set_line_width (SHAPE_LEGS (item), 2.0);
	dia_shape_text (SHAPE_TEXT(item),
			pango_font_description_from_string ("sans bold 10"),
			"");
	dia_shape_text_set_pos (SHAPE_TEXT(item), &pos);
	dia_shape_text_set_alignment (SHAPE_TEXT(item), PANGO_ALIGN_CENTER);
}


static void
actor_set_property (GObject *object, guint property_id,
		    const GValue *value, GParamSpec *pspec)
{
	PyObject *pyobj;

	switch (property_id) {
	case PROP_FONT:
		dia_shape_text_set_font_description (SHAPE_TEXT (object),
				(PangoFontDescription*) (g_value_get_boxed (value)));
		do_auto_resize (DIA_CANVAS_ITEM (object), SHAPE_TEXT (object));
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
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
actor_get_property (GObject *object, guint property_id,
				 GValue *value, GParamSpec *pspec)
{
	PyObject *pyobj;

	switch (property_id) {
	case PROP_FONT:
		g_value_set_boxed (value, ((DiaShapeText*)SHAPE_TEXT (object))->font_desc);
		break;
	case PROP_NAME:
		if (!MODEL_ELEMENT (object)->subject) {
			g_warning (_("Object does not have a subject!"));
			return;
		}
		g_value_set_string (value, subject_get_string (MODEL_ELEMENT(object)->subject, "name"));
		break;
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
actor_dispose (GObject *object)
{
	G_OBJECT_CLASS (parent_class)->dispose (object);
}

static void
do_auto_resize (DiaCanvasItem *item, DiaShape *shape_text)
{
	gint h, w;
	gdouble dw;
	PangoLayout *layout;

	layout = dia_shape_text_to_pango_layout (shape_text,
						 TRUE);

	pango_layout_get_size (layout, &w, &h);

	dia_canvas_item_preserve_property (item, "height");
	DIA_CANVAS_ELEMENT (item)->height =
		(gdouble) h / (gdouble) PANGO_SCALE
			+ HEAD + NECK + BODY + ARM;

	dw = (gdouble) w / (gdouble) PANGO_SCALE;
	if (dw > DIA_CANVAS_ELEMENT (item)->width) {
		dia_canvas_item_preserve_property (item,
						   "width");
		DIA_CANVAS_ELEMENT (item)->width = dw;
	}
	g_object_unref (layout);
	//DIA_SET_FLAGS (item, DIA_NEED_ALIGN_HANDLES);
	dia_canvas_element_align_handles (DIA_CANVAS_ELEMENT (item));
}

static void
actor_update (DiaCanvasItem *item, gdouble affine[6])
{
	DiaShape *shape_head, *shape_body,
		 *shape_arms, *shape_legs, *shape_text;
	DiaCanvasElement *elem = (DiaCanvasElement*) item;
	Actor *actor = (Actor*) item;
	DiaPoint p[3];
	gdouble cx;
	GList *l = item->shapes;

	shape_head = l->data; l = g_list_next (l);
	shape_body = l->data; l = g_list_next (l);
	shape_arms = l->data; l = g_list_next (l);
	shape_legs = l->data; l = g_list_next (l);
	shape_text = l->data;

	cx = elem->width / 2.0;

	/* Add actor text to the box */
	//dia_shape_text_set_font_description (shape_text,
	//				     actor->font);
	//dia_shape_set_color (shape_text, actor->color);
	//dia_shape_text_set_pos (shape_text, &pos);
	dia_shape_text_set_cursor (shape_text, actor->cursor_index);
	dia_shape_request_update (shape_text);
	
	if (MODEL_ELEMENT (item)->need_resize)
		do_auto_resize (item, shape_text);
	
	dia_shape_text_set_text_width (shape_text, elem->width);
	dia_shape_text_set_max_width (shape_text, elem->width);
	dia_shape_text_set_max_height (shape_text, elem->height
			- HEAD - BODY - NECK - ARM);

	/* We have checked the width and height, now call the parent: */
	DIA_CANVAS_ITEM_CLASS (parent_class)->update (item, affine);
	
	/* Create the actor head */
	p[0].x = cx; p[0].y = HEAD / 2.0;
	dia_shape_ellipse (shape_head, &p[0], HEAD, HEAD);
	//dia_shape_ellipse_set_line_width (shape_head, 2.0);
	dia_shape_request_update (shape_head);

	/* Body */
	p[0].x = cx;		p[0].y = HEAD;
	p[1].x = cx;		p[1].y = HEAD + NECK + BODY;
	dia_shape_line (shape_body, &p[0], &p[1]);
	//dia_shape_path_set_line_width (shape_body, 2.0);
	dia_shape_request_update (shape_body);

	/* Arms */
	p[0].x = cx - ARM;	p[0].y = HEAD + NECK;
	p[1].x = cx + ARM;	p[1].y = HEAD + NECK;
	dia_shape_line (shape_arms, &p[0], &p[1]);
	//dia_shape_path_set_line_width (shape_arms, 2.0);
	dia_shape_request_update (shape_arms);

	/* Legs */
	p[0].x = cx - ARM;	p[0].y = HEAD + NECK + BODY + ARM;
	p[1].x = cx;		p[1].y = HEAD + NECK + BODY;
	p[2].x = cx + ARM;	p[2].y = HEAD + NECK + BODY + ARM;
	dia_shape_polyline (shape_legs, 3, p);
	//dia_shape_path_set_line_width (shape_legs, 2.0);
	dia_shape_request_update (shape_legs);

	/* Adjust the bounding box */
	item->bounds.left -= 1.0;
        item->bounds.top -= 1.0;
	item->bounds.right += 1.0;
	item->bounds.bottom += 1.0;
}

static gboolean
actor_event (DiaCanvasItem *item, DiaEvent *event)
{
	Actor *actor = (Actor*) item;
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
						&actor->cursor_index);
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
						       &actor->cursor_index);
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
actor_element_update (ModelElement *element, const gchar *key)
{
	if (g_str_equal (key, "name")) {
		g_message (__FUNCTION__": name = '%s'", subject_get_string (element->subject, "name"));
		dia_shape_text_set_text (SHAPE_TEXT (element),
					 subject_get_string (element->subject,
							     "name"));
		do_auto_resize ((DiaCanvasItem*) element, SHAPE_TEXT (element));
		dia_canvas_item_request_update ((DiaCanvasItem*) element);
	} else {
		MODEL_ELEMENT_CLASS (parent_class)->element_update (element, key);
	}
}

