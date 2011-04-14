"""
request dispatcher WSGI app:
data persisting across requests should go here
"""

import os

from handlers import CreateProjectView
from handlers import DeleteProjectHandler
from handlers import FieldView
from handlers import ProjectView
from handlers import QueryView
from handlers import TagsView
from handlers import AboutView

from model import CouchCache
from model import MemoryCache
from pkg_resources import resource_filename
from webob import Request, Response, exc

# storage models
models = {'memory_cache': MemoryCache,
          'couch': CouchCache}

class Dispatcher(object):
    """toolbox WSGI app which dispatchers to associated handlers"""

    # class defaults
    defaults = { 'about': None, # file path to ReST about page
                 'model_type': 'memory_cache', # type of model to use
                 'reserved': set(['css', 'js', 'img']), # reserved URL namespaces
                 'template_dir': None, # directory for template overrides
                 }

    def __init__(self, **kw):
        """
        **kw arguments used to override defaults
        additional **kw are passed to the model
        """

        # set instance parameters from kw and defaults
        for key in self.defaults:
            setattr(self, key, kw.pop(key, self.defaults[key]))

        # model: backend storage and accessors
        if self.model_type not in models:
            raise AssertionError("model_type '%s' not found in %s" % (self.model_type, models.keys()))
        self.model = models[self.model_type](**kw)

        # request handlers in order they will be tried
        self.handlers = [ TagsView,
                          CreateProjectView,
                          FieldView,
                          ProjectView,
                          QueryView,
                          DeleteProjectHandler ]

        # add an about view if file specified
        if self.about:
            about = file(self.about).read()
            import docutils.core
            about = docutils.core.publish_parts(about, writer_name='html')['body']
            self.about = about
            self.handlers.append(AboutView)

        # extend reserved URLS from handlers
        for handler in self.handlers:
            if handler.handler_path:
                self.reserved.add(handler.handler_path[0])

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
            # TODO: our own 404 handler with a menu
            handler = exc.HTTPNotFound

        # get response
        res = handler()
        return res(environ, start_response)
