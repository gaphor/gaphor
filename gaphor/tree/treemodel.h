/* -*- Mode: C; c-basic-offset: 4 -*- */
#include <gtk/gtk.h>

#define PYGTK_TYPE_GENERIC_TREE_MODEL (pygtk_generic_tree_model_get_type())
#define PYGTK_GENERIC_TREE_MODEL(object) (G_TYPE_CHECK_INSTANCE_CAST((object), PYGTK_TYPE_GENERIC_TREE_MODEL, PyGtkGenericTreeModel))
#define PYGTK_GENERIC_TREE_MODEL_CLASS(klass) (G_TYPE_CHECK_CLASS_CAST((klass), PYGTK_TYPE_GENERIC_TREE_MODEL, PyGtkGenericTreeModelClass))
#define PYGTK_IS_GENERIC_TREE_MODEL(object) (G_TYPE_CHECK_INSTANCE_TYPE((object), PYGTK_TYPE_GENERIC_TREE_MODEL))
#define PYGTK_IS_GENERIC_TREE_MODEL_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), PYGTK_TYPE_GENERIC_TREE_MODEL))
#define PYGTK_GENERIC_TREE_MODEL_GET_CLASS(obj) (G_TYPE_INSTANCE_GET_CLASS((obj), PYGTK_TYPE_GENERIC_TREE_MODEL, PyGtkGenericTreeModelClass))

typedef struct _PyGtkGenericTreeModel PyGtkGenericTreeModel;
typedef struct _PyGtkGenericTreeModelClass PyGtkGenericTreeModelClass;

struct _PyGtkGenericTreeModel {
    GObject parent_instance;

    gboolean leak_references;
};

struct _PyGtkGenericTreeModelClass {
    GObjectClass parent_class;

};

GType pygtk_generic_tree_model_get_type(void);

PyGtkGenericTreeModel *pygtk_generic_tree_model_new(void);
