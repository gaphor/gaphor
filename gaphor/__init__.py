# Copyright 2001-2021 Arjan Molenaar & Dan Yeaw
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing
# permissions and limitations under the License.
#
# This license is applicable for all gaphor resources, unless specified
# otherwise.

"""Gaphor is the simple modeling tool written in Python."""

import os

import gi

gtk_version = "4.0" if os.getenv("GAPHOR_USE_GTK") == "4" else "3.0"
gtk_source_version = "5" if os.getenv("GAPHOR_USE_GTK") == "4" else "4"

gi.require_version("PangoCairo", "1.0")
gi.require_version("Gtk", gtk_version)
gi.require_version("Gdk", gtk_version)
gi.require_version("GtkSource", gtk_source_version)
