/* realization.h
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
 * Realization
 * -----------
 */

#ifndef __REALIZATION_H__
#define __REALIZATION_H__

#include "relationship.h"

G_BEGIN_DECLS

#define TYPE_REALIZATION		(realization_get_type ())
#define REALIZATION(obj)		(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_REALIZATION, Realization))
#define REALIZATION_CLASS(klass)	(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_REALIZATION, RealizationClass))
#define IS_REALIZATION(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_REALIZATION))
#define IS_REALIZATION_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_REALIZATION))
#define REALIZATION_GET_CLASS(obj)	(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_REALIZATION, RealizationClass))

#define _TYPE_REALIZATION		TYPE_REALIZATION
#define _REALIZATION			REALIZATION

typedef struct _Realization Realization;
typedef struct _RealizationClass RealizationClass;

struct _Realization
{
	Relationship item;
};


struct _RealizationClass
{
	RelationshipClass parent_class;
};

GType realization_get_type (void);

G_END_DECLS


#endif /* __REALIZATION_H__ */
