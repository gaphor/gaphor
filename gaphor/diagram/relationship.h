/* relationship.h
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
 * Relationship
 * ----------
 * Relationship is the base class for line-like objects in diagrams.
 */

#ifndef __RELATIONSHIP_H__
#define __RELATIONSHIP_H__

#include <diacanvas/dia-canvas-line.h>
#include <Python.h>

G_BEGIN_DECLS

#define TYPE_RELATIONSHIP		(relationship_get_type ())
#define RELATIONSHIP(obj)		(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_RELATIONSHIP, Relationship))
#define RELATIONSHIP_CLASS(klass)	(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_RELATIONSHIP, RelationshipClass))
#define IS_RELATIONSHIP(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_RELATIONSHIP))
#define IS_RELATIONSHIP_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_RELATIONSHIP))
#define RELATIONSHIP_GET_CLASS(obj)	(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_RELATIONSHIP, RelationshipClass))

#define _TYPE_RELATIONSHIP		TYPE_RELATIONSHIP
#define _RELATIONSHIP			RELATIONSHIP

typedef struct _Relationship Relationship;
typedef struct _RelationshipClass RelationshipClass;

struct _Relationship
{
	DiaCanvasLine item;
	
	PyObject *subject;
};


struct _RelationshipClass
{
	DiaCanvasLineClass parent_class;

	void (* element_update) (Relationship *relationship, const gchar *key);
};

GType relationship_get_type (void);

void relationship_element_update (Relationship *relationship, const gchar *key);

G_END_DECLS


#endif /* __RELATIONSHIP_H__ */
