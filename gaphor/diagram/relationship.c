/*
 * Relationship
 *
 * This is LGPL'ed code.
 */

#include "relationship.h"
#include "comment-line.h"
#include "common.h"
#include <diacanvas/dia-canvas-i18n.h>
#include <stdio.h>

enum {
	PROP_SUBJECT = 1,
	PROP_INTERNAL_SUBJECT
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
static void relationship_parent_notify (Relationship *rel);
static gboolean relationship_handle_disconnect (DiaCanvasItem *connected_to,
						DiaHandle *handle,
						Relationship *rel);

static DiaCanvasLineClass *parent_class = NULL;

/*
 * TYPE_RELATIONSHIP_SUBJECT
 */
#define TYPE_RELATIONSHIP_SUBJECT (relationship_subject_get_type ())

static gpointer
relationship_subject_copy (gpointer p)
{
	if (p && p != Py_None) {
		//g_message (__FUNCTION__);
		if (p != Py_None)
			subject_add_undoability (p);
		Py_INCREF ((PyObject*) p);
	}
	return p;
}

static void
relationship_subject_free (gpointer p)
{
	if (p) {
		//g_message (__FUNCTION__);
		if (p != Py_None)
			subject_remove_undoability (p);
		Py_DECREF ((PyObject*) p);
	}
}

GType
relationship_subject_get_type (void)
{
	static GType type = 0;

	if (!type) {
		type = g_boxed_type_register_static ("RelationshipSubject",
						     relationship_subject_copy,
						     relationship_subject_free);
	}
	return type;
}

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
	g_object_class_install_property (object_class,
					 PROP_INTERNAL_SUBJECT,
					 g_param_spec_boxed ("internal_subject",
						_("Internal subject"),
						_("Internal subject"),
						TYPE_RELATIONSHIP_SUBJECT,
						G_PARAM_READWRITE));

	klass->subject_class = NULL;
	klass->head_name = NULL;
	klass->tail_name = NULL;
	klass->head_xname = NULL;
	klass->tail_xname = NULL;
}


static void
relationship_init (Relationship *item)
{
	item->subject = NULL;
	item->head_disconnect_id = 0;
	item->tail_disconnect_id = 0;

	g_signal_connect (G_OBJECT (item), "notify::parent",
			  G_CALLBACK (relationship_parent_notify), NULL);

}

#define relationship_unset_subject(rel) \
	_unset_subject (DIA_CANVAS_ITEM(rel), &(RELATIONSHIP(rel)->subject))

static void
relationship_set_subject (Relationship *rel, PyObject *subject)
{
	if (subject == rel->subject)
		return;

	dia_canvas_item_preserve_property (DIA_CANVAS_ITEM (rel),
					   "internal_subject");
	if (rel->subject) {
		PyObject *self = pygobject_new (G_OBJECT (rel));

		//g_message (__FUNCTION__": (%p) if (rel->subject)", rel);
		/* subject.disconnect(self.rel_update) */
		subject_disconnect_element_update (rel->subject, self);
		subject_remove_presentation_undoable (rel->subject, self);
		/* Remove the undoability bit from the Relationship (it should
		 * be held by the element on the undo stack) */
		//if (DIA_CANVAS_ITEM (rel)->canvas->allow_undo)
		subject_remove_undoability (rel->subject);
		Py_DECREF (self);
		Py_DECREF (rel->subject);
		rel->subject = NULL;
	}

	if (subject && subject != Py_None) {
		PyObject *self = pygobject_new (G_OBJECT (rel));

		//g_message (__FUNCTION__": if (subject)");
		rel->subject = subject;
		Py_INCREF (rel->subject);

		subject_connect_element_update (subject, self);
		if (DIA_CANVAS_ITEM (rel)->canvas->in_undo) {
			/* Add extra undo-counter, since undo_presentation
			 * decrements the counter. */
			//if (DIA_CANVAS_ITEM (rel)->canvas->allow_undo)
			subject_add_undoability (subject);
			subject_undo_presentation (subject, self);
		} else
			subject_add_presentation (subject, self);
		Py_DECREF (self);
	}
	dia_canvas_item_request_update (DIA_CANVAS_ITEM (rel));
}

