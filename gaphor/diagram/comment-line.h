/* comment_line.h
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
 * CommentLine
 * ----------
 * A comment line is the line that connects the comment with a model element.
 * It checks if one end is a comment and the other end is a model element.
 * This item changes Comment.annotatedElement and ModelElement.comment.
 */

#ifndef __COMMENT_LINE_H__
#define __COMMENT_LINE_H__

#include <diacanvas/dia-canvas-line.h>

G_BEGIN_DECLS

#define TYPE_COMMENT_LINE		(comment_line_get_type ())
#define COMMENT_LINE(obj)		(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_COMMENT_LINE, CommentLine))
#define COMMENT_LINE_CLASS(klass)	(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_COMMENT_LINE, CommentLineClass))
#define IS_COMMENT_LINE(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_COMMENT_LINE))
#define IS_COMMENT_LINE_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_COMMENT_LINE))
#define COMMENT_LINE_GET_CLASS(obj)	(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_COMMENT_LINE, CommentLineClass))

#define _TYPE_COMMENT_LINE		TYPE_COMMENT_LINE
#define _COMMENT_LINE		COMMENT_LINE

typedef struct _CommentLine CommentLine;
typedef struct _CommentLineClass CommentLineClass;

struct _CommentLine
{
	DiaCanvasLine line;

	guint head_disconnect_id;
	guint tail_disconnect_id;
};


struct _CommentLineClass
{
	DiaCanvasLineClass parent_class;
};

GType comment_line_get_type (void);

gboolean comment_line_handle_glue (CommentLine *line, DiaHandle *handle,
				   DiaCanvasItem *gluing_to);
gboolean comment_line_handle_connect (CommentLine *line, DiaHandle *handle,
				      DiaCanvasItem *connecting_to);
//gboolean comment_line_handle_disconnect (CommentLine *line, DiaHandle *handle);

G_END_DECLS


#endif /* __COMMENT_LINE_H__ */
