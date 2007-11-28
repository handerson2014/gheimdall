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

import os
from string import Template
import random
import cherrypy
import zlib
import base64
import sha
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
from turbogears import config, flash
from gheimdall import errors, responsecreator
import saml2
import xmldsig as ds
from saml2 import saml, samlp
import logging

log = logging.getLogger("gheimdall.controllers")

righthand = '6789yuiophjknmYUIPHJKLNM'
lefthand = '2345qwertasdfgzxcvbQWERTASDFGZXCVB'
allchars = righthand + lefthand

def hashPassword(password, hash_style):

  if hash_style == '{SHA}':
    return hash_style + base64.b64encode(sha.new(password).digest())

  raise NotImplementedError('hash style is not implemented: %s.' % hash_style)

def generateRandomPassword(length=8, alternate_hands=True):
  rng = random.Random()
  ret = ''
  for i in range(length):
    if not alternate_hands:
      ret += rng.choice(allchars)
    else:
      if i%2:
        ret += rng.choice(lefthand)
      else:
        ret += rng.choice(righthand)
  return ret      

def ldapEscape(source):
  ret = source
  ret = ret.replace('*', '\\2a')
  ret = ret.replace('(', '\\28')
  ret = ret.replace(')', '\\29')
  ret = ret.replace('\\', '\\5c')
  return ret

def createLoginDict(SAMLRequest, RelayState, user_name):
  try:
    xml = zlib.decompress(base64.b64decode(SAMLRequest), -8)
    authn_request = samlp.AuthnRequestFromString(xml)
  except Exception, e:
    log.error(e)
    flash(_('The value of SAMLRequest is wrong'))
    raise errors.GheimdallException()
  # print authn_request.ToString()
  acsURL = authn_request.assertion_consumer_service_url
  issuer = authn_request.issuer.text.strip()
  
  # create response
  sp_setting = config.get('apps.service_providers')
  module_name = sp_setting.get(
    issuer, config.get("apps.default_response_creator","default"))
  response_creator = responsecreator.create(module_name, config)

  # create saml response
  saml_response = response_creator.createSamlResponse(user_name)

  signed_response = saml2.utils.sign(saml_response.ToString(),
                                     config.get('apps.privkey_filename'))
  encoded_response = base64.encodestring(signed_response)

  # set session data
  # Preserve user_name in the session for changing password.
  cherrypy.session['user_name'] = user_name
  cherrypy.session['authenticated'] = True
  if RelayState.find('continue=https') >= 0:
    cherrypy.session['useSSL'] = True

  return dict(acsURL=acsURL, SAMLResponse=encoded_response,
              RelayState=RelayState)

