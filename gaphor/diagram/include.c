/*
 * Include
 *
 * This is LGPL'ed code.
 */

#include "include.h"
#include "common.h"
#include <diacanvas/dia-shape.h>
#include <diacanvas/dia-canvas-i18n.h>

static void include_class_init (RelationshipClass *klass);
static void include_init (Include *item);
static void include_dispose (GObject *object);
static void include_set_property (GObject *object,
					     guint property_id,
					     const GValue *value,
					     GParamSpec *pspec);
static void include_get_property (GObject *object,
					     guint property_id,
					     GValue *value,
					     GParamSpec *pspec);
static void include_update (DiaCanvasItem *item, gdouble affine[6]);
static gboolean include_connect (DiaCanvasItem *item, DiaHandle *handle);
static gboolean include_disconnect (DiaCanvasItem *item,
					   DiaHandle *handle);

static RelationshipClass *parent_class = NULL;

GType
include_get_type (void)
{
	static GType object_type = 0;

	if (!object_type) {
		static const GTypeInfo object_info = {
			sizeof (IncludeClass),
			(GBaseInitFunc) NULL,
			(GBaseFinalizeFunc) NULL,
			(GClassInitFunc) include_class_init,
			(GClassFinalizeFunc) NULL,
			(gconstpointer) NULL, /* class_data */
			sizeof (Include),
			(guint16) 0, /* n_preallocs */
			(GInstanceInitFunc) include_init,
		};

		object_type = g_type_register_static (TYPE_RELATIONSHIP,
						      "Include",
						      &object_info, 0);
	}

	return object_type;
}


static void
include_class_init (RelationshipClass *klass)
{
	GObjectClass *object_class;
	DiaCanvasItemClass *item_class;
	
	object_class = (GObjectClass*) klass;
	item_class = DIA_CANVAS_ITEM_CLASS (klass);
	
	parent_class = g_type_class_peek_parent (klass);

	object_class->dispose = include_dispose;
	object_class->get_property = include_get_property;
	object_class->set_property = include_set_property;
	
	item_class->update = include_update;

	klass->subject_class = "Include";
	klass->head_name = "addition";
	klass->tail_name = "base";
	klass->head_xname = "includer";
	klass->tail_xname = "include";
}


static void
include_init (Include *item)
{
	gdouble *dash;
	DiaCanvasLine *line = (DiaCanvasLine*) item;

	line->has_head = TRUE;
	line->head_a = 15.0;
	line->head_b = 15.0;
	line->head_c = 10.0;
	line->head_d = 10.0;
	line->head_fill_color = 0;

	dash = g_new (gdouble, 2);
	dash[0] = 7.0;
	dash[1] = 5.0;
	DIA_CANVAS_LINE(item)->n_dash = 2;
	DIA_CANVAS_LINE(item)->dash = dash;
}


static void
include_set_property (GObject *object, guint property_id,
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
include_get_property (GObject *object, guint property_id,
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
include_dispose (GObject *object)
{
	G_OBJECT_CLASS (parent_class)->dispose (object);
}


static void
include_update (DiaCanvasItem *item, gdouble affine[6])
{
	DIA_CANVAS_ITEM_CLASS (parent_class)->update (item, affine);
}

