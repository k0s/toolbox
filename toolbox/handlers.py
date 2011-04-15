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
        self.check_json() # is this a JSON request?

    def __call__(self):
        return getattr(self, self.request.method.title())()

    def link(self, path=(), permanant=False):
        """create a link"""
        if isinstance(path, basestring):
            path = [ path ]
        path = [ i.strip('/') for i in path ]
        if permanant:
            application_url = self.request.application_url
        else:
            application_url = self.application_path
        path = [ application_url ] + path
        if path == ['']:
            return '/'
        return '/'.join(path)

    def redirect(self, location):
        return exc.HTTPSeeOther(location=location)

    def query_string(self, query):
        """
        generate a query string; query is a list of 2-tuples
        """
        return '?' + '&'.join(['%s=%s' % (i,j)
                               for i, j in query])

    # methods for JSON

    def check_json(self):
        """check to see if the request is for JSON"""
        self.json = self.request.GET.pop('format', '') == 'json'

    def post_data(self):
        """python dict from POST request"""
        if self.json:
            return json.loads(self.request.body)
        else:
            return self.request.POST.mixed()

    def get_json(self):
        """JSON to serialize if requested for GET"""
        raise NotImplementedError # abstract base class


class TempitaHandler(Handler):
    """handler for tempita templates"""

    template_dirs = [ resource_filename(__name__, 'templates') ]
    css = ['/css/style.css']
    js = ['/js/jquery.js', '/js/main.js']
    
    def __init__(self, app, request):
        Handler.__init__(self, app, request)

        # add application template_dir if specified
        if app.template_dir:
            template_dirs.insert(0, app_template_dir)

        self.data = { 'request': request,
                      'link': self.link,
                      'css': self.css,
                      'js':  self.js,
                      'title': self.__class__.__name__,
                      'hasAbout': bool(app.about)}

    def find_template(self, template):
        """find a template of a given name"""
        # TODO: make this faster; the application should probably cache
        # a dict of the (loaded) templates unless (e.g.) debug is given
        
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
        if self.json:
            return Response(content_type='application/json',
                            body=json.dumps(self.get_json(), cls=JSONEncoder))
        self.data['content'] = self.render(self.template, **self.data)
        return Response(content_type='text/html',
                        body=self.render('main.html', **self.data))

class ProjectsView(TempitaHandler):
    """abstract base class for view with projects"""

    js = TempitaHandler.js[:]
    js.extend(['/js/jquery.autoSuggest.js',
               '/js/jquery.jeditable.js',
               '/js/project.js'])

    def __init__(self, app, request):
        """project views specific init"""
        TempitaHandler.__init__(self, app, request)
        self.data['fields'] = self.app.model.fields()
        if not self.json:
            self.data['format_date'] = self.format_date

    def get_json(self):
        """JSON to serialize if requested"""
        return self.data['projects']

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
        format_string = '%B %-d, %Y - %H:%M'
        return datetime.fromtimestamp(timestamp).strftime(format_string)


class QueryView(ProjectsView):
    """general index view to query projects"""
    
    template = 'index.html'
    methods = set(['GET'])

    def __init__(self, app, request):
        ProjectsView.__init__(self, app, request)
        sort_type = self.request.GET.pop('sort', '-modified')
        query = self.request.GET.mixed()
        search = query.pop('q', None)
        self.data['projects']= self.app.model.get(search, **query)
        self.sort(sort_type)
        self.data['fields'] = self.app.model.fields()
        self.data['title'] = 'Toolbox'


class ProjectView(ProjectsView):
    """view of a particular project"""

    template = 'index.html'
    methods=set(['GET', 'POST'])

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

    def get_json(self):
        return self.data['projects'][0]

    def Post(self):

        post_data = self.post_data()

        # XXX for compatability with jetitable:
        id = post_data.pop('id', None)

        action = post_data.pop('action', None)
        project = self.data['projects'][0]
        old_name = project['name']
        if action == 'delete':
            for field in self.app.model.fields():
                if field in post_data and field in project:
                    values = post_data.pop(field)
                    if isinstance(values, basestring):
                        values = [values]
                    for value in values:
                        project[field].remove(value)
                    if not project[field]:
                        project.pop(field)
        else:
            for field in self.app.model.required:
                if field in post_data:
                    project[field] = post_data[field]
            for field in self.app.model.fields():
                if field in post_data:
                    value = post_data[field]
                    if isinstance(value, basestring):
                        value = [value]
                    if 'action' == 'replace':
                        # replace the field from the POST request
                        project[field] = value
                    else:
                        # append the items....the default action
                        project.setdefault(field, []).extend(value)

        if 'name' in post_data and post_data['name'] != old_name:
            self.app.model.delete(old_name)

        self.app.model.save(project)

        # XXX for compatability with jetitable:
        if id is not None:
            return Response(content_type='text/plain',
                            body=project['description'])

        return self.Get()

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
        self.data['title'] = 'Tools by %s' % field

        
