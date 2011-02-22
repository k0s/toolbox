"""
request handlers:
these are instantiated for every request, then called
"""

import os
from pkg_resources import resource_filename
from urlparse import urlparse
from webob import Response, exc
from tempita import HTMLTemplate

class HandlerMatchException(Exception):
    """the handler doesn't match the request"""

class Handler(object):

    methods = set(['GET']) # methods to listen to
    handler_path = [] # path elements to match        

    @classmethod
    def match(cls, app, request):

        # check the method
        if request.method not in cls.methods:
            return None

        # check the path
        if request.environ['path'] != cls.handler_path:
            return None

        # check the constructor
        try:
            return cls(app, request)
        except HandlerMatchException:
            return None
    
    def __init__(self, app, request):
        self.app = app
        self.request = request
        self.application_path = urlparse(request.application_url)[2]

    def link(self, path=(), permanant=False):
        """create a link"""
        if isinstance(path, basestring):
            path = [ path ]
        path = [ i.strip('/') for i in path ]
        if permanant:
            application_url = [ self.request.application_url ]
        else:
            application_url = [ self.application_path ]
        path = application_url + path
        return '/'.join(path)

    def redirect(self, location):
        raise exc.HTTPSeeOther(location=location)

class TempitaHandler(Handler):

    template_dirs = [ resource_filename(__name__, 'templates') ]
    
    def __init__(self, app, request):
        Handler.__init__(self, app, request)
        self.data = { 'request': request,
                      'link': self.link }

    def __call__(self):
        return getattr(self, self.request.method.title())()

    def find_template(self, template):
        for d in self.template_dirs:
            path = os.path.join(d, template)
            if os.path.exists(path):
                return HTMLTemplate.from_filename(path)

    def Get(self):
        # needs to have self.template set
        template = self.find_template(self.template)
        return Response(content_type='text/html',
                        body=template.substitute(**self.data))

class QueryView(TempitaHandler):
    """general view to query all projects"""
    
    template = 'index.html'
    methods=set(['GET'])

    def __init__(self, app, request):
        TempitaHandler.__init__(self, app, request)
        projects = self.app.model.get(**self.request.GET.mixed())
        self.data['projects'] = projects
        self.data['fields'] = self.app.model.fields()
        self.data['title'] = 'Tools'

class ProjectView(TempitaHandler):
    """view of a particular project"""

    template = 'index.html'
    methods=set(['GET'])

    @classmethod
    def match(cls, app, request):

        # check the method
        if request.method not in cls.methods:
            return None

        # the path should match a project
        if len(request.environ['path']) != 1:
            return None

        # get the project if it exists
        project = app.model.project(request.environ['path'][0])
        if not project:
            return None

        # check the constructor
        try:
            return cls(app, request, project)
        except HandlerMatchException:
            return None

    def __init__(self, app, request, project):
        TempitaHandler.__init__(self, app, request)
        self.data['fields'] = self.app.model.fields()
        self.data['projects'] = [project]
        self.data['title'] = project['name']
