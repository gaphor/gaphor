/* -*- Mode: C; c-basic-offset: 4 -*- */

#include "treemodel.h"
#include <Python.h>
#include "pygobject.h"

/* define this to print out debug messages */
#undef DEBUG_TREE_MODEL

#ifndef _
# define _(s) (s)
#endif

static void tree_model_class_init(TreeModelClass *klass);
static void tree_model_init(TreeModel *self);
static void tree_model_iface_init(GtkTreeModelIface *iface);

static void tree_model_set_property (GObject *object,
				     guint property_id,
				     const GValue *value,
				     GParamSpec *pspec);
static void tree_model_get_property (GObject *object,
				     guint property_id,
				     GValue *value,
				     GParamSpec *pspec);

GType
tree_model_get_type(void)
{
    static GType object_type = 0;

    if (!object_type) {
	static const GTypeInfo object_info = {
	    sizeof(TreeModelClass),
	    (GBaseInitFunc) NULL,
	    (GBaseFinalizeFunc) NULL,
	    (GClassInitFunc) tree_model_class_init,
	    NULL, /* class_finalize */
	    NULL, /* class_data */
	    sizeof(TreeModel),
	    0, /* n_preallocs */
	    (GInstanceInitFunc) tree_model_init,
	};
	static const GInterfaceInfo tree_model_info = {
	    (GInterfaceInitFunc) tree_model_iface_init,
	    NULL,
	    NULL,
	};

	object_type = g_type_register_static(G_TYPE_OBJECT,
					     "TreeModel",
					     &object_info, 0);
	g_type_add_interface_static(object_type,
				    GTK_TYPE_TREE_MODEL,
				    &tree_model_info);
    }
    return object_type;
}

static void
tree_model_class_init(TreeModelClass *klass)
{
    GObjectClass *object_class = (GObjectClass*) klass;

    object_class->get_property = tree_model_get_property;
    object_class->set_property = tree_model_set_property;
}

static guint tree_model_get_flags(GtkTreeModel *tree_model);
static gint tree_model_get_n_columns(GtkTreeModel *tree_model);
static GType tree_model_get_column_type(GtkTreeModel *tree_model,
					      gint index);
static gboolean tree_model_get_iter(GtkTreeModel *tree_model,
					  GtkTreeIter *iter,
					  GtkTreePath *path);
static GtkTreePath *tree_model_get_path(GtkTreeModel *tree_model,
					      GtkTreeIter *iter);
static void tree_model_get_value(GtkTreeModel*tree_model,
				       GtkTreeIter *iter,
				       gint column, GValue *value);
static gboolean tree_model_iter_next(GtkTreeModel *tree_model,
					   GtkTreeIter *iter);
static gboolean tree_model_iter_children(GtkTreeModel *tree_model,
					       GtkTreeIter *iter,
					       GtkTreeIter *parent);
static gboolean tree_model_iter_has_child(GtkTreeModel *tree_model,
						GtkTreeIter *iter);
static gint tree_model_iter_n_children(GtkTreeModel *tree_model,
					     GtkTreeIter *iter);
static gboolean tree_model_iter_nth_child(GtkTreeModel *tree_model,
						GtkTreeIter  *iter,
						GtkTreeIter  *parent,
						gint n);
static gboolean tree_model_iter_parent(GtkTreeModel *tree_model,
					     GtkTreeIter *iter,
					     GtkTreeIter *child);

static void
tree_model_iface_init(GtkTreeModelIface *iface)
{
  iface->get_flags = tree_model_get_flags;
  iface->get_n_columns = tree_model_get_n_columns;
  iface->get_column_type = tree_model_get_column_type;
  iface->get_iter = tree_model_get_iter;
  iface->get_path = tree_model_get_path;
  iface->get_value = tree_model_get_value;
  iface->iter_next = tree_model_iter_next;
  iface->iter_children = tree_model_iter_children;
  iface->iter_has_child = tree_model_iter_has_child;
  iface->iter_n_children = tree_model_iter_n_children;
  iface->iter_nth_child = tree_model_iter_nth_child;
  iface->iter_parent = tree_model_iter_parent;
}

static void
tree_model_init(TreeModel *self)
{
}

static void
tree_model_set_property (GObject *object, guint property_id,
				       const GValue *value, GParamSpec *pspec)
{
    switch (property_id) {
    default:
	G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
	break;
    }
}

