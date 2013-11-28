"""
request handlers:
these are instantiated for every request, then called
"""

import cgi
import os
from datetime import datetime
from pkg_resources import resource_filename
from urllib import quote as _quote
from urlparse import urlparse
from util import strsplit
from util import JSONEncoder
from webob import Response, exc
from tempita import HTMLTemplate
from time import time

# this is necessary because WSGI stupidly follows the CGI convention wrt encoding slashes
# http://comments.gmane.org/gmane.comp.web.pylons.general/5922
encoded_slash = '%25%32%66'

def quote(s, safe='/'):
    if isinstance(s, unicode):
        s = s.encode('utf-8', 'ignore') # hope we're using utf-8!
    return _quote(s, safe).replace('/', encoded_slash)

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
        self.check_json() # is this a JSON request?

    def __call__(self):
        return getattr(self, self.request.method.title())()

    def link(self, path=None):
        """
        link relative to the site root
        """
        path_info = self.request.path_info
        segments = path_info.split('/')
        if segments[0]:
            segments.insert(0, '')

        if len(segments) <3:
            if not path or path == '/':
                return './'
            return path

        nlayers = len(segments[2:])
        string = '../' * nlayers

        if not path or path == '/':
            return string
        return string + path

    def redirect(self, location, query=None, anchor=None):
        return exc.HTTPSeeOther(location=self.app.baseurl + '/' + location
                                + (query and self.query_string(query) or '')
                                + (anchor and ('#' + anchor) or ''))

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
            retval = self.request.POST.mixed()
            for key in retval:
                value = retval[key]
                if isinstance(value, basestring):
                    retval[key] = value.strip()
                else:
                    # TODO[?]: just throw away all empty values here
                    retval[key] = [i.strip() for i in value]
            return retval

    def get_json(self):
        """JSON to serialize if requested for GET"""
        raise NotImplementedError # abstract base class


class TempitaHandler(Handler):
    """handler for tempita templates"""

    template_dirs = [ resource_filename(__name__, 'templates') ]

    template_cache = {}

    css = ['css/html5boilerplate.css']

    less = ['css/style.less']

    js = ['js/jquery-1.6.min.js',
          'js/less-1.0.41.min.js',
          'js/jquery.timeago.js',
          'js/main.js']
    
    def __init__(self, app, request):
        Handler.__init__(self, app, request)

        # add application template_dir if specified
        if app.template_dir:
            self.template_dirs = self.template_dirs[:] + [app.template_dir]
            
        self.data = { 'request': request,
                      'css': self.css,
                      'item_name': self.app.item_name,
                      'item_plural': self.app.item_plural,
                      'less': self.less,
                      'js':  self.js,
                      'site_name': app.site_name,
                      'title': self.__class__.__name__,
                      'hasAbout': bool(app.about),
                      'urlescape': quote,
                      'link': self.link}

    def find_template(self, name):
        """find a template of a given name"""
        # the application caches a dict of the templates if app.reload is False
        if name in self.template_cache:
            return self.template_cache[name]
        
        for d in self.template_dirs:
            path = os.path.join(d, name)
            if os.path.exists(path):
                template = HTMLTemplate.from_filename(path)
                if not self.app.reload:
                    self.template_cache[name] = template
                return template

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
    """abstract base class for views of projects"""

    js = TempitaHandler.js[:]
    js.extend(['js/jquery.tokeninput.js',
               'js/jquery.jeditable.js',
               'js/jquery.autolink.js',
               'js/project.js'])
               
    less = TempitaHandler.less[:]
    less.extend(['css/project.less'])

    css = TempitaHandler.css[:]
    css.extend(['css/token-input.css',
                'css/token-input-facebook.css'])

    def __init__(self, app, request):
        """project views specific init"""
        TempitaHandler.__init__(self, app, request)
        self.data['fields'] = self.app.model.fields()
        self.data['error'] = None
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
        format_string = '%Y-%m-%dT%H:%M:%SZ'
        return datetime.utcfromtimestamp(timestamp).strftime(format_string)


