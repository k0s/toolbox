toolbox
=======

*an index of Mozilla software tools*


The Story of Toolbox
--------------------

A tool is only useful if you know it exists and can find it and
information about it. Toolbox is an index of tools developed by and
for the Mozilla community.  Toolbox is not a hosting service -- it is just a
listing of packages which can live anywhere that are of use to Mozillians.

It could also be used to track:

* smart bookmarks
* code snippets


How to use Toolbox
------------------

The `index page </>`_ of toolbox lists all tools with the most
recently updated first.  A tool has a name, a description, a URL, and a
number of classifier fields.  Most everything is clickable.  Clicking on the
description lets you edit the description which will be saved on
blur. Clicking a URL, like `?author=harth </?author=harth>`_ will give
you the tools that ``harth`` wrote. There is also full text search
using the ``?q=`` parameter (like `?q=firefox </?q=firefox>`_ ) which
will search both the descriptions and all of the fields.

You can also display results by a particular field by going to that
field name.  For example, to display tools by author, go to 
`/author </author>`_ .  You can create a new tool at 
`/new </new>`_ .


Classifiers
-----------

Outside of the required fields (name, description, and URL), a tool
has a number of classifier tags.  Out of the box, these fields are:

* usage: what the tool is for
* dependencies: what does this tool need?
* type: is the tool a particular definative kind of software?
* language: which computer languages the tool is
* author: who wrote and/or maintains the software?


Tool Sources
------------

* setup.py
* addons.mozilla.org
* OpenWebApps: https://developer.mozilla.org/en/OpenWebApps/The_Manifest


Running Toolbox
---------------

You can download and run the toolbox software yourself:
http://github.com/k0s/toolbox

To serve in baseline mode, install the software and run::

 paster serve paste.ini

This will serve the handlers and static content using the paste
(http://pythonpaste.org) webserver.

The dispatcher (``toolbox.dispatcher:Dispatcher``) is the central (WSGI)
webapp that designates per-request to a number of handlers (from
``handlers.py``).  The dispatcher has a few options:

* template_dirs: extra directories (in order) to look for templates
* model_type: type of backend to use

These may be configured in the ``paste.ini`` file in the
``[app:toolbox]`` section by prepending with the namespace
``toolbox.``. It is advisable that you copy the example ``paste.ini``
file for your own usage needs.


TODO
----

Toolbox features a fairly free form data format (a few required fields
and an arbitrary number of classifiers). While this is a conceptually
simplistic base, there is much that can be done with it! Several
improvements are listed below:

* cleanup couch model and ensure it works
* add (e.g.) selenium tests
* add import functionality to couch backend and make sure it works
* keep track of which URLs projects cant use
* add scrapers:
  * setup.py 
  * AMO 
  * mozdev 
* you should be able to rename tools and change their (main) URL
* allow projects to point to a setup.py or AMO URL
* URLs in the description should be made links
* dependencies should link appropriately (e.g. to toolbox if possible)
* calendar view for projects
* make the /tags view useful
* make fields computationable
* integrate author with community phonebook (and bugzilla id)
* the first time someone edits a description (etc.) from a pointed-to
  file (e.g. a setup.py) then the project should be notified
* you should be able to edit a field, e.g. author.  Changing one field
  value should give the option to change all similar field values.
* you should be able to drag a field from one classifier to
  another. Doing so should prompt for doing this for all similar
  values
* you should be able to rename classifiers
* front-ending single-button INSTALL (when applicable)
* for the addons of particular types, there should be some correlation
  and some sort of direction/help of what these are and why these are
* a "Request a tool" link that functions like stack overflow; users
  can request a tool. If it does not exist, it gets turned into a
  bug. Users should also be able to point to a tool to answer the question

Links
-----

A big TODO item is links.  Currently, each tool has a canonical URL.
Since toolbox is an index, this has the distinct advantage of
associating a single URL with the project.  It is assumed that the
linked-to resource should point to auxilliary resources as necessary.

However, as an index is useful for correlating information --
connecting the dots -- allowing a variety of links both allows the
browser to have information at their fingertips, but also to allow
mapping and intelligent manipulation of tools by their link types.
Several types of links may be recorded:

* repository
* how to report bugs
* wiki
* pypi


Other Resources
---------------

Mozilla tools are recorded on other sites too.

* http://www.mozdev.org/
* https://wiki.mozilla.org/User:Jprosevear/Tools
