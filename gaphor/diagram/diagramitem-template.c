/*
 * @Name@
 *
 * This is LGPL'ed code.
 */

#include "@filename@.h"
#include "common.h"
#include <diacanvas/dia-shape.h>
#include <diacanvas/dia-canvas-i18n.h>

enum {
};

static void @name@_class_init (@Name@Class *klass);
static void @name@_init (@Name@ *item);
static void @name@_dispose (GObject *object);
static void @name@_set_property (GObject *object,
					     guint property_id,
					     const GValue *value,
					     GParamSpec *pspec);
static void @name@_get_property (GObject *object,
					     guint property_id,
					     GValue *value,
					     GParamSpec *pspec);
static void @name@_update (DiaCanvasItem *item, gdouble affine[6]);
static gboolean @name@_event (DiaCanvasItem *item, DiaEvent *event);

static @ParentName@Class *parent_class = NULL;

GType
@name@_get_type (void)
{
	static GType object_type = 0;

	if (!object_type) {
		static const GTypeInfo object_info = {
			sizeof (@Name@Class),
			(GBaseInitFunc) NULL,
			(GBaseFinalizeFunc) NULL,
			(GClassInitFunc) @name@_class_init,
			(GClassFinalizeFunc) NULL,
			(gconstpointer) NULL, /* class_data */
			sizeof (@Name@),
			(guint16) 0, /* n_preallocs */
			(GInstanceInitFunc) @name@_init,
		};

		object_type = g_type_register_static (TYPE_@PARENT_NAME@,
						      "@Name@",
						      &object_info, 0);
	}

	return object_type;
}


static void
@name@_class_init (@Name@Class *klass)
{
	GObjectClass *object_class;
	DiaCanvasItemClass *item_class;
	
	object_class = (GObjectClass*) klass;
	item_class = DIA_CANVAS_ITEM_CLASS (klass);
	
	parent_class = g_type_class_peek_parent (klass);

	object_class->dispose = @name@_dispose;
	object_class->get_property = @name@_get_property;
	object_class->set_property = @name@_set_property;
	
	item_class->update = @name@_update;
	item_class->event = @name@_event;
}


static void
@name@_init (@Name@ *item)
{
}


static void
@name@_set_property (GObject *object, guint property_id,
				 const GValue *value, GParamSpec *pspec)
{
	PyObject *pyobj;

	switch (property_id) {
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
@name@_get_property (GObject *object, guint property_id,
				 GValue *value, GParamSpec *pspec)
{
	PyObject *pyobj;

	switch (property_id) {
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
@name@_dispose (GObject *object)
{
	G_OBJECT_CLASS (parent_class)->dispose (object);
}


static void
@name@_update (DiaCanvasItem *item, gdouble affine[6])
{
}

static gboolean
@name@_event (DiaCanvasItem *item, DiaEvent *event)
{
	@Name@ *@name@ = (@Name@*) item;
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
						&@name@->cursor_index);
		dia_canvas_item_request_update (item);
		break;
	}
	case DIA_EVENT_KEY_PRESS:
		result = handle_key_event_for_subject (item,
						       (DiaEventKey*) event,
						       MODEL_ELEMENT(item)->subject,
						       "name",
						       SHAPE_TEXT (item),
						       &@name@->cursor_index);
		break;
	default:
		break;
	}
	return result;
}

