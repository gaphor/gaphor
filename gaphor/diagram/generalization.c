/*
 * Generalization
 *
 * This is LGPL'ed code.
 */

#include "generalization.h"
#include "common.h"
#include <diacanvas/dia-shape.h>
#include <diacanvas/dia-canvas-i18n.h>


static void generalization_class_init (GeneralizationClass *klass);
static void generalization_init (Generalization *item);
static void generalization_dispose (GObject *object);
static void generalization_set_property (GObject *object,
					     guint property_id,
					     const GValue *value,
					     GParamSpec *pspec);
static void generalization_get_property (GObject *object,
					     guint property_id,
					     GValue *value,
					     GParamSpec *pspec);
static void generalization_update (DiaCanvasItem *item, gdouble affine[6]);
static gboolean generalization_connect (DiaCanvasItem *item, DiaHandle *handle);
static gboolean generalization_disconnect (DiaCanvasItem *item,
					   DiaHandle *handle);
static void generalization_parent_notify (Generalization *gen);

static RelationshipClass *parent_class = NULL;

GType
generalization_get_type (void)
{
	static GType object_type = 0;

	if (!object_type) {
		static const GTypeInfo object_info = {
			sizeof (GeneralizationClass),
			(GBaseInitFunc) NULL,
			(GBaseFinalizeFunc) NULL,
			(GClassInitFunc) generalization_class_init,
			(GClassFinalizeFunc) NULL,
			(gconstpointer) NULL, /* class_data */
			sizeof (Generalization),
			(guint16) 0, /* n_preallocs */
			(GInstanceInitFunc) generalization_init,
		};

		object_type = g_type_register_static (TYPE_RELATIONSHIP,
						      "Generalization",
						      &object_info, 0);
	}

	return object_type;
}


static void
generalization_class_init (GeneralizationClass *klass)
{
	GObjectClass *object_class;
	DiaCanvasItemClass *item_class;
	
	object_class = (GObjectClass*) klass;
	item_class = DIA_CANVAS_ITEM_CLASS (klass);
	
	parent_class = g_type_class_peek_parent (klass);

	object_class->dispose = generalization_dispose;
	object_class->get_property = generalization_get_property;
	object_class->set_property = generalization_set_property;
	
	item_class->update = generalization_update;
	item_class->connect = generalization_connect;
	item_class->disconnect = generalization_disconnect;
}


static void
generalization_init (Generalization *item)
{
	DiaCanvasLine *line = (DiaCanvasLine*) item;

	line->has_head = TRUE;
	line->head_a = 15.0;
	line->head_b = 15.0;
	line->head_c = 10.0;
	line->head_d = 10.0;
	line->head_fill_color = 0;
}


static void
generalization_set_property (GObject *object, guint property_id,
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
generalization_get_property (GObject *object, guint property_id,
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
generalization_dispose (GObject *object)
{
	G_OBJECT_CLASS (parent_class)->dispose (object);
}


static void
generalization_update (DiaCanvasItem *item, gdouble affine[6])
{
	DIA_CANVAS_ITEM_CLASS (parent_class)->update (item, affine);
}

gboolean
generalization_handle_connect (DiaCanvasItem *item, DiaHandle *handle)
{
#if 0
	/* Only allow comment and generalization objects to connect. */

	if (!IS_COMMENT (handle->owner) || !IS_GENERALIZATION (handle->owner))
		return G_MAXDOUBLE;

	oppos_handle = find_opposite_handle (DIA_CANVAS_ITEM(line), handle);

	/* set disconnect signals */

	/* Only do something if both ends of the generalization are connected */
	if (!oppos_handle->connected_to)
		return TRUE;

	/* Take a look in one of the connected object->subject's to see if
	 * a generalization relationship already exists. */
	if (!handle->connected_to)
		return TRUE;


	g_object_get (connecting_to, "subject", &subject, NULL);

	/* If it exists, use it. Otherwise create a new UML.Generalization */
	/* TODO: should we add the UML.Generalization field to the class obj?*/
#endif
	return DIA_CANVAS_ITEM_CLASS (parent_class)->connect (item, handle);
}

static gboolean
generalization_disconnect (DiaCanvasItem *item, DiaHandle *handle)
{
	return DIA_CANVAS_ITEM_CLASS (parent_class)->disconnect (item, handle);
}

static void
generalization_parent_notify (Generalization *gen)
{
}

