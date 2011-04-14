#!/usr/bin/env python

"""
doctest runner
"""

import doctest
import os
import shutil
from paste.fixture import TestApp
from toolbox.dispatcher import Dispatcher

try:
    import json
except ImportError:
    import simplejson as json

# globals
directory = os.path.dirname(os.path.abspath(__file__))
json_dir = os.path.join(directory, 'test_json')

class ToolboxTestApp(TestApp):
    def __init__(self):
        app = Dispatcher(fields=('usage', 'author', 'type', 'language', 'dependencies'), directory=json_dir)
        TestApp.__init__(self, app)

    def get(self, url='/', **kwargs):
        kwargs.setdefault('params', {})['format'] = 'json'
        response = TestApp.get(self, url, **kwargs)
        return json.loads(response.body)

def run_tests():
    tests =  [ test for test in os.listdir(directory)
               if test.endswith('.txt') ]
    for test in tests:
        shutil.rmtree(json_dir, ignore_errors=True)
        os.makedirs(json_dir)
        app = ToolboxTestApp()
        extraglobs = {'here': directory, 'app': app, 'json_dir': json_dir}
        try:
            doctest.testfile(test, extraglobs=extraglobs, raise_on_error=False)
        except:
            shutil.rmtree(json_dir, ignore_errors=True)
            raise

if __name__ == '__main__':
    run_tests()

