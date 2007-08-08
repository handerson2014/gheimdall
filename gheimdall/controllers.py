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

from turbogears import controllers, expose, flash, error_handler, validate
from turbogears import exception_handler, config, errorhandling
import cherrypy
# from model import *
import logging
from gheimdall import utils, errors, widgets, auth, passwd
try:
  import turbomail
  has_turbomail = True
except:
  has_turbomail = False

__all__ = ['ErrorCatcher']

log = logging.getLogger("gheimdall.controllers")
login_form_widget = widgets.LoginFormWidget()
passwd_form_widget = widgets.PasswdFormWidget(
  regex=config.get('apps.passwd_regex'))

ERROR_MAIL_TMPL = """\
----------URL----------

%(url)s

----------DATA:----------

%(data)s
"""

class ErrorCatcher(controllers.RootController):
  """Base class for RootControllers that catches errors in production mode.

  Sends an email to the admin, when an error occurs. Does not send email
  on 404 errors unless the 'error_catcher.send_email_on_404' configuration
  option is set to True.

  For email sending to work, at least the configuration options
  'error_catcher.sender_email' and 'error_catcher.admin_email' must be
  set to valid email addresses.

  See docstring for method 'send_exception_email' for more email related
  configuration information.
  """

  _error_codes = {
      None: u'General Error',
      400: u'400 - Bad Request',
      401: u'401 - Unauthorized',
      403: u'403 - Forbidden',
      404: u'404 - Not Found',
      500: u'500 - Internal Server Error',
      501: u'501 - Not Implemented',
      502: u'502 - Bad Gateway',
  }
  _error_templates = {
      None: '.templates.unhandled_exception',
      404: '.templates.404_exception',
  }
  admin_group_name = 'admin'
  output_format = 'html'
  content_type = 'text/html'

  def __init__(self, *args, **kw):
    super(ErrorCatcher, self).__init__(*args, **kw)
    self.sender_email = config.get('error_catcher.sender_email')
    self.admin_email = config.get('error_catcher.admin_email')
    self.smtp_host = config.get('error_catcher.smtp_host', 'localhost')
    self.smtp_user = config.get('error_catcher.smtp_user')
    self.smtp_passwd = config.get('error_catcher.smtp_passwd')

  def cp_on_http_error(self, status, message):
    """Handle HTTP errors by sending an error page and email."""

    try:
      cherrypy._cputil._cp_on_http_error(status, message)
      error_msg = self.get_error_message(status, message)
      url = "%s %s" % (cherrypy.request.method, cherrypy.request.path)
      log.exception("CherryPy %s error (%s) for request '%s'", status,
        error_msg, url)

      if status != 404:
        buf = StringIO.StringIO()
        traceback.print_exc(file=buf)
        details = buf.getvalue()
        buf.close()
      else:
        details = '404 error'

      data = dict(
          status = status,
          message = message,
          error_msg = error_msg,
          admin = identity.in_group(self.admin_group_name),
          url = url,
          details = details,
      )

      if status != 404 or config.get('error_catcher.send_email_on_404'):
        try:
          self.send_exception_email(status, url, details)
          data['email_sent'] = True
        except Exception, exc:
          log.exception('Error email failed: %s', exc)
          data['email_sent'] = False
      else:
        data['email_sent'] = False

      self.send_error_page(status, data)
    # don't catch SystemExit
    except StandardError, exc:
      log.exception('Error handler failed: %s', exc)

  # Hook in error handler for production only
  if config.get('server.environment') == 'production':
    _cp_on_http_error = cp_on_http_error

  def send_error_page(self, status, data):
    """Send error page using matching template from self._error_templates.
    """

    body = controllers._process_output(
        data,
        self._error_templates.get(status, self._error_templates.get(None)),
        self.output_format,
        self.content_type,
        None
    )
    cherrypy.response.headers['Content-Length'] = len(body)
    cherrypy.response.body = body

  def send_exception_email(self, status, url, data):
    """Send an email with the error info to the admin.

    Uses TurboMail if installed and activated, otherwise tries to send
    email with the smtplib module. The SMTP settings can be configured
    with the following configuration settings:

    error_catcher.smtp_host   - Mail server to connect to
      (default 'localhost')
    error_catcher.smtp_user   - User name for SMTP authentication.
      If unset no SMTP login is performed.
    error_catcher.smtp_passwd - Password for SMTP authentication
    """

    if not self.sender_email or not  self.admin_email:
      log.exception('Configuration error: could not send error'
        'because sender and/or admin email address is not set.')
      raise RuntimeError

    subject =  '%d ERROR on the Server' % status
    text = ERROR_MAIL_TMPL % dict(url=url, data=data)

    if has_turbomail and config.get('mail.on'):
      msg = turbomail.Message(self.sender_email, self.admin_email, subject)
      msg.plain = text
      turbomail.enqueue(msg)
    else:
      from email.MIMEMultipart import MIMEMultipart
      from email.MIMEText import MIMEText
      from email.Utils import formatdate
      msg = MIMEMultipart()
      msg['From'] = self.sender_email
      msg['To'] = self.admin_email
      msg['Date'] = formatdate(localtime=True)
      msg['Subject'] = subject
      msg.attach(MIMEText(text))
      self._send_email_smtp(self.sender_email, self.admin_email,
        msg.as_string())

  def _send_email_smtp(self, from_addr, to_addr, message):
    """Send email via SMTP."""

    import smtplib
    smtp = smtplib.SMTP(self.smtp_host)
    if self.smtp_user and self.smtp_passwd:
      smtp.login(self.smtp_user, self.smtp_passwd)
    smtp.sendmail(from_addr, to_addr, message)
    smtp.close()

  def get_error_message(self, status, default=None):
    """Return string error for HTTP status code."""

    return self._error_codes.get(status, default or self._error_codes[None])

