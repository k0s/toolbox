toolbox
=======

*an index of Mozilla software tools*


The Story of Toolbox
--------------------

A tool is only useful if you know it exists and can find it and
information about it. Toolbox is an index of tools developed by and
for the Mozilla community.  Toolbox is not a hosting service -- it is a
listing of tools which can live anywhere that are of use to Mozillians.

It could also be used to track:

* smart bookmarks
* code snippets
* webapps

A tool will always have

* a *name* that uniquely identifies the tool
* a text *description* of the tool
* a canonical *URL* where you can find the tool

Tools can also have a 'usage' for what it applies to
(e.g. 'bugzilla'), a 'type' for what type of tool it is (e.g. 'addon'
or 'webapp'), 'authors' with the names and links of the authors, and
'languages' for what programming language the tool is written in.


How to use Toolbox
------------------

The `index page </>`_ of toolbox lists all tools with the most
recently updated first.  A tool has a name, a description, a URL, and a
number of classifier fields.  Most everything is clickable.  Clicking on the
description lets you edit the description which will be saved on
blur. Hovering over the tool title or URL will display an
`edit button <http://universaleditbutton.org/>`_ which on clicking
will allow you to edit the appropriate data.
Clicking a URL, like `?author=harth </?author=harth>`_ will give
you the tools that ``harth`` wrote. There is also full text search
using the ``?q=`` parameter (like `?q=firefox </?q=firefox>`_ ) which
will search both the descriptions and all of the fields.

You can also display results by a particular field by going to that
field name.  For example, to display tools by author, go to 
`/author </author>`_ .  You can add a new tool at 
`/new </new>`_ by providing its name, description, and URL. Upon
creation, you'll be redirected to the tool's index page where you can
add whatever classifiers you want.


Classifiers
-----------

Outside of the required fields (name, description, and URL), a tool
has a number of classifier tags.  Out of the box, these fields are:

* usage: what the tool is for
* type: is the tool a particular definative kind of software such as an addon?
* language: which computer languages the tool is written in
* author: who wrote and/or maintains the software?

You can freely add and remove classifiers for each project.
Autocomplete is enabled to help you find the classifier you want.


TODO
----

Toolbox features a fairly free form data format (a few required fields
and an arbitrary number of classifiers). While this is a conceptually
simplistic base, there is much that can be done with it! Several
improvements are listed below:

* add scrapers:
  * setup.py 
  * AMO 
  * mozdev 
* allow projects to point to a setup.py or AMO URL
* URLs in the description should be made links
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
* it would be nice to point the description to a URL
* front-ending single-button INSTALL (when applicable)
* for the addons of particular types, there should be some correlation
  and some sort of direction/help of what these are and why these are
* a "Request a tool" link that functions like stack overflow; users
  can request a tool. If it does not exist, it gets turned into a
  bug. Users should also be able to point to a tool to answer the
  question. Similarly, developers should be able to see a list of
  requested tools and take ownership of them if desired
* Similarly, users should be able to note similarity of tools and
  propose a consolidation strategy


Other Resources
---------------

Mozilla tools are recorded on other sites too.

* http://www.mozdev.org/
* https://wiki.mozilla.org/User:Jprosevear/Tools
* http://infomonkey.cdleary.com/
* http://userscripts.org/
