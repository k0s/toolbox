toolbox
=======

a place to find Mozilla software tools

The Story of Toolbox
--------------------

A tool is only useful if you know it exists and can find it. Toolbox
is an index of tools developed by the mozilla community.  Toolbox is
not a hosting service -- it is just a listing of packages which can
live anywhere that are of use to Mozillians.

It could also be used to track:
* smart bookmarks
* code snippets


How to use Toolbox
------------------

The `index page </>`_ of toolbox lists all tools with the most
recently updated first.  A tool has a name, a description, a URL, and a
number of fields.  Most everything is clickable.  Clicking on the
description lets you edit the description which will be saved on
blur. Clicking a URL, like `?author=harth </?author=harth>`_ will give
you the tools that ``harth`` wrote. There is also full text search
using the ``?q=`` parameter (like `?q=firefox </?q=firefox>`_ ) which
will search both the descriptions and all of the fields.

You can also display results by a particular field by going to that
field name.  For example, to display tools by author, go to 
`/author </author>`_ .  You can create a new tool at 
`/new </new>`_ .


Running 
-------

To serve in baseline mode, install the software and run::

 paster serve paste.ini

This will serve the handlers and static content using the paste
(http://pythonpaste.org) webserver.

The dispatcher (``toolbox.dispatcher:Dispatcher``) is the central
webapp that designates per-request to a number of handlers (from
``handlers.py``).  The dispatcher has a few options::

* template_dirs: extra directories (in order) to look for templates
* model_type: type of backend to use

These may be configured in the ``paste.ini`` file in the
``[app:toolbox]`` section by prepending with the namespace
``toolbox.``. It is advisable that you copy the example ``paste.ini``
file for your own usage needs.


TODO
----

The list:

* add this file to /about
* make fields configurable if specified
* cleanup model; ensure couch works
* add (e.g.) selenium tests
* add import functionality to couch backend and make sure it works
* keep track of which URLs projects cant use
* make /new more AJAXy
* setup.py scraper
* AMO scraper
* mozdev scraper
* allow projects to point to a setup.py or AMO URL
* URLs in the description should be made links
* dependencies should link appropriately (e.g. to toolbox if possible)
* calendar view for projects
* make the /tags view useful
* the first time someone edits a description (etc.) from a pointed-to
  file (e.g. a setup.py) then the project should be notified


Links
-----

Types of links should be recorded:

* repository
* how to report bugs
* wiki
* pypi


More types of links should be allowed:
The current behaviour is that each project has a single link that is
linked to from its header.  While this is expedient behaviour, there
are a couple of deficiencies in this:

- if a project has multiple links, there is no way of adding them
- there is no permalink to the project itself

So there are a few things worth considering:

- the header link could be converted to the permalink to the canonical
  toolbox URL

- links could be scraped from the description

- you could have a way of entering links of various types


Other Resources
---------------

* http://www.mozdev.org/
* https://wiki.mozilla.org/User:Jprosevear/Tools
