/* actor.h
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
 * Actor
 * ----------
 * Base class for text like objects, which includes basically everything
 * that's not a line.
 * Texts have eight handles around them and can move, but handles can not
 * connect to other texts. Moving an individual handle will cause the
 * text to call ActorClass::resize().
 */

#ifndef __ACTOR_H__
#define __ACTOR_H__

#include "classifier.h"

G_BEGIN_DECLS

#define TYPE_ACTOR		(actor_get_type ())
#define ACTOR(obj)		(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_ACTOR, Actor))
#define ACTOR_CLASS(klass)	(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_ACTOR, ActorClass))
#define IS_ACTOR(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_ACTOR))
#define IS_ACTOR_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_ACTOR))
#define ACTOR_GET_CLASS(obj)	(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_ACTOR, ActorClass))

#define _TYPE_ACTOR		TYPE_ACTOR
#define _ACTOR			ACTOR

typedef struct _Actor Actor;
typedef struct _ActorClass ActorClass;

struct _Actor
{
	Classifier item;
	
	gint cursor_index;
};


struct _ActorClass
{
	ClassifierClass parent_class;
};

GType actor_get_type (void);

	
G_END_DECLS


#endif /* __ACTOR_H__ */
