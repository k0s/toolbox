"""
scrapes metadata from a python setup.py file
"""

import imp
import sys
import urllib2

# dictionary of 
data = {}

def mock_setup(**kwargs):
    """
    mock the distutils/setuptools setup function
    """
    import pdb; pdb.set_trace()

def setuppy2tool(url):
    """
    reads a file path or URL (TODO)
    returns a dict in the appropriate format
    """
    


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        print setuppy2tool(arg)
