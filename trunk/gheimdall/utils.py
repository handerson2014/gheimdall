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
import time
import libxml2
import xmlsec
import StringIO
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
  module_name = sp_setting.get(issuer,
                               config.get("apps.default_response_creator", "default"))
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

  return dict(acsURL=acsURL,
              SAMLResponse=encoded_response,
              RelayState=RelayState)

def createID():
  ret = ""
  for i in range(40):
    ret = ret + chr(random.randint(0, 15) + ord('a'));
  return ret

def getDateAndTime(slice=0):
  return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + slice))

def signResponse(saml_response, key_file, cert_file=None):
  # Init libxml library
  libxml2.initParser()
  libxml2.substituteEntitiesDefault(1)

  # Init xmlsec library
  if xmlsec.init() < 0:
    raise(errors.GheimdallException("Error: xmlsec initialization failed."))

  # Check loaded library version
  if xmlsec.checkVersion() != 1:
    raise(errors.GheimdallException(
      "Error: loaded xmlsec library version is not compatible.\n"))

  # Init crypto library
  if xmlsec.cryptoAppInit(None) < 0:
    raise(errors.GheimdallException("Error: crypto initialization failed."))

  # Init xmlsec-crypto library
  if xmlsec.cryptoInit() < 0:
    raise(errors.GheimdallException("Error: xmlsec-crypto initialization failed."))

  ret = sign_file(saml_response, key_file, cert_file)

  # Shutdown xmlsec-crypto library
  xmlsec.cryptoShutdown()

  # Shutdown crypto library
  xmlsec.cryptoAppShutdown()

  # Shutdown xmlsec library
  xmlsec.shutdown()

  return ret

# Signs the xml_file using private key from key_file and dynamicaly
# created enveloped signature template.
# Returns 0 on success or a negative value if an error occurs.
def sign_file(xml, key_file, cert_file=None):

  # Load template
  doc = libxml2.parseDoc(xml)
  if doc is None or doc.getRootElement() is None:
    cleanup(doc)
    raise errors.GheimdallException("Error: unable to parse string \"%s\"" % xml)

  node = xmlsec.findNode(doc.getRootElement(), xmlsec.NodeSignature,
                         xmlsec.DSigNs)

  if node is None:
    cleanup(doc)
    raise errors.GheimdallException("Error: start node not found.")

  # Create signature context, we don't need keys manager in this example
  dsig_ctx = xmlsec.DSigCtx()
  if dsig_ctx is None:
    cleanup(doc)
    raise errors.GheimdallException("Error: failed to create signature context")

  # Load private key, assuming that there is not password
  key = xmlsec.cryptoAppKeyLoad(key_file, xmlsec.KeyDataFormatPem,
                                None, None, None)
  if key is None:
    cleanup(doc, dsig_ctx)
    raise errors.GheimdallException(
      "Error: failed to load private pem key from \"%s\"" % key_file)
  dsig_ctx.signKey = key

  if cert_file is not None:
    if xmlsec.cryptoAppKeyCertLoad(
      dsig_ctx.signKey, cert_file, xmlsec.KeyDataFormatPem) < 0:
      cleanup(doc, dsig_ctx)
      raise errors.GheimdallException(
        "Error: failed to load cert pem from \"%s\"" % cert_file)
  else:
    pass
    
  # Set key name to the file name, this is just an example!
  if key.setName(key_file) < 0:
    cleanup(doc, dsig_ctx)
    raise errors.GheimdallException(
      "Error: failed to set key name for key from \"%s\"" % key_file)
    return cleanup(doc, dsig_ctx)

  # Sign the template
  if dsig_ctx.sign(node) < 0:
    cleanup(doc, dsig_ctx)
    raise errors.GheimdallException("Error: signature failed")
  
  # Print signed document to stdout
  ret = doc.__str__()

  # Success
  cleanup(doc, dsig_ctx, 1)

  return ret

def cleanup(doc=None, dsig_ctx=None, res=-1):
  if dsig_ctx is not None:
    dsig_ctx.destroy()
  if doc is not None:
    doc.freeDoc()
  return res
