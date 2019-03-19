# Copyright 2016 Christoph Reiter, 2019 Dan Yeaw
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""This file gets edited at build time to add build specific data"""

BUILD_TYPE = u"default"
"""Either 'windows', 'windows-portable', 'osx-gaphor', or 'default'"""

BUILD_INFO = u""
"""Additional build info like git revision etc"""

BUILD_VERSION = 0
"""1.2.3 with a BUILD_VERSION of 1 results in 1.2.3.1"""
