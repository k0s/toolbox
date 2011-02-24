toolbox
-------

a place to find Mozilla software tools

Other useful things:
* smart bookmarks
* code snippets

Testing
-------

To run in testing mode, cd to the toolbox directory and run::

 python factory.py

This will run a primitive wsgiref server on port 8080.

Improve instructions to come! :)

TODO
----

The list:

* allow editing of a tool via AJAX and add updating fields to model
* add a way of deleting a tool
* full-text search via whoosh
* add some CSS+JS
* keep track of which URLs projects cant use
* use a slotted template structure
* setup.py scraper
* AMO scraper
* more types of links should be allowed
* URLs in the description should be made links
* dependencies should link appropriately (e.g. to toolbox if possible)

The nitty-gritty:

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