class QueryView(ProjectsView):
    """general index view to query projects"""
    
    template = 'index.html'
    methods = set(['GET'])

    def __init__(self, app, request):
        ProjectsView.__init__(self, app, request)

        # pop non-query parameters;
        # sort is popped first so that it does go in the query
        sort_type = self.request.GET.pop('sort', None)
        query = self.request.GET.mixed()
        self.data['query'] = query
        search = query.pop('q', None)
        self.data['search'] = search

        # query for tools
        self.data['projects']= self.app.model.get(search, **query)

        # order the results
        self.data['sort_types'] = [('name', 'name'), ('-modified', 'last updated')]
        if search:
            self.data['sort_types'].insert(0, ('search', 'search rank'))
        if sort_type is None:
            if search:
                sort_type = 'search'
            else:
                # default
                sort_type = '-modified'
        self.data['sort_type'] = sort_type
        if sort_type != 'search':
            # preserve search order results 
            self.sort(sort_type)
            
        self.data['fields'] = self.app.model.fields()
        self.data['title'] = self.app.site_name


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
        if not len(request.environ['path']) == 1:
            return None

        # get the project if it exists
        projectname = request.environ['path'][0].replace('%2f', '/')  # double de-escape slashes, see top of file
        try:
            # if its utf-8, we should try to keep it utf-8
            projectname = projectname.decode('utf-8')
        except UnicodeDecodeError:
            pass
        project = app.model.project(projectname)
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

        # data
        post_data = self.post_data()
        project = self.data['projects'][0]

        # insist that you have a name
        if 'name' in post_data and not post_data['name'].strip():
            self.data['title'] = 'Rename error'
            self.data['error'] = 'Cannot give a project an empty name'
            self.data['content'] = self.render(self.template, **self.data)
            return Response(content_type='text/html',
                            status=403,
                            body=self.render('main.html', **self.data))

        # don't allow overiding other projects with your fancy rename
        if 'name' in post_data and post_data['name'] != project['name']:
            if self.app.model.project(post_data['name']):
                self.data['title'] = '%s -> %s: Rename error' % (project['name'], post_data['name'])
                self.data['error'] = 'Cannot rename over existing project: <a href="%s">%s</a>' % (post_data['name'], post_data['name'] )
                self.data['content'] = self.render(self.template, **self.data)
                return Response(content_type='text/html',
                                status=403,
                                body=self.render('main.html', **self.data))

        # XXX for compatability with jeditable:
        id = post_data.pop('id', None)

        action = post_data.pop('action', None)
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
                        value = strsplit(value)
                    if action == 'replace':
                        # replace the field from the POST request
                        project[field] = value
                    else:
                        # append the items....the default action
                        project.setdefault(field, []).extend(value)

        # rename handling
        if 'name' in post_data and post_data['name'] != old_name:
            self.app.model.delete(old_name)
            self.app.model.update(project)
            return self.redirect(quote(project['name']))

        self.app.model.update(project)

        # XXX for compatability with jeditable:
        if id is not None:
            return Response(content_type='text/plain',
                            body=cgi.escape(project['description']))

        # XXX should redirect instead
        return self.Get()


class FieldView(ProjectsView):
    """view of projects sorted by a field"""

    template = 'fields.html'
    methods=set(['GET', 'POST'])
    js = TempitaHandler.js[:] + ['js/field.js']

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
            projects = {}
        self.data['field'] = field
        self.data['values'] = projects
        self.data['title'] = app.item_plural + ' by %s' % field
        if self.request.method == 'GET':
            # get project descriptions for tooltips
            descriptions = {}
            project_set = set()
            for values in projects.values():
                project_set.update(values)
            self.data['projects'] = dict([(name, self.app.model.project(name))
                                          for name in project_set])

    def Post(self):
        field = self.data['field']
        for key in self.request.POST.iterkeys():
            value = self.request.POST[key]
            self.app.model.rename_field_value(field, key, value)
        
        return self.redirect(field, anchor=value)
        
    def get_json(self):
        return self.data['values']

        
