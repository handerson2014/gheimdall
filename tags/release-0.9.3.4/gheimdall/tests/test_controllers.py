#test_views.py
# Some code snippets stolen from Titus Brown
# http://www.advogato.org/article/874.html
from turbogears import testutil, database
import gheimdall.model
import cherrypy
import wsgi_testutil
import twill
from StringIO import StringIO

database.set_db_uri("sqlite:///:memory:")

class TestPages(wsgi_testutil.WSGITest):

  model = gheimdall.model

  def format(self, msg):
    return msg + "\nhtml: %s\n" % self.b.response().read()

  def _setUp(self):
    self.outp = StringIO()
    twill.set_output(self.outp) 
    testutil.capture_log("gheimdall.controllers")

  def _tearDown(self):
    print "log: %s\nout: %s\n" % (str(testutil.get_log()),
                                  str(self.outp.read()))
  
  def test_login_page(self):
    """Test for login"""

    from twill._browser import PatchedMechanizeBrowser as Browser
    b = Browser()
    self.b = b
    response1 = b.open("http://localhost/login?SAMLRequest=fZLLTsMwEEX3SPyD5X1eCCSwmlQFhKjEI2oDC3auO0mM7HHwOC38PWkKAhZ0O56Ze%2B71TKbv1rANeNIOc57FKWeAyq01Njl%2Fqm6icz4tjo8mJK3pxKwPLS7grQcKbJhEEuNDznuPwknSJFBaIBGUWM7u78RJnIrOu%2BCUM5zNr3MOr2ibWjqNboXWatm1yrxaqVvVWItQY9tJbFacPX9jneyw5kQ9zJGCxDCU0vQ8Sk%2Bj7KxKL8RZKrL0hbPyS%2BlS497BIazVvonEbVWVUfm4rMYFG70G%2FzB057xxrjEQK2c5mxGBDwPOlUPqLfgl%2BI1W8LS4y3kbQkciSbbbbfwzlMgkDEHF1EIrKUYIiVS0c1JKIr0ZFGppCHgxxitGh%2F5Xrof55TcRL340J8mvVcXXt%2B3czK9LZ7T6YDNj3PbKgwyDfvA9cHbjvJXhf7UszsaKXkf12Cp6pA6UrjWsOUuKverf%2Bxiu5hM%3D&RelayState=https%3A%2F%2Fwww.google.com%2Fa%2Ftest.shehas.net%2FServiceLogin%3Fservice%3Dmail%26passive%3Dtrue%26rm%3Dfalse%26continue%3Dhttps%253A%252F%252Fmail.google.com%252Fa%252Ftest.shehas.net%252F%26ltmpl%3Ddefault%26ltmplcache%3D2")
    #assert False, "html: %s" % b.response().read()
    b.select_form("login_form")
    b["user_name"] = "tmatsuo"
    b["password"] = "good"
    respose2 = b.submit()
    assert b.title() == "Logging in...", self.format("Login failed")
    b.select_form("acsForm")
    # TODO: check SAMLResponse value
    #print b["SAMLResponse"]
    #assert False, self.format("")

# import unittest
# import turbogears
# from turbogears import testutil
# from gheimdall.controllers import Root
# import cherrypy

# class TestPages(unittest.TestCase):

#   def setUp(self):
#     turbogears.startup.startTurboGears()

#   def tearDown(self):
#     """Tests for apps using identity need to stop CP/TG after each test to
#     stop the VisitManager thread. 
#     See http://trac.turbogears.org/turbogears/ticket/1217 for details.
#     """
#     #turbogears.startup.stopTurboGears()

#   def test_sign_in(self):
#     """Tests for sign in.
#     """
#     cherrypy.root = Root()
#     user = testutil.BrowsingSession()
#     user.goto("/login?SAMLRequest=fZJNT8MwDIbvSPyHKPd%2BTSChaC0aIMQkPipWOHDLOrfNSO0Spxv8e7puCDjA1bH9Pu8bT8%2FfWys24NgQpjIJYykAS1oZrFP5VFwHZ%2FI8Oz6asm5tp2a9b%2FAR3npgL4ZJZDU%2BpLJ3qEizYYW6BVa%2BVIvZ3a2ahLHqHHkqyUoxv0olVRU1FpfUVVDX2raIQNBBq9c1dmCWa0u4fiUpnr%2BwJjusOXMPc2Sv0Q%2BlOD4L4pMgOS3iRE0SdXL6IkV%2BULowuHfwH9Zy38TqpijyIH9YFOOCjVmBux%2B6U1kT1RbCklopZszg%2FIBzSch9C24BbmNKeHq8TWXjfccqirbbbfg9FOnID0GF3ECjOUTwkS555yTXzGYzKFTaMshsjFeNDt2PXP%2Fn119EMvvWnEY%2FVmWHb9u5mV%2FlZE35IWbW0vbSgfaDvnc9SHFNrtX%2Bb7UkTMaKWQXV2Kp65A5KUxlYSRFle9Xf9zFczSc%3D&RelayState=https%3A%2F%2Fwww.google.com%2Fa%2Ftest.shehas.net%2FServiceLogin%3Fservice%3Dmail%26passive%3Dtrue%26rm%3Dfalse%26continue%3Dhttps%253A%252F%252Fmail.google.com%252Fa%252Ftest.shehas.net%252F%26ltmpl%3Ddefault%26ltmplcache%3D2")
#     assert user.status == "200 OK", "status: %s" % user.status
#     assert "Login" in user.response, "response: %s" % user.response
