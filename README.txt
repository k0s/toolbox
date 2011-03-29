toolbox
-------

a place to find Mozilla software tools

The Story of Toolbox
--------------------

A tool is only useful if you know it exists and can find it.

Other useful things:
* smart bookmarks
* code snippets

Running
-------

To serve in baseline mode, run in this directory::

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

* add dynamic field addition with jqueryui autocomplete
* cleanup model
* add (e.g.) selenium tests
* add import functionality to couch backend and make sure it works
* check to see if in-situ editing isn't overridden by submit
* keep track of which URLs projects cant use
* setup.py scraper
* AMO scraper
* allow projects to point to a setup.py or AMO URL
* URLs in the description should be made links
* dependencies should link appropriately (e.g. to toolbox if possible)
* calendar view for projects
* the first time someone edits a description (etc.) from a pointed-to
  file (e.g. a setup.py) then the project should be notified


Thought Farm
------------

Links:

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
