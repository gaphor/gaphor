/*
 * Classifier
 *
 * This is LGPL'ed code.
 */

#include "classifier.h"
#include "generalization.h"
#include "realization.h"
#include "dependency.h"
#include "common.h"
#include <diacanvas/dia-shape.h>
#include <diacanvas/dia-canvas-i18n.h>

static void classifier_class_init (ClassifierClass *klass);
static void classifier_init (Classifier *item);
static void classifier_dispose (GObject *object);
static void classifier_set_property (GObject *object,
					     guint property_id,
					     const GValue *value,
					     GParamSpec *pspec);
static void classifier_get_property (GObject *object,
					     guint property_id,
					     GValue *value,
					     GParamSpec *pspec);
static gdouble classifier_glue (DiaCanvasItem *item, DiaHandle *handle,
				gdouble *wx, gdouble *wy);
static gboolean classifier_connect (DiaCanvasItem *item, DiaHandle *handle);
static gboolean classifier_disconnect (DiaCanvasItem *item, DiaHandle *handle);

static void classifier_parent_notify (ModelElement *me);

static ModelElementClass *parent_class = NULL;

GType
classifier_get_type (void)
{
	static GType object_type = 0;

	if (!object_type) {
		static const GTypeInfo object_info = {
			sizeof (ClassifierClass),
			(GBaseInitFunc) NULL,
			(GBaseFinalizeFunc) NULL,
			(GClassInitFunc) classifier_class_init,
			(GClassFinalizeFunc) NULL,
			(gconstpointer) NULL, /* class_data */
			sizeof (Classifier),
			(guint16) 0, /* n_preallocs */
			(GInstanceInitFunc) classifier_init,
		};

		object_type = g_type_register_static (TYPE_MODEL_ELEMENT,
						      "Classifier",
						      &object_info, 0);
	}

	return object_type;
}


static void
classifier_class_init (ClassifierClass *klass)
{
	GObjectClass *object_class;
	DiaCanvasItemClass *item_class;
	
	object_class = (GObjectClass*) klass;
	item_class = DIA_CANVAS_ITEM_CLASS (klass);
	
	parent_class = g_type_class_peek_parent (klass);

	object_class->dispose = classifier_dispose;
	object_class->get_property = classifier_get_property;
	object_class->set_property = classifier_set_property;
	
	item_class->glue = classifier_glue;
	item_class->connect = classifier_connect;
	item_class->disconnect = classifier_disconnect;
}


static void
classifier_init (Classifier *item)
{
	//item->old_namespace = NULL;

	//g_signal_connect (G_OBJECT (item), "notify::parent",
	//		  G_CALLBACK (classifier_parent_notify), NULL);
}


