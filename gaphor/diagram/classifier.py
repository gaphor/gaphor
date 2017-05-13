#!/usr/bin/env python

# Copyright (C) 2002-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#                         syt <noreply@example.com>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Classifier diagram item.
"""

from __future__ import absolute_import
from gaphor.diagram.compartment import CompartmentItem


class ClassifierItem(CompartmentItem):
    """
    Base class for UML classifiers.

    Classifiers can be abstract and this feature is supported by this
    class.
    """

    __style__ = {
        'name-font': 'sans bold 10',
        'abstract-name-font': 'sans bold italic 10',
    }
 
    def __init__(self, id=None):
        super(ClassifierItem, self).__init__(id)
        self.watch('subject<Classifier>.isAbstract', self.on_classifier_is_abstract)


    def on_classifier_is_abstract(self, event):
        self._name.font = self.style.abstract_name_font \
                if self.subject and self.subject.isAbstract \
                else self.style.name_font
        self.request_update()


    def postload(self):
        super(ClassifierItem, self).postload()
        self.on_classifier_is_abstract(None)


# vim:sw=4:et
