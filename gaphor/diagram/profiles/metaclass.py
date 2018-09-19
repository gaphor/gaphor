#!/usr/bin/env python

# Copyright (C) 2009-2017 Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Metaclass item for Metaclass UML metaclass :) from profiles.
"""

from __future__ import absolute_import
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram import uml
from gaphor.UML import uml2

@uml(uml2.Component, stereotype='metaclass')
class MetaclassItem(ClassItem):
    pass

