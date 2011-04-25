#!/usr/bin/env python

"""
doctest runner for toolbox
"""

import doctest
import os
import shutil
import sys
from optparse import OptionParser
from paste.fixture import TestApp
from toolbox.dispatcher import Dispatcher

try:
    import json
except ImportError:
    import simplejson as json

# globals
directory = os.path.dirname(os.path.abspath(__file__))

class ToolboxTestApp(TestApp):
    """WSGI app wrapper for testing JSON responses"""
    
    def __init__(self, **kw):
        dispatcher_args = dict(fields=('usage', 'author', 'type', 'language', 'dependencies'))
        dispatcher_args.update(kw)
        app = Dispatcher(**dispatcher_args)
        TestApp.__init__(self, app)

    def get(self, url='/', **kwargs):
        kwargs.setdefault('params', {})['format'] = 'json'
        response = TestApp.get(self, url, **kwargs)
        return json.loads(response.body)

    def cleanup(self):
        pass

class MemoryCacheTestApp(ToolboxTestApp):
    """test the MemoryCache file-backed backend"""

    def __init__(self):
        self.json_dir = os.path.join(directory, 'test_json')
        shutil.rmtree(self.json_dir, ignore_errors=True)
        os.makedirs(self.json_dir)
        ToolboxTestApp.__init__(self, directory=self.json_dir)

    def cleanup(self):
        shutil.rmtree(self.json_dir, ignore_errors=True)

def run_tests(raise_on_error=False, cleanup=True, report_first=False):

    results = {}

    # gather tests
    tests =  [ test for test in os.listdir(directory)
               if test.endswith('.txt') ]
        
    for test in tests:

        # create an app
        app = MemoryCacheTestApp()

        # doctest arguments
        extraglobs = {'here': directory, 'app': app}
        doctest_args = dict(extraglobs=extraglobs, raise_on_error=raise_on_error)
        if report_first:
            doctest_args['optionflags'] = doctest.REPORT_ONLY_FIRST_FAILURE

        # run the test
        try:
            results[test] = doctest.testfile(test, **doctest_args)
                                             
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
    options, args = parser.parse_args(args)

    # run the tests
    results = run_tests(raise_on_error=options.raise_on_error, cleanup=options.cleanup, report_first=options.report_first)
    if sum([i.failed for i in results.values()]):
        sys.exit(1) # error

if __name__ == '__main__':
    main()

