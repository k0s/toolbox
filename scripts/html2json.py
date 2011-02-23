#!/usr/bin/env python

"""
script to convert HTML microformat files to JSON:

<div class="project">
<h1><a href="${URL}">${PROJECT}</a></h1>
<p class="description">${DESCRIPTION}</p>

<!-- fields (lists) -->
<ul class="author"><li>${AUTHOR}</li></ul>
<ul class="usage"><li>${USAGE}</li></ul>
</div>
"""

### imports

import os

try:
    from lxml import etree
except ImportError:
    raise ImportError("""You need lxml to run this script. Try running
    `easy_install lxml`
    It will work if you're lucky""")

try:
    import json
except ImportError:
    import simplejson as json

### parse command line

from optparse import OptionParser

usage = '%prog file'
parser = OptionParser(usage=usage, description=__doc__)
parser.add_option('--pprint', dest='pprint',
                  action='store_true', default=False,
                  help="pretty-print the json")
                  
options, args = parser.parse_args()

if not len(args) == 1:
    parser.print_help()
    parser.exit()
filename = args[0]
assert os.path.exists(filename), "%s not found" % filename

### parse teh file
document = etree.parse(filename)
elements = document.findall(".//div[@class='project']")
if not elements:
    root = document.getroot()
    if root.tag == 'div' and 'project' in root.attrib.get('class', '').split():
        elements = [root]
if not elements:
    parser.error('No <div class="project"> found')

# print teh projects
for element in elements:
    project = {}
    header = element.find('.//h1')
    link = header.find('a')
    if link is not None:
        project['name'] = link.text
        project['url'] = link.attrib['href']
    else:
        project['name'] = header.text
    project['name'] = ' '.join(project['name'].strip().split())
    description = element.find("p[@class='description']")
    if description is not None:
        project['description'] = description.text or ''
        project['description'] = ' '.join(project['description'].strip().split())
    for field in ('author', 'usage', 'language', 'type'):
        e = element.find("ul[@class='%s']" % field)
        if e is not None:
            values = e.findall('li')
            for value in values:
                project.setdefault(field, []).append(value.text)
    indent = options.pprint and 2 or None
    print json.dumps(project, indent=indent)
