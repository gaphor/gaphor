/*
 * ModelElement
 *
 * This is LGPL'ed code.
 */

#include "model-element.h"
#include "comment-line.h"
#include "common.h"
#include <diacanvas/dia-canvas-i18n.h>


#define model_element_set_subject(me, sj) \
	_set_subject (DIA_CANVAS_ITEM(me), sj, &(MODEL_ELEMENT(me)->subject))

#define model_element_unset_subject(me) \
	_unset_subject (DIA_CANVAS_ITEM(me), &(MODEL_ELEMENT(me)->subject))

enum {
	PROP_AUTO_RESIZE = 1,
	PROP_SUBJECT
};

static void model_element_class_init (ModelElementClass *klass);
static void model_element_init (ModelElement *item);
static void model_element_dispose (GObject *object);
static void model_element_set_property (GObject *object,
					guint property_id,
					const GValue *value,
					GParamSpec *pspec);
static void model_element_get_property (GObject *object,
					guint property_id,
					GValue *value,
					GParamSpec *pspec);
static void model_element_update (DiaCanvasItem *item, gdouble affine[6]);
static void model_element_handle_motion (DiaCanvasItem *item, DiaHandle *handle,
					 gdouble *wx, gdouble *wy,
					 DiaEventMask mask);
static gdouble model_element_glue (DiaCanvasItem *item, DiaHandle *handle,
				   gdouble *wx, gdouble *wy);
static gboolean model_element_connect (DiaCanvasItem *item,
				       DiaHandle *handle);
static gboolean model_element_disconnect (DiaCanvasItem *item,
					  DiaHandle *handle);
static void model_element_real_element_update (ModelElement *element, const gchar* key);

static void model_element_parent_notify (ModelElement *me);

static DiaCanvasElementClass *parent_class = NULL;

GType
model_element_get_type (void)
{
	static GType object_type = 0;

	if (!object_type) {
		static const GTypeInfo object_info = {
			sizeof (ModelElementClass),
			(GBaseInitFunc) NULL,
			(GBaseFinalizeFunc) NULL,
			(GClassInitFunc) model_element_class_init,
			(GClassFinalizeFunc) NULL,
			(gconstpointer) NULL, /* class_data */
			sizeof (ModelElement),
			(guint16) 0, /* n_preallocs */
			(GInstanceInitFunc) model_element_init,
		};

		object_type = g_type_register_static (DIA_TYPE_CANVAS_ELEMENT,
						      "ModelElement",
						      &object_info,
						      G_TYPE_FLAG_ABSTRACT);
	}

	return object_type;
}


static void
model_element_class_init (ModelElementClass *klass)
{
	GObjectClass *object_class;
	DiaCanvasItemClass *item_class;
	
	object_class = (GObjectClass*) klass;
	item_class = (DiaCanvasItemClass*) klass;
	
	parent_class = g_type_class_peek_parent (klass);

	object_class->dispose = model_element_dispose;
	object_class->get_property = model_element_get_property;
	object_class->set_property = model_element_set_property;
	item_class->update = model_element_update;
	item_class->handle_motion = model_element_handle_motion;
	item_class->glue = model_element_glue;
	item_class->connect = model_element_connect;
	item_class->disconnect = model_element_disconnect;
	klass->element_update = model_element_real_element_update;

	g_object_class_install_property (object_class,
					 PROP_AUTO_RESIZE,
					 g_param_spec_boolean ("auto_resize",
						_("Auto resize"),
						_("Auto resize"),
						TRUE,
						G_PARAM_READWRITE));
	g_object_class_install_property (object_class,
					 PROP_SUBJECT,
					 g_param_spec_pointer ("subject",
						_("Subject"),
						_("Subject"),
						G_PARAM_READWRITE));
}


static void
model_element_init (ModelElement *item)
{
	item->subject = NULL;
	item->auto_resize = TRUE;
	item->need_resize = TRUE;

	g_signal_connect (G_OBJECT (item), "notify::parent",
			  G_CALLBACK (model_element_parent_notify), NULL);
}