static void
tree_model_get_property (GObject *object, guint property_id,
				       GValue *value, GParamSpec *pspec)
{
    switch (property_id) {
    default:
	G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
	break;
    }
}

TreeModel *
tree_model_new(void)
{
    return TREE_MODEL(g_object_new(TYPE_TREE_MODEL, NULL));
}

static PyObject *
tree_path_to_pyobject(GtkTreePath *path)
{
    gint len, i, *indices;
    PyObject *ret;

    len = gtk_tree_path_get_depth(path);
    indices = gtk_tree_path_get_indices(path);
    ret = PyTuple_New(len);
    for (i = 0; i < len; i++)
	PyTuple_SetItem(ret, i, PyInt_FromLong(indices[i]));
    return ret;
}

static GtkTreePath *
tree_path_from_pyobject(PyObject *object)
{
    if (PyTuple_Check(object)) {
	GtkTreePath *path;
	guint len, i;

	len = PyTuple_Size(object);
	if (len < 1)
	    return NULL;
	path = gtk_tree_path_new();
	for (i = 0; i < len; i++) {
	    PyObject *item = PyTuple_GetItem(object, i);
	    gint index = PyInt_AsLong(item);
	    if (PyErr_Occurred()) {
		gtk_tree_path_free(path);
		    PyErr_Clear();
		    return NULL;
	    }
	    gtk_tree_path_append_index(path, index);
	}
	return path;
    }
    return NULL;
}

/* format of GtkTreeIter's for TreeModel:
 *  user_data == python object
 *  user_data2 == floating reference?
 *
 * I haven't worked out how everything should work.  For now I will
 * leak references.
 */

#define METHOD_PREFIX "on_"

static guint
tree_model_get_flags(GtkTreeModel *tree_model)
{
    PyObject *self, *py_ret;

    g_return_val_if_fail(IS_TREE_MODEL(tree_model), 0);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("get_flags()");
#endif
    py_ret = PyObject_CallMethod(self, METHOD_PREFIX "get_flags", "");
    if (py_ret) {
	guint ret = PyInt_AsLong(py_ret);

	Py_DECREF(py_ret);
	return ret;
    } else {
	PyErr_Print();
	PyErr_Clear();
	return 0;
    }
}

static gint
tree_model_get_n_columns(GtkTreeModel *tree_model)
{
    PyObject *self, *py_ret;

    g_return_val_if_fail(tree_model != NULL, 0);
    g_return_val_if_fail(IS_TREE_MODEL(tree_model), 0);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("get_n_columns()");
#endif
    py_ret = PyObject_CallMethod(self, METHOD_PREFIX "get_n_columns", "");
    if (py_ret) {
	gint ret = PyInt_AsLong(py_ret);

	Py_DECREF(py_ret);
	return ret;
    } else {
	PyErr_Print();
	PyErr_Clear();
	return 0;
    }
}

static GType
tree_model_get_column_type(GtkTreeModel *tree_model, gint index)
{
    PyObject *self, *py_ret;

    g_return_val_if_fail(tree_model != NULL, G_TYPE_INVALID);
    g_return_val_if_fail(IS_TREE_MODEL(tree_model), G_TYPE_INVALID);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("get_column_type(%d)", index);
#endif
    py_ret = PyObject_CallMethod(self, METHOD_PREFIX "get_column_type",
				 "(i)", index);
    if (py_ret) {
	GType ret = pyg_type_from_object(py_ret);

	Py_DECREF(py_ret);
	return ret;
    } else {
	PyErr_Print();
	PyErr_Clear();
	return G_TYPE_INVALID;
    }
}

static gboolean
tree_model_get_iter(GtkTreeModel *tree_model,
			  GtkTreeIter *iter, GtkTreePath *path)
{
    PyObject *self, *py_path, *py_ret;

    g_return_val_if_fail(tree_model != NULL, FALSE);
    g_return_val_if_fail(IS_TREE_MODEL(tree_model), FALSE);
    g_return_val_if_fail(iter != NULL, FALSE);
    g_return_val_if_fail(path != NULL, FALSE);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("get_tree_iter(%p)", path);
#endif
    py_path = tree_path_to_pyobject(path);
    py_ret = PyObject_CallMethod(self, METHOD_PREFIX "get_iter",
				 "(O)", py_path);
    Py_DECREF(py_path);

    if (py_ret) {
	if (py_ret != Py_None) {
	    iter->user_data = py_ret;
	    Py_DECREF (py_ret);
	    return TRUE;
	} else {
	    iter->user_data = NULL;
	    Py_DECREF(py_ret);
	    return FALSE;
	}
    } else {
	PyErr_Print();
	PyErr_Clear();
	iter->user_data = NULL;
	return FALSE;
    }
}

