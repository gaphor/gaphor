/*
 * Relationship
 *
 * This is LGPL'ed code.
 */

#include "relationship.h"
#include "comment-line.h"
#include "common.h"
#include <diacanvas/dia-canvas-i18n.h>


#define relationship_set_subject(me, sj) \
	_set_subject (DIA_CANVAS_ITEM(me), sj, &(RELATIONSHIP(me)->subject))

#define relationship_unset_subject(me) \
	_unset_subject (DIA_CANVAS_ITEM(me), &(RELATIONSHIP(me)->subject))

enum {
	PROP_SUBJECT = 1
};

static void relationship_class_init (RelationshipClass *klass);
static void relationship_init (Relationship *item);
static void relationship_dispose (GObject *object);
static void relationship_set_property  (GObject *object,
					guint property_id,
					const GValue *value,
					GParamSpec *pspec);
static void relationship_get_property  (GObject *object,
					guint property_id,
					GValue *value,
					GParamSpec *pspec);
static void relationship_update (DiaCanvasItem *item, gdouble affine[6]);
static void relationship_handle_motion  (DiaCanvasItem *item, DiaHandle *handle,
					 gdouble *wx, gdouble *wy,
					 DiaEventMask mask);
static gdouble relationship_glue  (DiaCanvasItem *item, DiaHandle *handle,
				   gdouble *wx, gdouble *wy);
static gboolean relationship_connect  (DiaCanvasItem *item,
				       DiaHandle *handle);
static gboolean relationship_disconnect  (DiaCanvasItem *item,
					  DiaHandle *handle);
static void relationship_real_element_update (Relationship *relationship,
					      const gchar *key);

static DiaCanvasLineClass *parent_class = NULL;

GType
relationship_get_type (void)
{
	static GType object_type = 0;

	if (!object_type) {
		static const GTypeInfo object_info = {
			sizeof (RelationshipClass),
			(GBaseInitFunc) NULL,
			(GBaseFinalizeFunc) NULL,
			(GClassInitFunc) relationship_class_init,
			(GClassFinalizeFunc) NULL,
			(gconstpointer) NULL, /* class_data */
			sizeof (Relationship),
			(guint16) 0, /* n_preallocs */
			(GInstanceInitFunc) relationship_init,
		};

		object_type = g_type_register_static (DIA_TYPE_CANVAS_LINE,
						      "Relationship",
						      &object_info,
						      G_TYPE_FLAG_ABSTRACT);
	}

	return object_type;
}


static void
relationship_class_init (RelationshipClass *klass)
{
	GObjectClass *object_class;
	DiaCanvasItemClass *item_class;

	object_class = (GObjectClass*) klass;
	item_class = (DiaCanvasItemClass*) klass;
	
	parent_class = g_type_class_peek_parent (klass);

	object_class->dispose = relationship_dispose;
	object_class->get_property = relationship_get_property;
	object_class->set_property = relationship_set_property;
	item_class->update = relationship_update;
	item_class->handle_motion = relationship_handle_motion;
	item_class->glue = relationship_glue;
	item_class->connect = relationship_connect;
	item_class->disconnect = relationship_disconnect;
	klass->element_update = relationship_real_element_update;

	g_object_class_install_property (object_class,
					 PROP_SUBJECT,
					 g_param_spec_pointer ("subject",
						_("Subject"),
						_("Subject"),
						G_PARAM_READWRITE));
}


static void
relationship_init (Relationship *item)
{
	item->subject = NULL;
}


static void
relationship_set_property (GObject *object, guint property_id,
			    const GValue *value, GParamSpec *pspec)
{
	Relationship *element = (Relationship*) object;
	PyObject *subject;

	switch (property_id) {
	case PROP_SUBJECT:
		subject = g_value_get_pointer (value);
		if (element->subject) {
			g_warning ("This diagram item already has "
				   "a subject assigned to it");
			return;
		}
		relationship_set_subject (element, subject);
		dia_canvas_item_request_update (DIA_CANVAS_ITEM (element));
		break;
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
relationship_get_property (GObject *object, guint property_id,
				 GValue *value, GParamSpec *pspec)
{
	Relationship *element = (Relationship*) object;

	switch (property_id) {
	case PROP_SUBJECT:
		if (element->subject) {
			Py_INCREF (element->subject);
			g_value_set_pointer (value, element->subject);
		} else {
			Py_INCREF (Py_None);
			g_value_set_pointer (value, Py_None);
		}
		break;
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
relationship_dispose (GObject *object)
{
	Relationship *element = (Relationship*) object;

	if (element->subject) {
		relationship_unset_subject (element);
	}

	G_OBJECT_CLASS (parent_class)->dispose (object);
}	

static void
relationship_update (DiaCanvasItem *item, gdouble affine[6])
{
	PyObject *wrapper;

	g_assert (RELATIONSHIP(item)->subject != NULL);
	wrapper = pygobject_new (G_OBJECT (item));
	Py_DECREF (wrapper);

	//g_message (__FUNCTION__": model-element ref %d (GObject: %d)",
	//	   wrapper->ob_refcnt, G_OBJECT (item)->ref_count);
	//g_message (__FUNCTION__": subject ref %d (%x)",
	//	   RELATIONSHIP(item)->subject->ob_refcnt,
	//	   RELATIONSHIP(item)->subject);

	DIA_CANVAS_ITEM_CLASS (parent_class)->update (item, affine);
}

static void
relationship_handle_motion (DiaCanvasItem *item, DiaHandle *handle,
			     gdouble *wx, gdouble *wy, DiaEventMask mask)
{
	DIA_CANVAS_ITEM_CLASS (parent_class)->handle_motion (item, handle,
							     wx, wy, mask);
}

static gdouble
relationship_glue (DiaCanvasItem *item, DiaHandle *handle,
		   gdouble *wx, gdouble *wy)
{
	gdouble res = G_MAXDOUBLE;

	if (IS_COMMENT_LINE (handle->owner)
	    && comment_line_handle_glue (COMMENT_LINE (handle->owner),
				         handle, item)) {
		res = DIA_CANVAS_ITEM_CLASS(parent_class)->glue (item, handle,
								 wx, wy);
	}
	return res;
}

static gboolean
relationship_connect (DiaCanvasItem *item, DiaHandle *handle)
{
	gboolean res = FALSE;

	if (IS_COMMENT_LINE (handle->owner)
	    && comment_line_handle_connect (COMMENT_LINE (handle->owner),
					    handle, item)) {
		res =  DIA_CANVAS_ITEM_CLASS(parent_class)->connect (item,
								     handle);
		g_assert (res == TRUE);
	}
	return res;
}

static gboolean
relationship_disconnect (DiaCanvasItem *item, DiaHandle *handle)
{
	gboolean res = FALSE;

	//if (IS_COMMENT_LINE (handle->owner)
	//    && comment_line_handle_disconnect (COMMENT_LINE (handle->owner),
	//				       handle)) {
		res = DIA_CANVAS_ITEM_CLASS(parent_class)->disconnect (item,
								       handle);
		g_assert (res == TRUE);
	//}
	return res;
}

static void
relationship_real_element_update (Relationship *relationship, const gchar* key)
{
	if (g_str_equal (key, "unlink")) {
		g_message (__FUNCTION__": Unlinking subject");
		relationship_unset_subject (relationship);
		relationship->subject = NULL;
	}
}

void
relationship_element_update (Relationship *relationship, const gchar *key)
{
	RelationshipClass *klass;

	klass = RELATIONSHIP_GET_CLASS (relationship);
	if (klass->element_update)
		klass->element_update (relationship, key);
}

