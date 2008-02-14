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

from turbogears import widgets, validators, url, config
import formencode

class PasswdSchema(formencode.Schema):
  filter_extra_fields = True
  allow_extra_fields = True
  chained_validators = [validators.FieldsMatch(
    'new_password',
    'password_confirm',
    messages = {'invalidNoMatch': _("New password does not match")}
  )]

class PasswdFormWidget(widgets.TableForm):

  def __init__(self, regex="^.+$"):
    backURL = widgets.HiddenField(
      'backURL', validator=validators.UnicodeString())
    SAMLRequest = widgets.HiddenField(
      'SAMLRequest', validator=validators.UnicodeString())
    RelayState = widgets.HiddenField(
      'RelayState', validator=validators.UnicodeString())
    user_name = widgets.HiddenField(
      'user_name', validator=validators.UnicodeString(not_empty=True))
    old_password = widgets.PasswordField(
      'old_password', label=_('Old password:'), attrs=dict(size=16),
      validator=validators.UnicodeString(not_empty=True))
    new_password = widgets.PasswordField(
      'new_password', label=_('New password:'), attrs=dict(size=16),
      validator=validators.All(
        validators.UnicodeString(not_empty=True),
        validators.Regex(
          regex,
          messages = {'invalid': _("Input does not match our password policy")}
        )))
    password_confirm = widgets.PasswordField(
      'password_confirm', label=_('Confirm:'), attrs=dict(size=16),
      validator=validators.UnicodeString(not_empty=True))
    super(PasswdFormWidget, self).__init__(
      'passwd_form',
      fields=[SAMLRequest, RelayState, user_name, old_password, new_password,
              password_confirm, backURL],
      action=url('/passwd.do'),
      submit_text=_('Change password'),
      validator=PasswdSchema())

class LoginFormWidget(widgets.TableForm):

  def __init__(self):
    SAMLRequest = widgets.HiddenField(
      'SAMLRequest',
      validator=validators.UnicodeString(not_empty=True))
    RelayState = widgets.HiddenField(
      'RelayState',
      validator=validators.UnicodeString())
    user_name = widgets.TextField(
      'user_name', label=_('User Name:'), attrs=dict(size=16),
      validator=validators.UnicodeString(
      not_empty=True,
      messages = {
      'empty': _("Please enter a value"),
      'badType': _("The input must be a string (not a %(type)s: %(value)r)"),
      'noneType': _("The input must be a string (not None)"),
      }))
    password = widgets.PasswordField(
      'password', label=_('Password:'), attrs=dict(size=16),
      validator=validators.UnicodeString(
      not_empty=True,
      messages = {
      'empty': _("Please enter a value"),
      'badType': _("The input must be a string (not a %(type)s: %(value)r)"),
      'noneType': _("The input must be a string (not None)"),
      }))
    if config.get('always_remember_me', False):
      super(LoginFormWidget, self).__init__(
        'login_form',
        fields=[SAMLRequest, RelayState, user_name, password],
        action=url('/login.do'),
        submit_text=_('Login'))
    else:
      remember_me = widgets.CheckBox(
        'remember_me', label=_('Remember me on this computer:'))
      super(LoginFormWidget, self).__init__(
        'login_form',
        fields=[SAMLRequest, RelayState, user_name, password, remember_me],
        action=url('/login.do'),
        submit_text=_('Login'))

class ResetFormWidget(widgets.TableForm):

  def __init__(self):
    user_name = widgets.TextField(
      'user_name', label=_('User Name:'), attrs=dict(size=16),
      validator=validators.UnicodeString(
      not_empty=True,
      messages = {
      'empty': _("Please enter a value"),
      'badType': _("The input must be a string (not a %(type)s: %(value)r)"),
      'noneType': _("The input must be a string (not None)"),
      }))
    super(ResetFormWidget, self).__init__(
      'reset_form',
      fields=[user_name],
      action=url('/manage_reset_passwd.do'),
      submit_text=_('Reset'))
