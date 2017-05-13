#!/usr/bin/env python

# Copyright (C) 2008-2017 Arjan Molenaar <gaphor@gmail.com>
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
Test pseudostates.
"""

from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram.states.pseudostates import InitialPseudostateItem, HistoryPseudostateItem
from gaphor.tests.testcase import TestCase


class InitialPseudostate(TestCase):
    """
    Initial pseudostate item test cases.
    """

    def test_initial_pseudostate(self):
        """Test creation of initial pseudostate
        """
        item = self.create(InitialPseudostateItem, uml2.Pseudostate)
        self.assertEquals('initial', item.subject.kind)


    def test_history_pseudostate(self):
        """Test creation of initial pseudostate
        """
        item = self.create(HistoryPseudostateItem, uml2.Pseudostate)
        # history setting is done in the DiagramToolbox factory:
        item.subject.kind = 'shallowHistory'
        self.assertEquals('shallowHistory', item.subject.kind)


# vim:sw=4:et:ai