static void
relationship_set_property (GObject *object, guint property_id,
			   const GValue *value, GParamSpec *pspec)
{
	Relationship *rel = (Relationship*) object;
	PyObject *subject;
	PyObject *pyobj;
	int result;

	switch (property_id) {
	case PROP_SUBJECT:
		subject = g_value_get_pointer (value);
		relationship_set_subject (RELATIONSHIP (object), subject);
		break;
	case PROP_INTERNAL_SUBJECT:
		/* Steal the value -> no reference increment */
		subject = g_value_get_boxed (value);
		relationship_set_subject (RELATIONSHIP (object), subject);
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
	Relationship *rel = (Relationship*) object;

	switch (property_id) {
	case PROP_INTERNAL_SUBJECT:
		if (rel->subject) {
			/* Prevent the subject from setting an extra
			 * undoItemStack entry. */
			//g_value_set_boxed_take_ownership (value, rel->subject);
			g_value_set_boxed (value, rel->subject);
		} else {
			g_value_set_boxed (value, NULL);
		}
		break;
	case PROP_SUBJECT:
		if (rel->subject) {
			Py_INCREF (rel->subject);
			g_value_set_pointer (value, rel->subject);
		} else {
			Py_INCREF (Py_None);
			g_value_set_pointer (value, Py_None);
		}
	default:
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}

static void
relationship_dispose (GObject *object)
{
	Relationship *rel = (Relationship*) object;

	if (rel->subject) {
		relationship_unset_subject (rel);
	}
	rel->head_disconnect_id = 0;
	rel->tail_disconnect_id = 0;

	G_OBJECT_CLASS (parent_class)->dispose (object);
}	

static void
relationship_update (DiaCanvasItem *item, gdouble affine[6])
{
	/* We can so something nice with stereotypes here... */

	DIA_CANVAS_ITEM_CLASS (parent_class)->update (item, affine);
}

static void
relationship_handle_motion (DiaCanvasItem *item, DiaHandle *handle,
			     gdouble *wx, gdouble *wy, DiaEventMask mask)
{
	DIA_CANVAS_ITEM_CLASS (parent_class)->handle_motion (item, handle,
							     wx, wy, mask);
}

static void
relationship_parent_notify (Relationship *rel)
{
	PyObject *self;
	PyObject *child;
	PyObject *parent;

	if (!rel->subject)
		return;

	self = pygobject_new (G_OBJECT (rel));
	g_assert (self != NULL && self != Py_None);

	if (DIA_CANVAS_ITEM (rel)->parent
	    && DIA_CANVAS_ITEM (rel)->canvas->in_undo) {
		/* Object is undone */
	} else if (!(DIA_CANVAS_ITEM (rel)->parent
		     && DIA_CANVAS_ITEM (rel)->canvas->in_undo)) {
		/* Object is removed from the canvas */
	}
	Py_DECREF (self);
}

static gdouble
relationship_glue (DiaCanvasItem *item, DiaHandle *handle,
		   gdouble *wx, gdouble *wy)
{
	if (IS_COMMENT_LINE (handle->owner)
	    && comment_line_handle_glue (COMMENT_LINE (handle->owner),
				         handle, item)) {
		return DIA_CANVAS_ITEM_CLASS(parent_class)->glue (item, handle,
								  wx, wy);
	}
	return G_MAXDOUBLE;
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

	res = DIA_CANVAS_ITEM_CLASS(parent_class)->disconnect (item,
							       handle);
	g_assert (res == TRUE);
	return res;
}

static void
relationship_real_element_update (Relationship *relationship, const gchar* key)
{
	if (g_str_equal (key, "unlink")) {
		//g_message (__FUNCTION__": Unlinking subject");
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

gboolean
relationship_handle_glue (Relationship *rel, DiaHandle *handle,
			  DiaCanvasItem *gluing_to)
{
	DiaHandle *head, *tail;
	DiaCanvasItem *head_item, *tail_item;
	PyObject *head_subject, *tail_subject;

	head = g_list_first (DIA_CANVAS_ITEM (rel)->handles)->data;
	tail = g_list_last (DIA_CANVAS_ITEM (rel)->handles)->data;

	if (handle == head) {
		if (!tail->connected_to)
			return TRUE;
		head_item = gluing_to;
		tail_item = tail->connected_to;
	} else if (handle == tail) {
		if (!head->connected_to)
			return TRUE;
		head_item = head->connected_to;
		tail_item = gluing_to;
	} else
		g_assert_not_reached ();

	g_object_get (head_item, "subject", &head_subject, NULL);
	g_assert (head_subject != NULL);
	Py_DECREF (head_subject);
	g_object_get (tail_item, "subject", &tail_subject, NULL);
	g_assert (tail_subject != NULL);
	Py_DECREF (tail_subject);

	return (head_subject != tail_subject);
}

static gboolean
relationship_handle_disconnect (DiaCanvasItem *connected_to,
				DiaHandle *handle, Relationship *rel)
{
	DiaHandle *head, *tail;

	if (!g_list_find (DIA_CANVAS_ITEM (rel)->handles, handle))
		return TRUE;

	head = g_list_first (DIA_CANVAS_ITEM (rel)->handles)->data;
	tail = g_list_last (DIA_CANVAS_ITEM (rel)->handles)->data;

	if (rel->head_disconnect_id) {
		g_signal_handler_disconnect (head->connected_to,
					     rel->head_disconnect_id);
		rel->head_disconnect_id = 0;
	}
	if (rel->tail_disconnect_id) {
		g_signal_handler_disconnect (tail->connected_to,
					     rel->tail_disconnect_id);
		rel->tail_disconnect_id = 0;
	}

	//if (!head->connected_to || !tail->connected_to)
	//	return TRUE;

	g_assert (head->connected_to != NULL);
	g_assert (tail->connected_to != NULL);

	//g_message (__FUNCTION__": Going to disconnect subject...");
	relationship_set_subject (rel, NULL);

	return TRUE;
}

/**
 * find_relationship:
 * @me: Element that owns the relationship (a ModelElement)
 * @attr_name: name of the relationship field from @me's point of view.
 * @obj_to_look_for: Object on the other end of the relationship
 * @rel_name: Relationship attribute the @obj_to_look_for should be
 * connected to.
 *
 * Find an already existing relationship between @me and @obj_to_look_for.
 * If none is found, NULL is returned.
 *
 * Return value: The 
 **/
static PyObject*
find_relationship (PyObject *me, const gchar *attr_name,
		   PyObject *obj_to_look_for, const gchar *rel_name)
{
	PyObject *me_attr;
	gint attr_len, i;
	PyObject *result = NULL;

	me_attr = PyObject_GetAttrString (me, (char*) attr_name);
	g_assert (me_attr != NULL && PySequence_Check (me_attr));

	attr_len = PySequence_Length (me_attr);
	for (i = 0; i < attr_len && !result; i++) {
		PyObject *item, *subject_attr;
		
		item = PySequence_GetItem (me_attr, i);
		subject_attr = PyObject_GetAttrString (item, (char*) rel_name);
		g_assert (subject_attr != NULL);

		if (subject_attr == obj_to_look_for) {
			result = item;
			Py_INCREF (result);
		}

		Py_DECREF (subject_attr);
		Py_DECREF (item);
	}
	Py_DECREF (me_attr);

	return result;
}

gboolean
relationship_handle_connect (Relationship *rel, DiaHandle *handle,
			     DiaCanvasItem *connecting_to)
{
	RelationshipClass *klass = RELATIONSHIP_GET_CLASS (rel);
	PyObject *self;
	DiaHandle *head, *tail;
	DiaCanvasItem *head_item, *tail_item;
	PyObject *head_subject, *tail_subject;
	PyObject *py_rel = NULL;

	//g_message (__FUNCTION__);

	self = pygobject_new (G_OBJECT (rel));

	head = g_list_first (DIA_CANVAS_ITEM (rel)->handles)->data;
	tail = g_list_last (DIA_CANVAS_ITEM (rel)->handles)->data;

	if (handle == head) {
		head_item = connecting_to;
		tail_item = tail->connected_to;
	} else if (handle == tail) {
		head_item = head->connected_to;
		tail_item = connecting_to;
	} else
		g_assert_not_reached ();

	if (!head_item || !tail_item) {
		//g_message (__FUNCTION__": Do not connect...");
		return TRUE;
	}

	/* Do a disconnect if the head or tail is disconnected: */
	rel->head_disconnect_id = g_signal_connect (head_item, "disconnect",
			G_CALLBACK (relationship_handle_disconnect), rel);
	rel->tail_disconnect_id = g_signal_connect (tail_item, "disconnect",
			G_CALLBACK (relationship_handle_disconnect), rel);

	g_object_get (head_item, "subject", &head_subject, NULL);
	g_assert (head_subject != NULL);
	g_object_get (tail_item, "subject", &tail_subject, NULL);
	g_assert (tail_subject != NULL);

	/* First check if we already have a subject and, if so,
	 * check if the ends match and if they match, connect the CanvasItem
	 * and do nothing more. */
	if (rel->subject) {
		PyObject *hs, *ts;

		//g_message (__FUNCTION__": already have a subject...");
		hs = PyObject_GetAttrString (rel->subject, klass->head_name);
		g_assert (hs != NULL);
		ts = PyObject_GetAttrString (rel->subject, klass->tail_name);
		g_assert (ts != NULL);

		//g_message (__FUNCTION__": (%p) %p %p, %p %p, %p %p.", rel->subject, hs, ts, head_subject, tail_subject, head_item, tail_item);

		if ((hs == head_subject) && (ts == tail_subject)) {
			//g_message (__FUNCTION__": already have the right subject...");
			Py_DECREF (head_subject);
			Py_DECREF (tail_subject);
			Py_DECREF (hs);
			Py_DECREF (ts);
			Py_DECREF (self);
			return TRUE;
		}
		Py_DECREF (hs);
		Py_DECREF (ts);
	}

	/* Do a lookup for an already existing generalization between the
	 * elements. Do the lookup using the element connected to the tail,
	 * since this one is bi-directional on Include and Extend elements. */
	py_rel = find_relationship (tail_subject, klass->tail_xname,
				    head_subject, klass->head_name);
	
	//g_message (__FUNCTION__": py_rel = %p", py_rel);
	/* If a generalization already exists, use this one and approve the
	 * generalization. */
	if (py_rel) {
		//g_message (__FUNCTION__": Using existing relationship (%p)", py_rel);
		relationship_set_subject (rel, py_rel);
	} else {
		int res;
		/* Else, create a new Generalization object and connect that
		 * between the elements. */
		py_rel = create_uml_object (klass->subject_class);

		//g_message (__FUNCTION__": Creating a new relationship (%p)", py_rel);
		
		relationship_set_subject (rel, py_rel);

		res = PyObject_SetAttrString (head_subject, klass->head_xname, py_rel);
		g_assert (res == 0);
		res = PyObject_SetAttrString (tail_subject, klass->tail_xname, py_rel);
		g_assert (res == 0);
	}

	Py_DECREF (head_subject);
	Py_DECREF (tail_subject);
	if (py_rel)
		Py_DECREF (py_rel);
	Py_DECREF (self);
	return TRUE;
}

