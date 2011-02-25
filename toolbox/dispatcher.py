"""
request dispatcher:
data persisting across requests should go here
"""

import os

from handlers import CreateProjectView
from handlers import DeleteProjectHandler
from handlers import FieldView
from handlers import ProjectView
from handlers import QueryView

from model import CouchCache
from model import MemoryCache
from pkg_resources import resource_filename
from webob import Request, Response, exc

models = {'memory_cache': MemoryCache,
          'couch': CouchCache}

class Dispatcher(object):

    ### class level variables
    defaults = { 'template_dirs': '',
                 'model_type': 'memory_cache'}

    def __init__(self, directory, **kw):

        # set instance parameters from kw and defaults
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))

        # JSON blob directory
        assert os.path.exists(directory) and os.path.isdir(directory)
        self.directory = directory

        # model: backend storage and accessors
        if self.model_type not in models:
            raise AssertionError("model_type '%s' not found in %s" % (self.model_type, models.keys()))
        self.model = models[self.model_type](directory)

        # request handlers in order they will be tried
        self.handlers = [ CreateProjectView, FieldView, ProjectView, QueryView, DeleteProjectHandler ]

    def __call__(self, environ, start_response):

        # get a request object
        request = Request(environ)

        # get the path 
        path = request.path_info.strip('/').split('/')
        if path == ['']:
            path = []
        request.environ['path'] = path

        # load any new data
        self.model.load()

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
