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
#   $Id: sample.py 2 2007-07-20 03:11:43Z matsuo.takashi $

__author__ = 'tmatsuo@sios.com (Takashi MATSUO)'

from gheimdall import auth
import subprocess

class ExternalAuthEngine(auth.BaseAuthEngine):

  def _prepare(self, config):
    self.command = config.get('external.command')
    self.use_env = config.get('external.use_env')
    self.env_user = config.get('external.env_user')
    self.env_password = config.get('external.env_password')
    self.stdin_format = config.get('external.stdin_format')

  def _authenticate(self, user_name, password):
    env = {}
    if self.use_env:
      if self.env_user is None:
        raise auth.AuthException(
          'You must set external.env_user'
          ' when you set external.use_env to True.',
          auth.ERR_UNKNOWN)
      if self.env_password is None:
        raise auth.AuthException(
          'You must set external.env_password'
          ' when you set external.use_env to True.',
          auth.ERR_UNKNOWN)
      env[self.env_user] = user_name
      env[self.env_password] = password
    p = subprocess.Popen([self.command], env=env, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, close_fds=True)
    if not self.use_env:
      if self.stdin_format is None:
        raise auth.AuthException(
          'You must set external.stdin_format'
          ' when you set external.use_env to False',
          auth.ERR_UNKNOWN)
      p.stdin.write(self.stdin_format % (user_name, password))
    ret = p.wait()
    if ret == 0:
      return True
    else:
      raise auth.AuthException(
          'login failure. The return code is %d.' % ret,
          auth.ERR_UNKNOWN)

cls = ExternalAuthEngine
