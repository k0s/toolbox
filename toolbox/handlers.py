"""
request handlers:
these are instantiated for every request, then called
"""

import os
from datetime import datetime
from pkg_resources import resource_filename
from urlparse import urlparse
from util import JSONEncoder
from webob import Response, exc
from tempita import HTMLTemplate

try:
    import json
except ImportError:
    import simplejson as json

class HandlerMatchException(Exception):
    """the handler doesn't match the request"""

class Handler(object):
    """general purpose request handler (view)"""

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
        return exc.HTTPSeeOther(location=location)

    def query_string(self, query):
        """
        generate a query string; query is a list of 2-tuples
        """
        return '?' + '&'.join(['%s=%s' % (i,j)
                               for i, j in query])


class TempitaHandler(Handler):
    """handler for tempita templates"""

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

    def render(self, template, **data):
        template = self.find_template(template)
        if template is None:
            raise Exception("I can't find your template")
        return template.substitute(**data)

    def Get(self):
        # needs to have self.template set
        return Response(content_type='text/html',
                        body=self.render(self.template, **self.data))
    
    def navigation(self):
        """render navigation menu"""
        ### toolbox-specific function
        data = self.data.copy()
        data['fields'] = self.app.model.fields()
        return self.render('navigation.html', **data)


class ProjectsView(TempitaHandler):
    """abstract base class for view with projects"""

    def __init__(self, app, request):
        """project views specific init"""
        TempitaHandler.__init__(self, app, request)
        self.check_json()
        if not self.json:
            self.data['navigation'] = self.navigation()
            self.data['format_date'] = self.format_date

    def check_json(self):
        """check to see if the request is for JSON"""
        self.json = self.request.GET.pop('format', '') == 'json'

    def get_json(self):
        """JSON to serialize if requested"""
        return self.data['projects']

    def Get(self):
        if self.json:
            return Response(content_type='application/json',
                            body=json.dumps(self.get_json(), cls=JSONEncoder))
        return TempitaHandler.Get(self)

    def sort(self, field):
        reverse = False
        if field.startswith('-'):
            field = field[1:]
            reverse = True
        if field == 'name':
            self.data['projects'].sort(key=lambda value: value[field].lower(), reverse=reverse)
        else:
            self.data['projects'].sort(key=lambda value: value[field], reverse=reverse)

    def format_date(self, timestamp):
        """return a string representation of a timestamp"""
        return datetime.fromtimestamp(timestamp).isoformat()


class QueryView(ProjectsView):
    """general view to query all projects"""
    
    template = 'index.html'
    methods=set(['GET'])

    def __init__(self, app, request):
        ProjectsView.__init__(self, app, request)
        sort_type = self.request.GET.pop('sort', '-modified')
        self.data['projects']= self.app.model.get(**self.request.GET.mixed())
        self.sort(sort_type)
        self.data['fields'] = self.app.model.fields()
        self.data['title'] = 'Tools'


class ProjectView(ProjectsView):
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
        ProjectsView.__init__(self, app, request)
        self.data['fields'] = self.app.model.fields()
        self.data['projects'] = [project]
        self.data['title'] = project['name']


class FieldView(ProjectsView):
    """view of projects sorted by a field"""

    template = 'fields.html'

    @classmethod
    def match(cls, app, request):

        # check the method
        if request.method not in cls.methods:
            return None

        # the path should match a project
        if len(request.environ['path']) != 1:
            return None

        # ensure the field exists
        field = request.environ['path'][0]
        if field not in app.model.fields():
            return None

        # check the constructor
        try:
            return cls(app, request, field)
        except HandlerMatchException:
            return None

    def __init__(self, app, request, field):
        ProjectsView.__init__(self, app, request)
        projects = self.app.model.field_query(field)
        if projects is None:
            raise HandlerMatchException
        self.data['field'] = field
        self.data['projects'] = projects
        
class CreateProjectView(TempitaHandler):
    """view to create a new project"""

    template = 'new.html'
    methods = set(['GET', 'POST'])
    handler_path = ['new']

    def __init__(self, app, request):
        TempitaHandler.__init__(self, app, request)
        self.data['navigation'] = self.navigation()
        self.data['fields'] = ['name', 'description', 'url'] + list(self.app.model.fields())
        self.data['errors'] = {}
        for field in self.request.GET.getall('missing'):
            self.data['errors'].setdefault(field, []).append('Required')

    def Post(self):
        required = set(['name', 'description', 'url'])
        missing = set([i for i in required
                       if not self.request.POST.get(i, '').strip()])

        if missing:
            location = self.link(self.request.path_info) + self.query_string([('missing', i) for i in missing])
            return self.redirect(location)
        # TODO check for duplicate project name

        project = dict([(i, self.request.POST[i]) for i in required]) 
        for field in self.app.model.fields():
            value = self.request.POST.get(field, '').strip()
            if not value:
                continue
            project[field] = value.split()

        self.app.model.save(project)
        return self.redirect(project['name'])
