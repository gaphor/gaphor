/* -*- Mode: C; c-basic-offset: 4 -*- */
#include <gtk/gtk.h>

#define TYPE_TREE_MODEL (tree_model_get_type())
#define TREE_MODEL(object) (G_TYPE_CHECK_INSTANCE_CAST((object), TYPE_TREE_MODEL, TreeModel))
#define TREE_MODEL_CLASS(klass) (G_TYPE_CHECK_CLASS_CAST((klass), TYPE_TREE_MODEL, TreeModelClass))
#define IS_TREE_MODEL(object) (G_TYPE_CHECK_INSTANCE_TYPE((object), TYPE_TREE_MODEL))
#define IS_TREE_MODEL_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), TYPE_TREE_MODEL))
#define TREE_MODEL_GET_CLASS(obj) (G_TYPE_INSTANCE_GET_CLASS((obj), TYPE_TREE_MODEL, TreeModelClass))

#define _TYPE_TREE_MODEL	TYPE_TREE_MODEL
#define _TREE_MODEL		TREE_MODEL

typedef struct _TreeModel TreeModel;
typedef struct _TreeModelClass TreeModelClass;

struct _TreeModel {
    GObject parent_instance;
};

struct _TreeModelClass {
    GObjectClass parent_class;

};

GType tree_model_get_type(void);

TreeModel *tree_model_new(void);