static void
classifier_set_property (GObject *object, guint property_id,
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
classifier_get_property (GObject *object, guint property_id,
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
classifier_dispose (GObject *object)
{
	Classifier *c = (Classifier*) object;
/*
	if (c->old_namespace) {
		PyObject *old_namespace = c->old_namespace;
		c->old_namespace = NULL;
		Py_DECREF (old_namespace);
		if (MODEL_ELEMENT (object)->subject) {
			PyObject *result = PyObject_CallMethod
					(MODEL_ELEMENT (object)->subject,
					 "remove_undoability", NULL);
			if (result)
				Py_DECREF (result);
			else {
				PyErr_Print();
				PyErr_Clear();
			}
		}
	} */

	G_OBJECT_CLASS (parent_class)->dispose (object);
}

static gdouble
classifier_glue (DiaCanvasItem *item, DiaHandle *handle,
		 gdouble *wx, gdouble *wy)
{
	gdouble result = G_MAXDOUBLE;

	if ((IS_GENERALIZATION (handle->owner)
	     || IS_DEPENDENCY (handle->owner)
	     || IS_REALIZATION (handle->owner))
	    && relationship_handle_glue (RELATIONSHIP (handle->owner),
		    			 handle, item)) {
		/* Skip the ModelElement::glue() function, since it will only
		 * allow comments to be connected. */
		DiaCanvasElementClass *element_class;

		element_class = g_type_class_ref (DIA_TYPE_CANVAS_ELEMENT);
		result = DIA_CANVAS_ITEM_CLASS (element_class)->glue (item, handle, wx, wy);

		g_type_class_unref (element_class);
	} else
		result = DIA_CANVAS_ITEM_CLASS (parent_class)->glue (item, handle, wx, wy);
	return result;
}

static gboolean
classifier_connect (DiaCanvasItem *item, DiaHandle *handle)
{
	gboolean result = FALSE;

	if ((IS_GENERALIZATION (handle->owner)
	     || IS_DEPENDENCY (handle->owner)
	     || IS_REALIZATION (handle->owner))
	    && relationship_handle_connect (RELATIONSHIP (handle->owner),
					    handle, item)) {
		DiaCanvasElementClass *element_class;
		element_class = g_type_class_ref (DIA_TYPE_CANVAS_ELEMENT);
		result = DIA_CANVAS_ITEM_CLASS (element_class)->connect (item, handle);

		g_type_class_unref (element_class);
	} else
		result = DIA_CANVAS_ITEM_CLASS (parent_class)->connect (item, handle);
	return result;
}

static gboolean
classifier_disconnect (DiaCanvasItem *item, DiaHandle *handle)
{
	return DIA_CANVAS_ITEM_CLASS (parent_class)->disconnect (item, handle);
}

#if 0
/**
 * classifier_parent_notify:
 * @me: 
 *
 * This notifier is called when the 'parent' of item @me is changed. It
 * removes the namespace attribute from @me's subject if no more presentation
 * elements are active.
 *
 * TODO: How should we handle the case where no more items point to the
 * subject directly (they are i the subject.presentation list), but it
 * is still referenced from the undo stack. If the undo stack 
 **/
static void
classifier_parent_notify (ModelElement *me)
{
	PyObject *wrapper;
	PyObject *namespace;
	int refcnt;

	if (!me->subject)
		return;

	wrapper = pygobject_new (G_OBJECT (me));
	g_assert (wrapper != NULL && wrapper != Py_None);
	refcnt = wrapper->ob_refcnt;

	namespace = PyObject_GetAttrString (me->subject, "namespace");

	if (DIA_CANVAS_ITEM (me)->parent
	    && DIA_CANVAS_ITEM (me)->canvas->in_undo) {
		g_message (__FUNCTION__": reseting parent");
		/* reset the old namespace value... */
		if (namespace == Py_None &&  CLASSIFIER (me)->old_namespace)
			PyObject_SetAttrString (me->subject, "namespace",
						CLASSIFIER (me)->old_namespace);
		Py_XDECREF (CLASSIFIER (me)->old_namespace);
		CLASSIFIER (me)->old_namespace = NULL;
		g_assert (wrapper->ob_refcnt = refcnt + 1);
	} else if (!(DIA_CANVAS_ITEM (me)->parent
		     && DIA_CANVAS_ITEM (me)->canvas->in_undo)) {
		PyObject *presentation;

		g_message (__FUNCTION__": no more parent");
		presentation = PyObject_GetAttrString (me->subject,
						       "presentation");
		CLASSIFIER (me)->old_namespace = namespace;
		Py_INCREF (namespace);

		if (PySequence_Length (presentation) == 0) {
			/* Set namespace to None */
			g_message (__FUNCTION__": Set namespace to None");
			PyObject_DelAttrString (me->subject, "namespace");
		}
		Py_DECREF (presentation);
		g_assert (wrapper->ob_refcnt = refcnt - 1); // pres + ns
	}
	Py_DECREF (namespace);
	Py_DECREF (wrapper);

	g_message (__FUNCTION__": Parent is set to %p (refcnt = %d)", DIA_CANVAS_ITEM (me)->parent, G_OBJECT (me)->ref_count);
}
#endif
