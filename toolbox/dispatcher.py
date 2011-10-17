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
from handlers import NotFound

from model import models
from util import strsplit
from webob import Request, Response, exc

here = os.path.dirname(os.path.abspath(__file__))

class Dispatcher(object):
    """toolbox WSGI app which dispatchers to associated handlers"""

    # class defaults
    defaults = { 'about': None, # file path to ReST about page
                 'model_type': 'memory_cache', # type of model to use
                 'handlers': None,
                 'reload': True, # reload templates
                 'reserved': None, # reserved URL namespaces
                 'template_dir': None, # directory for template overrides
                 'baseurl': '', # base URL for redirects

                 # branding variables
                 'site_name': 'toolbox', # name of the site
                 'item_name': 'tool', # name of a single item
                 'item_plural': None, # item_name's plural, or None for item_name + 's'
                 }

    def __init__(self, **kw):
        """
        **kw arguments used to override defaults
        additional **kw are passed to the model
        """

        # set instance parameters from kw and defaults
        for key in self.defaults:
            setattr(self, key, kw.pop(key, self.defaults[key]))
        if self.item_plural is None:
            self.item_plural = self.item_name + 's'

        # should templates be reloaded?
        if isinstance(self.reload, basestring):
            self.reload = self.reload.lower() == 'true'

        # model: backend storage and associated methods
        if 'fields' in kw and isinstance(kw['fields'], basestring):
            # split fields if given as a string
            kw['fields'] = strsplit(kw['fields'])
        if hasattr(self.model_type, '__call__'):
            model = self.model_type
        elif self.model_type in models:
            model = models[self.model_type]
        else:
            try:
                import pyloader
                model = pyloader.load(self.model_type)
            except:
                raise AssertionError("model_type '%s' not found in %s" % (self.model_type, models.keys()))
        self.model = model(**kw)

        # add an about view if file specified
        if self.about:
            about = file(self.about).read()
            import docutils.core
            about = docutils.core.publish_parts(about, writer_name='html')['body']
            self.about = about


        # request handlers in order they will be tried
        if self.handlers is None:
            self.handlers = [ TagsView,
                              CreateProjectView,
                              FieldView,
                              QueryView,
                              DeleteProjectHandler,
                              ProjectView]
            if self.about:
                self.handlers.append(AboutView)

        # extend reserved URLS from handlers
        if self.reserved is None:
            self.reserved = set(['css', 'js', 'img'])
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
            # our 404 handler
            handler = NotFound(self, request)

        # get response
        res = handler()
        return res(environ, start_response)
