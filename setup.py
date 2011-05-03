from setuptools import setup, find_packages

try:
    description = file('README.txt').read()
except IOError: 
    description = ''

version = "0.1"

# dependencies
dependencies = [
    'WebOb',
    'tempita',
    'paste',
    'pastescript', # technically optional, but here for ease of install
    'whoosh',
    'couchdb',
    'docutils',
    'relocator'
    ]
try:
    import json
except ImportError:
    dependencies.append('simplejson')

setup(name='toolbox',
      version=version,
      description="a place to list Mozilla software tools",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='jhammel@mozilla.com',
      url='',
      license="MPL",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=dependencies,
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      convert-toolbox-model = toolbox.model:convert
      
      [paste.app_factory]
      toolbox = toolbox.factory:paste_factory
      """,
      )
      
