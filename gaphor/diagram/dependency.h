/* dependency.h
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
 * Dependency
 * -----------
 */

#ifndef __DEPENDENCY_H__
#define __DEPENDENCY_H__

#include "relationship.h"

G_BEGIN_DECLS

#define TYPE_DEPENDENCY		(dependency_get_type ())
#define DEPENDENCY(obj)		(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_DEPENDENCY, Dependency))
#define DEPENDENCY_CLASS(klass)	(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_DEPENDENCY, DependencyClass))
#define IS_DEPENDENCY(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_DEPENDENCY))
#define IS_DEPENDENCY_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_DEPENDENCY))
#define DEPENDENCY_GET_CLASS(obj)	(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_DEPENDENCY, DependencyClass))

#define _TYPE_DEPENDENCY		TYPE_DEPENDENCY
#define _DEPENDENCY			DEPENDENCY

typedef struct _Dependency Dependency;
typedef struct _DependencyClass DependencyClass;

struct _Dependency
{
	Relationship item;
};


struct _DependencyClass
{
	RelationshipClass parent_class;
};

GType dependency_get_type (void);

G_END_DECLS


#endif /* __DEPENDENCY_H__ */