class CreateProjectView(TempitaHandler):
    """view to create a new project"""

    template = 'new.html'
    methods = set(['GET', 'POST'])
    handler_path = ['new']
    js = TempitaHandler.js[:]
    js.extend(['js/jquery.tokeninput.js',
               'js/queryString.js',
               'js/new.js'])
               
    less = TempitaHandler.less[:]
    less.extend(['css/new.less'])
    
    css = TempitaHandler.css[:]
    css.extend(['css/token-input.css',
                'css/token-input-facebook.css'])

    def __init__(self, app, request):
        TempitaHandler.__init__(self, app, request)
        self.data['title'] = 'Add a ' + app.item_name
        self.data['fields'] = self.app.model.fields()

    def check_name(self, name):
        """
        checks a project name for validity
        returns None on success or an error message if invalid
        """
        reserved = self.app.reserved.copy()
        if name in reserved or name in self.app.model.fields(): # check application-level reserved URLS
            return 'reserved'
        if self.app.model.project(name): # check projects for conflict
            return 'conflict'

    def Post(self):

        # get some data
        required = self.app.model.required
        post_data = self.post_data()

        # ensure the form isn't over 24 hours old
        day = 24*3600
        form_date = post_data.pop('form-render-date', -day)
        try:
            form_date = float(form_date)
        except ValueError:
            form_date = -day
        if abs(form_date - time()) > day:
            # if more than a day old, don't honor the request
            return Response(content_type='text/plain',
                            status=400,
                            body="Your form is over a day old or you don't have Javascript enabled")

        # build up a project dict
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
            errors[name_conflict] = [project['name']]
        if errors:
            error_list = []
            for key in errors:
                # flatten the error dict into a list
                error_list.extend([(key, i) for i in errors[key]])
            return self.redirect(self.request.path_info.strip('/'), error_list)

        # add fields to the project
        for field in self.app.model.fields():
            value = post_data.get(field, '').strip()
            values = strsplit(value)
            if not value:
                continue
            project[field] = values or value

        self.app.model.update(project)
        return self.redirect(quote(project['name']))


class DeleteProjectHandler(Handler):

    methods = set(['POST'])
    handler_path = ['delete']

    def Post(self):        
        post_data = self.post_data()
        project = post_data.get('project')
        if project:
            try:
                self.app.model.delete(project)
            except:
                pass # XXX better than internal server error

        # redirect to query view
        return self.redirect('')


class TagsView(TempitaHandler):
    """view most popular tags"""
    methods = set(['GET'])
    handler_path = ['tags']
    template = 'tags.html'

    def __init__(self, app, request):
        TempitaHandler.__init__(self, app, request)
        self.data['fields'] = self.app.model.fields()
        fields = self.request.GET.getall('field') or self.data['fields']
        query = self.request.GET.get('q', '')
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
            # possibly at the model level
            for field in fields:
                for value in project.get(field, []):
                    if value in ommitted[field] or query not in value:
                        continue
                    count = field_tags[field].get(value, 0) + 1
                    field_tags[field][value] = count
        tags = []
        for field in field_tags:
            for value, count in field_tags[field].items():
                tags.append({'field': field, 'value': value, 'count': count, 'id': value, 'name': value})
        tags.sort(key=lambda x: x['count'], reverse=True)

        self.data['tags'] = tags

    def get_json(self):
        return self.data['tags']


class AboutView(TempitaHandler):
    """the obligatory about page"""
    methods = set(['GET'])
    handler_path = ['about']
    template = 'about.html'
    less = TempitaHandler.less[:] + ['css/about.less']
    def __init__(self, app, request):
        TempitaHandler.__init__(self, app, request)
        self.data['fields'] = self.app.model.fields()
        self.data['title'] = 'about:' + self.app.site_name
        self.data['about'] = self.app.about

class NotFound(TempitaHandler):
    def __init__(self, app, request):
        TempitaHandler.__init__(self, app, request)
        self.data['fields'] = self.app.model.fields()

    def __call__(self):
        self.data['content'] = '<h1 id="title">Not Found</h1>'
        return Response(content_type='text/html',
                        status=404,
                        body=self.render('main.html', **self.data))
