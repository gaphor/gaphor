/* classifier.h
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
 * Classifier
 * ----------
 * Classifiers are the items that represent static elements, such as classes,
 * packages, use cases and actors. Classifiers can connect generalizations,
 * realizations and dependencies.
 */

#ifndef __CLASSIFIER_H__
#define __CLASSIFIER_H__

#include "model-element.h"

G_BEGIN_DECLS

#define TYPE_CLASSIFIER			(classifier_get_type ())
#define CLASSIFIER(obj)			(G_TYPE_CHECK_INSTANCE_CAST ((obj), TYPE_CLASSIFIER, Classifier))
#define CLASSIFIER_CLASS(klass)		(G_TYPE_CHECK_CLASS_CAST ((klass), TYPE_CLASSIFIER, ClassifierClass))
#define IS_CLASSIFIER(obj)		(G_TYPE_CHECK_INSTANCE_TYPE ((obj), TYPE_CLASSIFIER))
#define IS_CLASSIFIER_CLASS(klass)	(G_TYPE_CHECK_CLASS_TYPE ((klass), TYPE_CLASSIFIER))
#define CLASSIFIER_GET_CLASS(obj)		(G_TYPE_INSTANCE_GET_CLASS ((obj), TYPE_CLASSIFIER, ClassifierClass))

#define _TYPE_CLASSIFIER			TYPE_CLASSIFIER
#define _CLASSIFIER			CLASSIFIER

typedef struct _Classifier Classifier;
typedef struct _ClassifierClass ClassifierClass;

struct _Classifier
{
	ModelElement item;
	
	/* PyObject *old_namespace; */
};


struct _ClassifierClass
{
	ModelElementClass parent_class;
};

GType classifier_get_type (void);

	
G_END_DECLS


#endif /* __CLASSIFIER_H__ */
