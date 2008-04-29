#wsgi_testutil.py
# Many code snippets stolen from Titus Brown
# http://www.advogato.org/article/874.html
from turbogears import testutil
from gheimdall.controllers import Root
import cherrypy
from twill import wsgi_intercept

class WSGITest(testutil.DBTest):
  def setUp(self):
    testutil.DBTest.setUp(self)

    _cached_app = {}
    ### dynamically created function to build & return a WSGI app
    ### for a CherryPy Web app.
    def get_wsgi_app(_cached_app=_cached_app):
      if not _cached_app:
        cherrypy.root = Root()
        # configure cherrypy to be quiet ;)
        #cherrypy.config.update({ "server.logToScreen" : False })
        testutil.start_cp()
        # get WSGI app.
        from cherrypy._cpwsgi import wsgiApp
        _cached_app['app'] = wsgiApp
      return _cached_app['app']

    wsgi_intercept.add_wsgi_intercept('localhost', 80, get_wsgi_app)
    self._setUp()

  def tearDown(self):
    wsgi_intercept.remove_wsgi_intercept('localhost', 80)
    # shut down the cherrypy server.
    #cherrypy.server.stop()
    testutil.DBTest.tearDown(self) 
    self._tearDown()
