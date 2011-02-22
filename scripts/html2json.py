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

try:
    from lxml import etree
except ImportError:
    raise ImportError("""You need lxml to run this script. Try running
    `easy_install lxml`
    It will work if you're lucky""")

from optparse import OptionParser

usage = '%prog file'
parser = OptionParser(usage=usage)
