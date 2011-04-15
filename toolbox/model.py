"""
models for toolbox
"""

import couchdb
import os
from search import WhooshSearch
from time import time
from util import str2filename

try:
    import json
except ImportError:
    import simplejson as json

# TODO: types of fields:
# - string: a single string: {'type': 'string', 'name': 'name', 'required': True}
# - field: a list of strings: {'type': 'field', 'name', 'usage'}
# - dict: a subclassifier: {'type': '???', 'name': 'url', 'required': True}

class ProjectsModel(object):
    """
    abstract base class for toolbox tools
    """

    def __init__(self, required=('name', 'description', 'url')):
        """
        - required : required data (strings)
        """
        self.required = set(required)

        # reserved fields        
        self.reserved = self.required.copy()
        self.reserved.update(['modified']) 
        self.modified = {}
        self.search = WhooshSearch()

    def update_fields(self, name, **fields):
        """
        update the fields of a particular project
        """
        project = self.project(name)
        for field in required:
            value = fields.pop(field)
            if value is not None:
                project[field] = value
        for field, value in fields.items():
            project[field] = value
        self.update(project)

    def update_search(self, project):
        """update the search index"""
        assert self.required.issubset(project.keys()) # XXX should go elsewhere
        fields = dict([(field, project[field])
                       for field in self.fields()
                       if field in project])

        # keys must be strings, not unicode, on some systems
        f = dict([(str(i), j) for i, j in fields.items()])

        self.search.update(name=project['name'], description=project['description'], **f)

    def update(self, project):
        """update a project"""
        raise NotImplementedError

    def get(self, **query):
        """
        get a list of projects matching a query
        the query should be key, value pairs to match;
        if the value is single, it should be a string;
        if the value is multiple, it should be a set which will be
        ANDed together
        """
        raise NotImplementedError

    def fields(self):
        """what fields does the model support?"""
        raise NotImplementedError

    def project(self, name):
        """get a project of a particular name, or None if there is none"""
        raise NotImplementedError

    def field_query(self, field):
        """get projects according to a particular field, or None"""
        raise NotImplementedError

    def delete(self, project):
        raise NotImplementedError


class MemoryCache(ProjectsModel):
    """
    sample implementation keeping everything in memory with backing files
    """

    def __init__(self, directory, fields=None):
        """
        - directory: directory of .json tool files
        - fields : list of fields to use, or None to calculate dynamically
        """
        ProjectsModel.__init__(self)

        # JSON blob directory
        if not os.path.exists(directory):
            os.makedirs(directory)
        assert os.path.isdir(directory)
        self.directory = directory
        
        self.files = {}
        self._projects = {}
        self._fields = fields
        self.field_set = set(fields or ())
        self.index = {}
        self.load()

    def update(self, project):
        self._projects[project['name']] = project
        if self._fields is None:
            fields = [i for i in project if i not in self.reserved]
            self.field_set.update(fields)
        else:
            fields = self._fields
        for field in fields:
            for _set in self.index.get(field, {}).values():
                _set.discard(project['name'])
            if field not in project:
                continue
            index = self.index.setdefault(field, {})
            values = project[field]
            if isinstance(values, basestring):
                values = [values]
            for value in values:
                index.setdefault(value, set()).update([project['name']])
        self.update_search(project)


    def get(self, search=None, **query):
        """
        - search: text search
        """
        order = None
        if search:
            results = self.search(search)
            order = dict([(j,i) for i,j in enumerate(results)])
        else:
            results = self._projects.keys()
        results = set(results)
        for key, value in query.items():
            results.intersection_update(self.index.get(key, {}).get(value, set()))
        if order:
            # preserve search order
            results = sorted(list(results), key=lambda x: order[x])
        return [self._projects[project] for project in results]

    def fields(self):
        return list(self.field_set)

    def project(self, name):
        return self._projects.get(name)

    def field_query(self, field):
        return self.index.get(field)

    def delete(self, project):
        """
        delete a project
        - project : name of the project
        """
        if project not in self._projects:
            return
        del self._projects[project]
        for key, value in self.index.items():
            if project in value:
                if len(value) == 1:
                    self._fields.pop(key)
                value.pop(project)
        self.search.delete(project)
        os.remove(os.path.join(self.directory, self.files.pop(project)))

    def load(self):
        """load JSON from the directory"""
        for i in os.listdir(self.directory):
            if not i.endswith('.json'):
                continue
            filename = os.path.join(self.directory, i)
            mtime = os.path.getmtime(filename)
            if mtime > self.modified.get(i, -1):
                self.modified[i] = mtime
                try:
                    project = json.loads(file(filename).read())
                except:
                    print 'File: ' + i
                    raise
                self.files[project['name']] = i
                if 'modified' not in project:
                    project['modified'] = mtime
                    self.save(project)
                self.update(project)

    def save(self, project):
        filename = self.files.get(project['name'])
        if not filename:
            filename = str2filename(project['name']) + '.json'
        filename = os.path.join(self.directory, filename)
        file(filename, 'w').write(json.dumps(project))


class CouchCache(MemoryCache):
    """
    store json files in couchdb
    """

    def __init__(self,
                 server="http://127.0.0.1:5984",
                 dbname="toolbox"):
        server = couchdb.Server(server)
        try:
            self.db = server[dbname]
        except:
            self.db = server.create(dbname)

        # XXX *should* inherit from ABC!
        MemoryCache.__init__(self)


    def load(self):
        """load JSON objects from CouchDB docs"""
        for id in self.db:
            doc = self.db[id]
            project = doc['project']
            self.update(project)
            
    def save(self, project):
        name = project['name']
        try:
             updated = self.db[name]
        except:
             updated = {}
        updated['project'] = project
        updated['project']['modified'] = time()
        self.db[name] = updated
