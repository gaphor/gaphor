/* comment.h
 * Copyright (C) 2002  Arjan Molenaar
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
 * Comment
 * ----------
 * Base class for text like objects, which includes basically everything
 * that's not a line.
 * Texts have eight handles around them and can move, but handles can not
 * connect to other texts. Moving an individual handle will cause the
 * text to call CommentClass::resize().
 */

#ifndef __COMMENT_H__
#define __COMMENT_H__

#include "model-element.h"
#include <pango/pangoft2.h>

G_BEGIN_DECLS

#define TYPE_COMMENT		(comment_get_type ())
#define COMMENT(obj)		(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_COMMENT, Comment))
#define COMMENT_CLASS(klass)	(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_COMMENT, CommentClass))
#define IS_COMMENT(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_COMMENT))
#define IS_COMMENT_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_COMMENT))
#define COMMENT_GET_CLASS(obj)	(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_COMMENT, CommentClass))

#define _TYPE_COMMENT		TYPE_COMMENT
#define _COMMENT		COMMENT

typedef struct _Comment Comment;
typedef struct _CommentClass CommentClass;

struct _Comment
{
	ModelElement item;
	
	gint cursor_index;
};


struct _CommentClass
{
	ModelElementClass parent_class;
};

GType comment_get_type (void);

	
G_END_DECLS


#endif /* __COMMENT_H__ */