class Root(controllers.RootController):

  @expose(template="gheimdall.templates.gheimdall-logout")
  def logout(self):
    useSSL = cherrypy.session.get('useSSL')
    if useSSL:
      scheme = 'https'
    else:
      scheme = 'http'
    url = scheme + '://mail.google.com/a/' + config.get('apps.domain') + '/'
    # delete session data
    cherrypy.session = dict()
    return dict(url=url)

  @expose(template="gheimdall.templates.gheimdall-login")
  def login(self, SAMLRequest, RelayState, *args, **kw):
    if config.get('apps.use_header_auth'):
      # header auth
      # retrieve user name from header
      key = config.get('apps.auth_header_key')
      user_name = cherrypy.request.headers.get(key, None)
      if user_name is None:
        raise errors.GheimdallException('Can not retrieve user name.')

      ret = utils.createLoginDict(SAMLRequest, RelayState, user_name)
      ret['tg_template'] = 'gheimdall.templates.gheimdall-login-success'
      return ret

    remember_me = None
    authenticated = None
    try:
      remember_me = cherrypy.session['remember_me']
      authenticated = cherrypy.session['authenticated']
    except KeyError:
      # ignore KeyError
      pass
    if remember_me and authenticated:
      ret = utils.createLoginDict(SAMLRequest, RelayState,
                                  cherrypy.session['user_name'])
      ret['tg_template'] = 'gheimdall.templates.gheimdall-login-success'
      return ret
      
    tg_exception = kw.get('tg_exceptions', None)
    if tg_exception is not None:
      log.error(tg_exception)
    return dict(form=login_form_widget,
                values=dict(SAMLRequest=SAMLRequest,RelayState=RelayState))

  @expose(template="gheimdall.templates.gheimdall-login-success")
  @error_handler(login)
  @exception_handler(login,
                     rules="isinstance(tg_exceptions,errors.GheimdallException)")
  @validate(form=login_form_widget)
  def login_do(self, SAMLRequest, RelayState, user_name, password,
               **kw):
    cherrypy.session['remember_me'] = kw.get('remember_me', False)
    if config.get('apps.use_header_auth', False):
      raise errors.GheimdallException(
        'You can not use this method when ' +
        'app.use_header_auth configration directive is set to True.')

    # authentication
    auth_engine = auth.createAuthEngine(engine=config.get('apps.auth_engine'),
                                    config=config)
    try:
      auth_engine.authenticate(user_name, password)
    except auth.AuthException, e:
      if e.code == auth.NEW_AUTHTOK_REQD:
        # When the user's password is expired, display password form if I can.
        log.error(e)
        flash(_('Password is expired. You need to set new password.'))
        if not config.get('apps.use_change_passwd'):
          flash(_('Password is expired. You need to set new password. ' +
                  'But changing password is not available here'))
          return dict(user_name=user_name,
                      tg_template="gheimdall.templates.gheimdall-nopasswd")
        # save user_name to session
        cherrypy.session['user_name'] = user_name
        return dict(tg_template="gheimdall.templates.gheimdall-passwd",
                    form=passwd_form_widget,
                    values=dict(backURL='',
                                user_name=user_name,
                                old_password=password,
                                SAMLRequest=SAMLRequest,
                                RelayState=RelayState))
      # Failed.
      flash(_('Can not login'))
      raise errors.GheimdallException(e.reason)

    return utils.createLoginDict(SAMLRequest, RelayState, user_name)

  @expose(template="gheimdall.templates.gheimdall-passwd")
  def passwd(self, *args, **kw):
    tg_exception = kw.get('tg_exceptions', None)
    if tg_exception is not None:
      log.error(tg_exception)

    # First, check user_name value from get parameter
    user_name = kw.get('user_name', None)

    # Second, check user_name value from args
    if user_name is None:
      try:
        user_name = args[0]
      except:
        pass

    backURL = ''

    # Third, retrieve user_name value from session
    if user_name is None:
      # There must be an user_name in the session.
      user_name = cherrypy.session.get('user_name')
      backURL = 'http://mail.google.com/a/%s/' % config.get('apps.domain')
      
    if user_name is None:
      raise errors.GheimdallException('Can not retrieve user name.')

    if not config.get('apps.use_change_passwd'):
      # changing password is not available.
      flash(_('Changing password is not available here'))
      return dict(user_name=user_name,
                  tg_template="gheimdall.templates.gheimdall-nopasswd")

    # display password form.
    return dict(form=passwd_form_widget,
                values=dict(user_name=user_name, backURL=backURL))

  @expose(template="gheimdall.templates.gheimdall-passwd-success")
  @error_handler(passwd)
  @exception_handler(passwd,
                     rules="isinstance(tg_exceptions,errors.GheimdallException)")
  @validate(form=passwd_form_widget)
  def passwd_do(self, user_name, old_password, new_password, password_confirm,
                SAMLRequest, RelayState, backURL):
    # changing password
    if not config.get('apps.use_change_passwd'):
      flash(_('Changing password is not available here'))
      return dict(user_name=user_name,
                  tg_template="gheimdall.templates.gheimdall-nopasswd")
    passwd_engine = passwd.createPasswdEngine(
      engine=config.get('apps.passwd_engine'),
      config=config)
    try:
      passwd_engine.changePassword(user_name,
                                   old_password,
                                   new_password)
    except passwd.PasswdException, e:
      # changing password failed
      flash(_('Failed to change password'))
      raise errors.GheimdallException(e.reason)

    if SAMLRequest != "":
      # User's password was expired. Now, we can let them in...
      ret = utils.createLoginDict(SAMLRequest, RelayState, user_name)
      ret['tg_template'] = 'gheimdall.templates.gheimdall-login-success'
      return ret

    return dict(user_name=user_name, backURL=backURL)
