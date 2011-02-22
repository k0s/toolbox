"""
models for toolbox
"""

try:
    import json
except ImportError:
    import simplejson as json

class ProjectsModel(object):
    """
    abstract base class for toolbox projects
    """
    reserved = set(['name', 'description'])

    def __init__(self, directory):
        """
        - directory: directory of projects
        """
        self.directory = directory

    def load(self):
        raise NotImplementedError

    def get(self, **query):
        raise NotImplementedError

    def fields(self):
        """what fields does the model support?"""
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

    def load(self):
        for i in os.listdir(self.directory):
            if not i.endswith('.json'):
                continue
            project = json.loads(file(os.path.join(self.directory, i))).read()
            self.projects[project['name']] = project
            fields = [i for i in project if i not in self.reserved]
            self.fields.update(fields)
            for field in fields:
                self.index.setdefault(field, {}).setdefault(project[field], set()).update([project['name']])

    def update(self, project):
        pass

    def get(self, **query):
        results = set(self.projects.keys())
        for key, value in query.items():
            results.intersection_update(self.index.get(key, {}).get(value, set())

    def fields(self):
        return self._fields
