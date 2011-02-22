import os

from dispatcher import Dispatcher
from paste.httpexceptions import HTTPExceptionHandler
from paste.urlparser import StaticURLParser
from pkg_resources import resource_filename

class PassthroughFileserver(object):
    """serve files if they exist"""

    def __init__(self, app, directory):
        self.app = app
        self.directory = directory
        self.fileserver = StaticURLParser(self.directory)

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')
        if path and os.path.exists(os.path.join(self.directory, path)):
            return self.fileserver(environ, start_response)
        return self.app(environ, start_response)

def factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""

    keystr = 'toolbox.'
    args = dict([(key.split(keystr, 1)[-1], value)
                 for key, value in app_conf.items()
                 if key.startswith(keystr) ])
    app = Dispatcher(**args)
    return HTTPExceptionHandler(PassthroughFileserver(app, resource_filename(__name__, 'static')))
    
