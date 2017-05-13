#!/usr/bin/env python

# Copyright (C) 2010-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
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
Module dealing with options (typing) of icons.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from simplegeneric import generic


@generic
def get_icon_option(element):
    """
    Default behaviour: no options.
    """
    return


@get_icon_option.when_type(uml2.Class)
def get_option_class(element):
    if element.extension:
        return 'metaclass'


@get_icon_option.when_type(uml2.Component)
def get_option_component(element):
    for p in element.presentation:
        try:
            if p.__stereotype__ == 'subsystem':
                return 'subsystem'
        except AttributeError:
            pass


@get_icon_option.when_type(uml2.Property)
def get_option_property(element):
    if element.association:
        return 'association-end'

# vim:sw=4:et:ai