static GtkTreePath *
tree_model_get_path(GtkTreeModel *tree_model, GtkTreeIter *iter)
{
    PyObject *self, *py_ret;

    g_return_val_if_fail(tree_model != NULL, NULL);
    g_return_val_if_fail(IS_TREE_MODEL(tree_model), NULL);
    g_return_val_if_fail(iter != NULL, NULL);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("get_tree_path(%p)", iter);
#endif
    py_ret = PyObject_CallMethod(self, METHOD_PREFIX "get_tree_path",
				 "(O)", (PyObject *)iter->user_data);
    if (py_ret) {
	GtkTreePath *path = tree_path_from_pyobject(py_ret);

	Py_DECREF(py_ret);
	return path;
    } else {
	PyErr_Print();
	PyErr_Clear();
	return NULL;
    }
}

static void
tree_model_get_value(GtkTreeModel*tree_model, GtkTreeIter *iter,
			   gint column, GValue *value)
{
    PyObject *self, *py_value;

    g_return_if_fail(tree_model != NULL);
    g_return_if_fail(IS_TREE_MODEL(tree_model));
    g_return_if_fail(iter != NULL);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("get_value(%p, %d)", iter, column);
    _PyObject_Dump (iter->user_data);
#endif
    /* init value to column type */
    g_value_init(value, tree_model_get_column_type(tree_model, column));


    py_value = PyObject_CallMethod(self, METHOD_PREFIX "get_value",
				   "(Oi)", (PyObject *)iter->user_data, column);

    if (py_value) {
	pyg_value_from_pyobject(value, py_value);
	Py_DECREF(py_value);
    } else {
	PyErr_Print();
	PyErr_Clear();
    }
}

static gboolean
tree_model_iter_next(GtkTreeModel *tree_model, GtkTreeIter *iter)
{
    PyObject *self, *py_ret;

    g_return_val_if_fail(tree_model != NULL, FALSE);
    g_return_val_if_fail(IS_TREE_MODEL(tree_model), FALSE);
    g_return_val_if_fail(iter != NULL, FALSE);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("iter_next(%p)", iter);
#endif
    py_ret = PyObject_CallMethod(self, METHOD_PREFIX "iter_next",
				 "(O)", (PyObject *)iter->user_data);
    if (py_ret) {
	if (py_ret != Py_None) {
	    /* XXXX handle reference counting here */
	    if (iter->user_data) {
		Py_DECREF ((PyObject*) iter->user_data);
	    }
	    iter->user_data = py_ret;
	    Py_DECREF(py_ret);
	    return TRUE;
	} else {
	    iter->user_data = NULL;
	    Py_DECREF(py_ret);
	    return FALSE;
	}
    } else {
	iter->user_data = NULL;
	PyErr_Print();
	PyErr_Clear();
	return FALSE;
    }
}

static gboolean
tree_model_iter_children(GtkTreeModel *tree_model, GtkTreeIter *iter,
			       GtkTreeIter *parent)
{
    PyObject *self, *py_ret, *py_parent = Py_None;

    g_return_val_if_fail(tree_model != NULL, FALSE);
    g_return_val_if_fail(IS_TREE_MODEL(tree_model), FALSE);
    g_return_val_if_fail(iter != NULL, FALSE);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("iter_children(%p, %p)", iter, parent);
#endif
    if (parent && parent->user_data)
	py_parent = (PyObject *)parent->user_data;
    py_ret = PyObject_CallMethod(self, METHOD_PREFIX "iter_children",
				 "(O)", py_parent);
    if (py_ret) {
	if (py_ret != Py_None) {
	    /* XXXX handle reference counting here */
	    iter->user_data = py_ret;
	    Py_DECREF(py_ret);
	    return TRUE;
	} else {
	    iter->user_data = NULL;
	    Py_DECREF(py_ret);
	    return FALSE;
	}
    } else {
	iter->user_data = NULL;
	PyErr_Print();
	PyErr_Clear();
	return FALSE;
    }
}

