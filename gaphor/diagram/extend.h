/* extend.h
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
 * Extend
 * ------
 */

#ifndef __EXTEND_H__
#define __EXTEND_H__

#include "relationship.h"

G_BEGIN_DECLS

#define TYPE_EXTEND		(extend_get_type ())
#define EXTEND(obj)		(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_EXTEND, Extend))
#define EXTEND_CLASS(klass)	(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_EXTEND, ExtendClass))
#define IS_EXTEND(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_EXTEND))
#define IS_EXTEND_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_EXTEND))
#define EXTEND_GET_CLASS(obj)	(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_EXTEND, ExtendClass))

#define _TYPE_EXTEND		TYPE_EXTEND
#define _EXTEND			EXTEND

typedef struct _Extend Extend;
typedef struct _ExtendClass ExtendClass;

struct _Extend
{
	Relationship item;
};


struct _ExtendClass
{
	RelationshipClass parent_class;
};

GType extend_get_type (void);

G_END_DECLS


#endif /* __EXTEND_H__ */
