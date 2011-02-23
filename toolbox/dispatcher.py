"""
request dispatcher:
data persisting across requests should go here
"""

import os

from handlers import FieldView
from handlers import ProjectView
from handlers import QueryView
from model import MemoryCache
from pkg_resources import resource_filename
from webob import Request, Response, exc

class Dispatcher(object):

    ### class level variables
    defaults = { 'template_dirs': ''}

    def __init__(self, directory, **kw):

        # set instance parameters from kw and defaults
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))

        # JSON blob directory
        assert os.path.exists(directory) and os.path.isdir(directory)
        self.directory = directory

        # model -- TODO: make pluggable via setuptools entry points
        self.model = MemoryCache(self.directory)

        # request handlers
        self.handlers = [ FieldView, ProjectView, QueryView ]

    def __call__(self, environ, start_response):

        # get a request object
        request = Request(environ)

        # get the path 
        path = request.path_info.strip('/').split('/')
        if path == ['']:
            path = []
        request.environ['path'] = path

        # match the request to a handler
        for h in self.handlers:
            handler = h.match(self, request)
            if handler is not None:
                break
        else:
            handler = exc.HTTPNotFound

        # get response
        res = handler()
        return res(environ, start_response)
