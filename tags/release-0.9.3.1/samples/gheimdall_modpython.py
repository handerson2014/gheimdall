#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   GHeimdall - A small web application for Google Apps SSO service.
#   Copyright (C) 2007 SIOS Technology, Inc.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
#   USA.
#
#   $Id$

__author__ = 'tmatsuo@sios.com (Takashi MATSUO)'

import pkg_resources
pkg_resources.require("TurboGears")

#Set this to absolute app home path
#virtual_current_uri = '/etc/gheimdall'

import cherrypy
import turbogears

#Override TurboGear's configuration function
#original_config_defaults = turbogears.config.config_defaults
#def overrided_config_default():
#    config_default = original_config_defaults()
#    config_default.update({'current_dir_uri' : virtual_current_uri})
#    return config_default
#turbogears.config.config_defaults = overrided_config_default

turbogears.update_config(
    configfile="/etc/gheimdall/prod.cfg",
    modulename="gheimdall.config"
)

from gheimdall.controllers import Root
cherrypy.root = Root()
cherrypy.server.start(initOnly=True, serverClass=None)

def fixuphandler(req):
    return 0
