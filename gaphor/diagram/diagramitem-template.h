/* @filename@.h
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
 * @Name@
 * ----------
 */

#ifndef __@NAME@_H__
#define __@NAME@_H__

#include "@parentfilename@.h"

G_BEGIN_DECLS

#define TYPE_@NAME@			(@name@_get_type ())
#define @NAME@(obj)			(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_@NAME@, @Name@))
#define @NAME@_CLASS(klass)		(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_@NAME@, @Name@Class))
#define IS_@NAME@(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_@NAME@))
#define IS_@NAME@_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_@NAME@))
#define @NAME@_GET_CLASS(obj)		(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_@NAME@, @Name@Class))

#define _TYPE_@NAME@			TYPE_@NAME@
#define _@NAME@			@NAME@

typedef struct _@Name@ @Name@;
typedef struct _@Name@Class @Name@Class;

struct _@Name@
{
	@ParentName@ item;
	
};


struct _@Name@Class
{
	@ParentName@Class parent_class;
};

GType @name@_get_type (void);

	
G_END_DECLS


#endif /* __@NAME@_H__ */
