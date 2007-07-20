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

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import atom
import gdata.apps
import gdata.apps.service

ERR_UNKNOWN = 99
ERR_FATAL = 98

class PasswdException(Exception):
  def __init__(self, reason, code=ERR_UNKNOWN):
    self.reason = reason
    self.code = code

  def __str__(self):
    return "%d: %s" % (self.code, self.reason)

class BasePasswdEngine(object):

  def __init__(self, config):
    self._prepare(config)
    
  def changePassword(self, user_name, old_password, new_password):
    self._changeLocalPassword(user_name, old_password, new_password)
    try:
      self._changeGooglePassword(user_name, new_password)
    except Exception, e1:
      try: 
        self._changeLocalPassword(user_name, new_password, old_password)
      except Exception, e2:
        raise PasswdException("Failed rollback password. " + str(e2),
                              ERR_FATAL)
      else:
        raise PasswdException("Failed to change google password. " + str(e1),
                              ERR_FATAL)
    return True

  def _changeGooglePassword(self, user_name, new_password):

    return True

  def _changeLocalPassword(self, user_name, old_password, new_password):
    raise NotImplementedError('Child class must implement me.')

  def _prepare(self, config):
    raise NotImplementedError('Child class must implement me.')

class BaseSyncPasswdEngine(BasePasswdEngine):

  def __init__(self, config):
    self.domain = config.get('apps.domain')
    self.domain_admin = config.get('apps.domain_admin')
    self.admin_passwd = config.get('apps.admin_passwd')
    self.ready = False
    self._prepare(config)

  def _login(self):
    email = self.domain_admin + '@' + self.domain
    self.apps_client = gdata.apps.service.AppsService(
      email=email, domain=self.domain, password=self.admin_passwd,
      source='gheimdall')
    self.apps_client.ProgrammaticLogin()
    self.ready = True
    
  def _changeLocalPassword(self, user_name, old_password, new_password):
    raise NotImplementedError('Child class must implement me.')

  def _prepare(self, config):
    raise NotImplementedError('Child class must implement me.')

  def _changeGooglePassword(self, user_name, new_password):

    try:
      if not self.ready:
        self._login()
        self.target_user = self.apps_client.RetrieveUser(user_name)
        self.target_user.login.password = new_password
        self.target_user = self.apps_client.UpdateUser(user_name,
                                                       self.target_user)
    except Exception,e:
      self._cleanup()
      # TODO: log something
      raise PasswdException("Failed to change google password.", ERR_FATAL)

    self._cleanup()
    return True

  def _cleanup(self):

    del(self.apps_client)

def createPasswdEngine(engine, config):

  exec('from gheimdall.passwd import %s' % engine)
  ret = eval('%s.cls(config)' % engine)
  return ret
