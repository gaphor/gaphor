/* include.h
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
 * Include
 * -------
 */

#ifndef __INCLUDE_H__
#define __INCLUDE_H__

#include "relationship.h"

G_BEGIN_DECLS

#define TYPE_INCLUDE		(include_get_type ())
#define INCLUDE(obj)		(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_INCLUDE, Include))
#define INCLUDE_CLASS(klass)	(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_INCLUDE, IncludeClass))
#define IS_INCLUDE(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_INCLUDE))
#define IS_INCLUDE_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_INCLUDE))
#define INCLUDE_GET_CLASS(obj)	(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_INCLUDE, IncludeClass))

#define _TYPE_INCLUDE		TYPE_INCLUDE
#define _INCLUDE		INCLUDE

typedef struct _Include Include;
typedef struct _IncludeClass IncludeClass;

struct _Include
{
	Relationship item;
};


struct _IncludeClass
{
	RelationshipClass parent_class;
};

GType include_get_type (void);

G_END_DECLS


#endif /* __INCLUDE_H__ */
