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
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
from turbogears import config, flash
from gheimdall import errors, unamemapper
import logging

log = logging.getLogger("gheimdall.controllers")

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
    saml_tree = ElementTree.fromstring(xml)
  except Exception, e:
    log.error(e)
    flash(_('The value of SAMLRequest is wrong'))
    raise errors.GheimdallException()
  acsURL = saml_tree.attrib['AssertionConsumerServiceURL']

  # uname mapping
  mapper = unamemapper.createUnameMapper(
    mapper=config.get('apps.uname_mapper'),
    config=config)
  google_user_name = mapper.getGoogleUsername(user_name)

  # create saml response
  saml_response = createSamlResponse(google_user_name)

  signed_response = signResponse(saml_response,
                                 config.get('apps.privkey_filename'))

  # set session data
  # Preserve user_name in the session for changing password.
  cherrypy.session['user_name'] = user_name
  cherrypy.session['google_user_name'] = google_user_name
  cherrypy.session['authenticated'] = True
  if RelayState.find('continue=https') >= 0:
    cherrypy.session['useSSL'] = True

  return dict(acsURL=acsURL,
              SAMLResponse=signed_response,
              RelayState=RelayState)

def createSamlResponse(username):
  xml_template_path = os.path.join(
    os.path.dirname(__file__),
    os.path.join('templates', 'samlResponseTemplate.xml'))
    
  xml_template_file = file(xml_template_path)
  xml_template = Template(xml_template_file.read())
  xml_template_file.close()

  return xml_template.substitute(dict(USERNAME_STRING=username,
                                      RESPONSE_ID=createID(),
                                      ISSUE_INSTANT=getDateAndTime(),
                                      AUTHN_INSTANT=getDateAndTime(),
                                      NOT_BEFORE=getDateAndTime(-31536000),
                                      NOT_ON_OR_AFTER=getDateAndTime(31536000),
                                      ASSERTION_ID=createID()))

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