static void
model_element_set_property (GObject *object, guint property_id,
			    const GValue *value, GParamSpec *pspec)
{
	ModelElement *element = (ModelElement*) object;
	PyObject *subject;

	switch (property_id) {
	case PROP_AUTO_RESIZE:
		element->auto_resize = g_value_get_boolean (value);
		if (element->auto_resize) {
			element->need_resize = TRUE;
			dia_canvas_item_request_update (DIA_CANVAS_ITEM (element));
		}
		break;
	case PROP_SUBJECT:
		subject = g_value_get_pointer (value);
		g_message (__FUNCTION__": subject");
		if (element->subject) {
			g_warning ("This diagram item already has "
				   "a subject assigned to it");
			return;
		}
		model_element_set_subject (element, subject);
		dia_canvas_item_request_update (DIA_CANVAS_ITEM (element));
		break;
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
model_element_get_property (GObject *object, guint property_id,
				 GValue *value, GParamSpec *pspec)
{
	ModelElement *element = (ModelElement*) object;

	switch (property_id) {
	case PROP_AUTO_RESIZE:
		g_value_set_boolean (value, element->auto_resize);
		break;
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
model_element_dispose (GObject *object)
{
	ModelElement *element = (ModelElement*) object;

	if (element->subject)
		model_element_unset_subject (element);

	G_OBJECT_CLASS (parent_class)->dispose (object);
}	

static void
model_element_update (DiaCanvasItem *item, gdouble affine[6])
{
	PyObject *wrapper;

	g_assert (MODEL_ELEMENT(item)->subject != NULL);
	wrapper = pygobject_new (G_OBJECT (item));
	Py_DECREF (wrapper);

	//g_message (__FUNCTION__": model-element ref %d (GObject: %d)",
	//	   wrapper->ob_refcnt, G_OBJECT (item)->ref_count);
	//g_message (__FUNCTION__": subject ref %d (%x)",
	//	   MODEL_ELEMENT(item)->subject->ob_refcnt,
	//	   MODEL_ELEMENT(item)->subject);

	DIA_CANVAS_ITEM_CLASS (parent_class)->update (item, affine);

	MODEL_ELEMENT(item)->need_resize = FALSE;
}

static void
model_element_handle_motion (DiaCanvasItem *item, DiaHandle *handle,
			     gdouble *wx, gdouble *wy, DiaEventMask mask)
{
	//MODEL_ELEMENT (item)->auto_resize = FALSE;

	DIA_CANVAS_ITEM_CLASS (parent_class)->handle_motion (item, handle,
							     wx, wy, mask);
}

static gdouble
model_element_glue (DiaCanvasItem *item, DiaHandle *handle,
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
model_element_connect (DiaCanvasItem *item, DiaHandle *handle)
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
model_element_disconnect (DiaCanvasItem *item, DiaHandle *handle)
{
	gboolean res = FALSE;

	res = DIA_CANVAS_ITEM_CLASS(parent_class)->disconnect (item,
							       handle);
	g_assert (res == TRUE);

	return res;
}

static void
model_element_real_element_update (ModelElement *element, const gchar* key)
{
	if (g_str_equal (key, "unlink")) {
		g_message (__FUNCTION__": Unlinking subject");
		model_element_unset_subject (element);
		element->subject = NULL;
	}
}

void
model_element_element_update (ModelElement *element, const gchar *key)
{
	ModelElementClass *klass;

	klass = MODEL_ELEMENT_GET_CLASS (element);
	if (klass->element_update)
		klass->element_update (element, key);
}

static void
model_element_parent_notify (ModelElement *me)
{
	PyObject *wrapper;
	PyObject *result;

	if (!me->subject)
		return;

	wrapper = pygobject_new (G_OBJECT (me));
	g_assert (wrapper != NULL && wrapper != Py_None);

	if (DIA_CANVAS_ITEM (me)->parent) {
		subject_undo_presentation (me->subject, wrapper);
	} else {
		subject_remove_presentation_undoable (me->subject, wrapper);
	}
	Py_DECREF (wrapper);
}

