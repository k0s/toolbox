import os

from dispatcher import Dispatcher
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


def paste_factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""

    keystr = 'toolbox.'
    args = dict([(key.split(keystr, 1)[-1], value)
                 for key, value in app_conf.items()
                 if key.startswith(keystr) ])
    app = Dispatcher(**args)
    return PassthroughFileserver(app, resource_filename(__name__, 'static'))

try:
    from relocator import Relocator
    def relocator_factory(global_conf, **app_conf):
        """
        create a toolbox app that uses relocator to set outgoing Location headers:
        http://k0s.org/hg/relocator
        """
        baseurl = app_conf.pop('baseurl')
        app = paste_factory(global_conf, **app_conf)
        return Relocator(app, baseurl)
    
except ImportError:
    pass # relocator unvailable

def wsgiref_factory(host='0.0.0.0', port=8080):
    # for testing only
    here = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(os.path.dirname(here), 'sample')
    app = Dispatcher(directory=directory)
    app = PassthroughFileserver(app, resource_filename(__name__, 'static'))
    from wsgiref import simple_server
    server = simple_server.make_server(host=host, port=int(port), app=app)
    server.serve_forever()
    
if __name__ == '__main__':
    wsgiref_factory()
