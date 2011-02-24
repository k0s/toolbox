"""
models for toolbox
"""

import os
from search import WhooshSearch
from time import time
from util import str2filename

try:
    import json
except ImportError:
    import simplejson as json

class ProjectsModel(object):
    """
    abstract base class for toolbox projects
    """
    reserved = set(['name', 'description', 'url', 'modified'])

    def __init__(self, directory):
        """
        - directory: directory of projects
        """
        self.directory = directory
        self.files = {}
        self.search = WhooshSearch()

    def load(self):
        """load JSON from the directory"""
        for i in os.listdir(self.directory):
            if not i.endswith('.json'):
                continue
            filename = os.path.join(self.directory, i)
            mtime = os.path.getmtime(filename)
            if mtime > self.files.get(i, -1):
                self.files[i] = mtime
                project = json.loads(file(filename).read())
                self.files[project['name']] = i
                project['modified'] = mtime
                self.update(project)

    def save(self, project):
        filename = self.files.get(project['name'])
        if not filename:
            filename = str2filename(project['name']) + '.json'
        filename = os.path.join(self.directory, filename)
        file(filename, 'w').write(json.dumps(project))
        # TODO: data integrity checking

    def update_fields(self, name, **fields):
        """
        update the fields of a particular project
        """
        project = self.project(name)
        for field, value in fields.items():
            raise NotImplementedError # TODO

    def update(self, project):
        """update a project"""
        raise NotImplementedError

    def get(self, **query):
        """
        get a list of projects matching a query
        the query should be key, value pairs to match;
        if the value is single, it should be a string;
        if the value is multiple, it should be a set which will be
        anded together
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

class MemoryCache(ProjectsModel):
    """
    sample implementation keeping everything in memory
    """

    def __init__(self, directory):
        ProjectsModel.__init__(self, directory)
        self.projects = {}
        self._fields = set()
        self.index = {}
        self.load()

    def update(self, project):
        self.projects[project['name']] = project
        fields = [i for i in project if i not in self.reserved]
        self._fields.update(fields)
        for field in fields:
            index = self.index.setdefault(field, {})
            values = project[field]
            if isinstance(values, basestring):
                values = [values]
            for value in values:
                index.setdefault(value, set()).update([project['name']])

    def get(self, **query):
        results = set(self.projects.keys())
        for key, value in query.items():
            results.intersection_update(self.index.get(key, {}).get(value, set()))
        return [self.projects[project] for project in results]

    def fields(self):
        return self._fields

    def project(self, name):
        return self.projects.get(name)

    def field_query(self, field):
        return self.index.get(field)
