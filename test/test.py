#!/usr/bin/env python

"""
doctest runner for toolbox
"""

import doctest
import json
import os
import shutil
import sys
from cgi import escape
from optparse import OptionParser
from paste.fixture import TestApp
from time import time
from toolbox.dispatcher import Dispatcher

# global
directory = os.path.dirname(os.path.abspath(__file__))


class ToolboxTestApp(TestApp):
    """WSGI app wrapper for testing JSON responses"""

    def __init__(self, **kw):
        dispatcher_args = dict(model_type='memory_cache', fields=('usage', 'author', 'type', 'language', 'dependencies'))
        dispatcher_args.update(kw)
        app = Dispatcher(**dispatcher_args)
        TestApp.__init__(self, app)

    def get(self, url='/', **kwargs):
        kwargs.setdefault('params', {})['format'] = 'json'
        response = TestApp.get(self, url, **kwargs)
        return json.loads(response.body)

    def new(self, **kwargs):
        kwargs['form-render-date'] = str(time())
        return self.post('/new', params=kwargs)

    def cleanup(self):
        pass


class FileCacheTestApp(ToolboxTestApp):
    """test the MemoryCache file-backed backend"""

    def __init__(self):
        self.json_dir = os.path.join(directory, 'test_json')
        shutil.rmtree(self.json_dir, ignore_errors=True)
        os.makedirs(self.json_dir)
        ToolboxTestApp.__init__(self, model_type='file_cache', directory=self.json_dir)

    def cleanup(self):
        shutil.rmtree(self.json_dir, ignore_errors=True)


class CouchTestApp(ToolboxTestApp):
    """test the MemoryCache file-backed backend"""

    def __init__(self):
        ToolboxTestApp.__init__(self, model_type='couch', dbname='test_json')
        for project in self.app.model.projects():
            self.app.model.delete(project)

    def cleanup(self):
        for project in self.app.model.projects():
            self.app.model.delete(project)


app_classes = {'memory_cache': ToolboxTestApp,
               'file_cache': FileCacheTestApp,
               'couch': CouchTestApp}


def run_tests(app_cls,
              raise_on_error=False,
              cleanup=True,
              report_first=False,
              output=sys.stdout):

    results = {}

    # gather tests
    tests =  [ test for test in os.listdir(directory)
               if test.endswith('.txt') ]
    output.write("Tests:\n%s\n" % '\n'.join(tests))

    for test in tests:

        # create an app
        app = app_cls()

        # doctest arguments
        extraglobs = {'here': directory, 'app': app, 'urlescape': escape}
        doctest_args = dict(extraglobs=extraglobs, raise_on_error=raise_on_error)
        if report_first:
            doctest_args['optionflags'] = doctest.REPORT_ONLY_FIRST_FAILURE

        # run the test
        try:
            results[test] = doctest.testfile(test, **doctest_args)
        except doctest.DocTestFailure, failure:
            raise
        except doctest.UnexpectedException, failure:
            raise failure.exc_info[0], failure.exc_info[1], failure.exc_info[2]
        finally:
            if cleanup:
                app.cleanup()

    return results


def main(args=sys.argv[1:]):

    # parse command line args
    parser = OptionParser()
    parser.add_option('--no-cleanup', dest='cleanup',
                      default=True, action='store_false',
                      help="cleanup following the tests")
    parser.add_option('--raise', dest='raise_on_error',
                      default=False, action='store_true',
                      help="raise on first error")
    parser.add_option('--report-first', dest='report_first',
                      default=False, action='store_true',
                      help="report the first error only (all tests will still run)")
    parser.add_option('--model', dest='model', default='file_cache',
                      help="model to use")
    options, args = parser.parse_args(args)

    # get arguments to run_tests
    kw = dict([(i, getattr(options, i)) for i in ('raise_on_error', 'cleanup', 'report_first')])
    if options.model is not None:
        try:
            kw['app_cls'] = app_classes[options.model]
        except KeyError:
            parser.error("Model '%s' unknown (choose from: %s)" % (options.model, app_classes.keys()))

    # run the tests
    results = run_tests(**kw)
    if sum([i.failed for i in results.values()]):
        sys.exit(1) # error


if __name__ == '__main__':
    main()