class CreateProjectView(TempitaHandler):
    """view to create a new project"""

    template = 'new.html'
    methods = set(['GET', 'POST'])
    handler_path = ['new']
    js = TempitaHandler.js[:]
    js.extend(['/js/jquery.autoSuggest.js',
               '/js/new.js'])
    css = TempitaHandler.css[:]
    css.append('/css/new.css')

    def __init__(self, app, request):
        TempitaHandler.__init__(self, app, request)
        self.data['title'] = 'Add a tool'
        self.data['fields'] = self.app.model.fields()

        # deal with errors, currently badly contracted in query string
        self.data['errors'] = {}
        for field in self.request.GET.getall('missing'):
            self.data['errors'].setdefault(field, []).append('Required')
        if 'conflict' in self.request.GET:
            self.data['errors'].setdefault('name', []).append(self.check_name(self.request.GET['conflict']))

    def check_name(self, name):
        """
        checks a project name for validity
        returns None on success or an error message if invalid
        """
        reserved = self.app.reserved.copy()
        reserved_msg = "'%s' conflicts with a reserved URL" % name
        if name in reserved: # check application-level reserved URLS
            return reserved_msg
        if name in self.app.model.fields(): # check field URLs (XXX incestuous)
            return reserved_msg

        if self.app.model.project(name): # check projects for conflict
            return '<a href="%s">%s</a> already exists' % (self.link(name), name)

    def Post(self):

        # get some data
        required = self.app.model.required
        post_data = self.post_data()
        project = dict([(i, post_data.get(i, '').strip())
                        for i in required])

        # check for errors
        errors = {}
        missing = set([i for i in required if not project[i]])
        if missing: # missing required fields
            errors['missing'] = missing
        # TODO check for duplicate project name
        # and other url namespace collisions
        name_conflict = self.check_name(project['name'])
        if name_conflict:
            errors['conflict'] = [project['name']]
        if errors:
            error_list = [] 
            for key in errors:
                # flatten the error dict into a list
                error_list.extend([(key, i) for i in errors[key]])
            location = self.link(self.request.path_info) + self.query_string(error_list)
            return self.redirect(location)

        # add fields to the project
        # currently used only for JSON requests
        for field in self.app.model.fields():
            value = post_data.get(field, '').strip()
            values = [i.strip() for i in value.split(',') if i.strip()]
            if not value:
                continue
            project[field] = value

        self.app.model.save(project)
        return self.redirect(project['name'])


class DeleteProjectHandler(Handler):

    methods = set(['POST'])
    handler_path = ['delete']

    def Post(self):
        post_data = self.post_data()
        project = post_data.get('project')
        if project:
            self.app.model.delete(project)

        # redirect to query view
        return self.redirect(location=self.link())


class TagsView(TempitaHandler):
    """view most popular tags"""
    methods = set(['GET'])
    handler_path = ['tags']
    template = 'tags.html'

    def __init__(self, app, request):
        TempitaHandler.__init__(self, app, request)
        self.data['fields'] = self.app.model.fields()
        fields = self.request.GET.getall('field') or self.data['fields']
        self.data['title'] = 'Tags'
        field_tags = dict((i, {}) for i in fields)
        omit = self.request.GET.getall('omit')
        ommitted = dict([(field, set()) for field in fields])
        for name in omit:
            project = self.app.model.project(name)
            if not project:
                continue
            for field in fields:
                ommitted[field].update(project.get(field, []))
            
        for project in self.app.model.get():
            if project in omit:
                continue
            # TODO: cache this for speed somehow
            for field in fields:
                for value in project.get(field, []):
                    if value in ommitted[field]:
                        continue
                    count = field_tags[field].get(value, 0) + 1
                    field_tags[field][value] = count
        tags = []
        for field in field_tags:
            for value, count in field_tags[field].items():
                tags.append({'field': field, 'value': value, 'count': count})
        tags.sort(key=lambda x: x['count'], reverse=True)            
        self.data['tags'] = tags

    def get_json(self):
        return self.data['tags']


class AboutView(TempitaHandler):
    """the obligatory about page"""
    methods = set(['GET'])
    handler_path = ['about']
    template = 'about.html'

    def __init__(self, app, request):
        TempitaHandler.__init__(self, app, request)
        self.data['fields'] = self.app.model.fields()
        self.data['title'] = 'about:toolbox'
        self.data['about'] = self.app.about
