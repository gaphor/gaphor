/* model-element.h
 * Copyright (C) 2001  Arjan Molenaar
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */
/*
 * ModelElement
 * ----------
 * This is the base class for elements on the canvas. Note that line-like
 * stuff is inherited from Relationship instead of ModelElement.
 */

#ifndef __MODEL_ELEMENT_H__
#define __MODEL_ELEMENT_H__

#include <diacanvas/dia-canvas-element.h>
#include <pango/pango.h>
#include <Python.h>

G_BEGIN_DECLS

#define TYPE_MODEL_ELEMENT		(model_element_get_type ())
#define MODEL_ELEMENT(obj)		(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_MODEL_ELEMENT, ModelElement))
#define MODEL_ELEMENT_CLASS(klass)	(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_MODEL_ELEMENT, ModelElementClass))
#define IS_MODEL_ELEMENT(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_MODEL_ELEMENT))
#define IS_MODEL_ELEMENT_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_MODEL_ELEMENT))
#define MODEL_ELEMENT_GET_CLASS(obj)	(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_MODEL_ELEMENT, ModelElementClass))

#define _TYPE_MODEL_ELEMENT		TYPE_MODEL_ELEMENT
#define _MODEL_ELEMENT			MODEL_ELEMENT

typedef struct _ModelElement ModelElement;
typedef struct _ModelElementClass ModelElementClass;

struct _ModelElement
{
	DiaCanvasElement item;
	
	PyObject *subject;

	gboolean auto_resize;
	/* should be: */
	gboolean auto_grow;
	gboolean auto_shrink;

	gboolean need_resize;
};


struct _ModelElementClass
{
	DiaCanvasElementClass parent_class;

	void (* element_update) (ModelElement *element, const gchar *key);
};

GType model_element_get_type (void);

void model_element_element_update (ModelElement *element, const gchar *key);

G_END_DECLS


#endif /* __MODEL_ELEMENT_H__ */
