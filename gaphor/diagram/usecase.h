/* use_case.h
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
 * UseCase
 * ----------
 * Base class for text like objects, which includes basically everything
 * that's not a line.
 * Texts have eight handles around them and can move, but handles can not
 * connect to other texts. Moving an individual handle will cause the
 * text to call UseCaseClass::resize().
 */

#ifndef __USE_CASE_H__
#define __USE_CASE_H__

#include "classifier.h"

G_BEGIN_DECLS

#define TYPE_USE_CASE			(use_case_get_type ())
#define USE_CASE(obj)			(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_USE_CASE, UseCase))
#define USE_CASE_CLASS(klass)		(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_USE_CASE, UseCaseClass))
#define IS_USE_CASE(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_USE_CASE))
#define IS_USE_CASE_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_USE_CASE))
#define USE_CASE_GET_CLASS(obj)		(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_USE_CASE, UseCaseClass))

#define _TYPE_USE_CASE			TYPE_USE_CASE
#define _USE_CASE			USE_CASE

typedef struct _UseCase UseCase;
typedef struct _UseCaseClass UseCaseClass;

struct _UseCase
{
	Classifier item;
	
	gint cursor_index;
	gdouble text_height;
};


struct _UseCaseClass
{
	ClassifierClass parent_class;
};

GType use_case_get_type (void);

	
G_END_DECLS


#endif /* __USE_CASE_H__ */
