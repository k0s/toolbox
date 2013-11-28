#!/usr/bin/env python

"""
WSGI -> HTTP server factories for toolbox
"""

import os
import sys

from dispatcher import Dispatcher
from paste.urlparser import StaticURLParser
from pkg_resources import resource_filename
from theslasher import TheSlasher

class PassthroughFileserver(object):
    """serve files if they exist"""

    def __init__(self, app, directory):
        self.app = app
        self.directory = directory
        self.fileserver = StaticURLParser(self.directory)

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')
        if path and os.path.exists(os.path.join(self.directory, path)) and '..' not in path:
            return self.fileserver(environ, start_response)
        return self.app(environ, start_response)


def paste_factory(global_conf=None, **app_conf):
    """create a webob view and wrap it in middleware"""

    keystr = 'toolbox.'
    static_directory = app_conf.pop('static',
                                    resource_filename(__name__, 'static'))
    args = dict([(key.split(keystr, 1)[-1], value)
                 for key, value in app_conf.items()
                 if key.startswith(keystr) ])
    app = TheSlasher(Dispatcher(**args)) # kill slashes
    return PassthroughFileserver(app, static_directory)

def wsgiref_factory(host='0.0.0.0', port=8080):
    """wsgiref factory; for testing only"""

    from wsgiref import simple_server
    app = Dispatcher()
    app = PassthroughFileserver(app, resource_filename(__name__, 'static'))
    server = simple_server.make_server(host=host, port=int(port), app=app)
    fqdn = '127.0.0.1' if host =='0.0.0.0' else host
    print "Serving toolbox at http://%s:%d/" % (fqdn, port)
    server.serve_forever()


# WSGI factories available
factories = {'paste': paste_factory,
             'wsgiref': wsgiref_factory}

def main(args=sys.argv[1:]):
    """CLI entry point"""

    # parse command line
    usage = '%prog [options]'
    import argparse
    parser = argparse.ArgumentParser(usage=usage, description=__doc__.strip())
    parser.add_argument('--factory', default='wsgiref',
                        choices=factories.keys(),
                        help="factory to use")
    parser.add_argument('--port', type=int, default=8080,
                        help="port to serve on")
    args = parser.parse_args()

    # serve toolbox
    factory = factories[args.__dict__.pop('factory')]
    factory_args = args.__dict__
    print "Serving using factory: %s" % getattr(factory, '__name__', str(factory))
    print "Factory arguments: %s" % factory_args
    factory(**factory_args)

if __name__ == '__main__':
    main()
