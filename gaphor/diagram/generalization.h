/* generalization.h
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
 * Generalization
 * ----------
 */

#ifndef __GENERALIZATION_H__
#define __GENERALIZATION_H__

#include "relationship.h"

G_BEGIN_DECLS

#define TYPE_GENERALIZATION			(generalization_get_type ())
#define GENERALIZATION(obj)			(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_GENERALIZATION, Generalization))
#define GENERALIZATION_CLASS(klass)		(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_GENERALIZATION, GeneralizationClass))
#define IS_GENERALIZATION(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_GENERALIZATION))
#define IS_GENERALIZATION_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_GENERALIZATION))
#define GENERALIZATION_GET_CLASS(obj)		(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_GENERALIZATION, GeneralizationClass))

#define _TYPE_GENERALIZATION			TYPE_GENERALIZATION
#define _GENERALIZATION			GENERALIZATION

typedef struct _Generalization Generalization;
typedef struct _GeneralizationClass GeneralizationClass;

struct _Generalization
{
	Relationship item;
	
};


struct _GeneralizationClass
{
	RelationshipClass parent_class;
};

GType generalization_get_type (void);

	
G_END_DECLS


#endif /* __GENERALIZATION_H__ */
