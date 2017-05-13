#!/usr/bin/env python

# Copyright (C) 2008-2017 Arjan Molenaar <gaphor@gmail.com>
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
Modified pickler. This version uses forward declarations in the
state machine, so recursion depth can be limited.
"""

from __future__ import absolute_import
import pickle, types, struct


BUILD = pickle.BUILD
INST = pickle.INST
OBJ = pickle.OBJ
MARK = pickle.MARK
POP = pickle.POP
STOP = pickle.STOP


class LatePickler(pickle.Pickler):
    """
    Pickler use breadth-first traversal. This approach limits the
    recursion depth of the pickler.

    For List types, a trick is to memorize all items at first,
    
    NOTE: this pickler does not work in binary mode!
    """

    dispatch = dict(pickle.Pickler.dispatch)

    def __init__(self, file, protocol=0):
        pickle.Pickler.__init__(self, file, protocol)
        self.later = []

    def dump(self, obj):
        if self.proto >= 2:
            self.write(PROTO + chr(self.proto))
        self.save(obj)

        later = self.later
        memo = self.memo
        get = self.get
        save = self.save
        write = self.write

        index = 0
        # Use while loop as objects may be added as we save more items:
        while later:
            obj, stuff = later[0]
            
            # First retrieve the object from the memo
            assert id(obj) in memo
            x = memo[id(obj)]
            write(get(x[0]))

            # Now populate it
            save(stuff)
            write(BUILD)
            
            write(POP)
            del later[0]

        self.write(STOP)


    def save_later(self, obj, stuff):
        self.later.append((obj, stuff))


    def delay(self, obj):
        """
        Use this to check if items can be saved later on,
        or need imediate saving.
        """
        return True

    def save_inst(self, obj):
        """
        For old-style classes!
        """
        cls = obj.__class__

        memo  = self.memo
        write = self.write
        save  = self.save

        if hasattr(obj, '__getinitargs__'):
            args = obj.__getinitargs__()
            len(args) # XXX Assert it's a sequence
            _keep_alive(args, memo)
        else:
            args = ()

        write(MARK)

        if self.bin:
            save(cls)
            for arg in args:
                save(arg)
            write(OBJ)
        else:
            for arg in args:
                save(arg)
            write(INST + cls.__module__ + '\n' + cls.__name__ + '\n')

        self.memoize(obj)

        try:
            getstate = obj.__getstate__
        except AttributeError:
            stuff = obj.__dict__
        else:
            stuff = getstate()
            _keep_alive(stuff, memo)

        if self.delay(obj):
            # TODO: delay this until all is saved:
            self.save_later(obj, stuff)
        else:
            save(stuff)
            write(BUILD)

    dispatch[types.InstanceType] = save_inst

    def save_reduce(self, func, args, state=None,
                    listitems=None, dictitems=None, obj=None):
        #print 'saving reduce', func, args, obj

        # We want to reduce nesting, hence the state should be saved later:
        if obj and state and self.delay(obj):
            self.save_later(obj, state)
            state = None

        pickle.Pickler.save_reduce(self, func, args, state, listitems, dictitems, obj)


# vim:sw=4:et:ai