static gboolean
tree_model_iter_has_child(GtkTreeModel *tree_model, GtkTreeIter *iter)
{
    PyObject *self, *py_ret;

    g_return_val_if_fail(tree_model != NULL, FALSE);
    g_return_val_if_fail(IS_TREE_MODEL(tree_model), FALSE);
    g_return_val_if_fail(iter != NULL, FALSE);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("iter_has_child(%p)", iter);
#endif
    py_ret = PyObject_CallMethod(self, METHOD_PREFIX "iter_has_child",
				 "(O)", (PyObject *)iter->user_data);
    if (py_ret) {
	gboolean ret = PyObject_IsTrue(py_ret);

	Py_DECREF(py_ret);
	return ret;
    } else {
	PyErr_Print();
	PyErr_Clear();
	return FALSE;
    }
}

static gint
tree_model_iter_n_children(GtkTreeModel *tree_model, GtkTreeIter *iter)
{
    PyObject *self, *py_ret;

    g_return_val_if_fail(tree_model != NULL, FALSE);
    g_return_val_if_fail(IS_TREE_MODEL(tree_model), FALSE);
    g_return_val_if_fail(iter != NULL, FALSE);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("iter_n_children(%p)", iter);
#endif
    py_ret = PyObject_CallMethod(self, METHOD_PREFIX "iter_n_children",
				 "(O)", (PyObject *)iter->user_data);
    if (py_ret) {
	gint ret = PyInt_AsLong(py_ret);

	Py_DECREF(py_ret);
	return ret;
    } else {
	PyErr_Print();
	PyErr_Clear();
	return 0;
    }
}

static gboolean
tree_model_iter_nth_child(GtkTreeModel *tree_model, GtkTreeIter  *iter,
				GtkTreeIter  *parent, gint n)
{
    PyObject *self, *py_ret, *py_parent = Py_None;

    g_return_val_if_fail(tree_model != NULL, FALSE);
    g_return_val_if_fail(IS_TREE_MODEL(tree_model), FALSE);
    g_return_val_if_fail(iter != NULL, FALSE);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("iter_nth_child(%p, %p (%p), %d)", iter, parent, parent ? parent->user_data : NULL, n);
#endif
    if (parent && parent->user_data)
	py_parent = (PyObject *)parent->user_data;
    py_ret = PyObject_CallMethod(self, METHOD_PREFIX "iter_nth_child",
				 "(Oi)", py_parent, n);
    if (py_ret) {
	if (py_ret != Py_None) {
	    /* XXXX handle reference counting here */
	    iter->user_data = py_ret;
	    Py_DECREF(py_ret);
	    return TRUE;
	} else {
	    iter->user_data = NULL;
	    Py_DECREF(py_ret);
	    return FALSE;
	}
    } else {
	iter->user_data = NULL;
	PyErr_Print();
	PyErr_Clear();
	return FALSE;
    }
}

static gboolean
tree_model_iter_parent(GtkTreeModel *tree_model, GtkTreeIter *iter,
			     GtkTreeIter *child)
{
    PyObject *self, *py_ret, *py_child = Py_None;

    g_return_val_if_fail(tree_model != NULL, FALSE);
    g_return_val_if_fail(IS_TREE_MODEL(tree_model), FALSE);
    g_return_val_if_fail(iter != NULL, FALSE);
    /* this call finds the wrapper for this GObject */
    self = pygobject_new((GObject *)tree_model);

#ifdef DEBUG_TREE_MODEL
    g_message("iter_parent(%p, %p)", iter, child);
#endif
    if (child && child->user_data)
	py_child = (PyObject *)child->user_data;
    py_ret = PyObject_CallMethod(self, METHOD_PREFIX "iter_parent",
				 "(O)", py_child);
    if (py_ret) {
	if (py_ret != Py_None) {
	    /* XXXX handle reference counting here */
	    if (iter->user_data) {
		Py_DECREF ((PyObject*) iter->user_data);
	    }
	    iter->user_data = py_ret;
	    Py_DECREF(py_ret);
	    return TRUE;
	} else {
	    iter->user_data = NULL;
	    Py_DECREF(py_ret);
	    return FALSE;
	}
    } else {
	iter->user_data = NULL;
	PyErr_Print();
	PyErr_Clear();
	return FALSE;
    }
}

