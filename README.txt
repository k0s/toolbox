The Story of Toolbox
====================

Toolbox is fundamentally a document-oriented approach to resource
indexing.  A "tool" consists three mandatory string fields -- name,
description, and URL -- that are generic to the large class of problems
of web resources, as well as classifiers, such as author, usage, type,
etc. A tool may have an arbitrary number of classifier fields as
needed.  Each classifier consists of a set of values with which a tool
is tagged. This gives toolbox the flexibility to fit a large number of
data models, such as PYPI, DOAP, and others.


Running Toolbox
---------------

You can download and run the toolbox software yourself:
http://github.com/k0s/toolbox

To serve in baseline mode, install the software and run::

 paster serve paste.ini

This will serve the handlers and static content using the paste
(http://pythonpaste.org) webserver using ``README.txt`` as the
``/about`` page and serving the data in ``sample``.

The dispatcher (``toolbox.dispatcher:Dispatcher``) is the central (WSGI)
webapp that designates per-request to a number of handlers (from
``handlers.py``).  The dispatcher has a few options:

* about: path to a restructured text file to serve at ``/about``
* model_type: name of the backend to use (memory_cache, file_cache, or couch)
* template_dir: extra directory to look for templates

These may be configured in the ``paste.ini`` file in the
``[app:toolbox]`` section by prepending with the namespace
``toolbox.``. It is advisable that you copy the example ``paste.ini``
file for your own usage needs.  Additional ``toolbox.``-namespaced
arguments will be passed to the model.  For instance, to specify the
directory for the ``file_cache`` model, the provided ``paste.ini`` uses
``toolbox.directory = %(here)s/sample``.


Architecture
------------

Toolbox uses a fairly simple architecture with a single abstract data
model allowing an arbitrary number of implementations to be constructed::

 Interfaces            Implementations

 +----+              +-+-----+
 |HTTP|              | |files|
 +----+---\  +-----+ | +-----+
           |-|model|-+-+-----+
 +------+-/  +-----+ | |couch|
 |script|            | +-----+
 +------+            +-+------+
                     | |memory|
                     | +------+
                     +-+---+
                       |...|
                       +---+

Toolbox was originally intended to use a directory of files, one per project,
as the backend. These were originally intended to be HTML files as the
above model may be clearly mapped as HTML::

 <div class="project"><h1><a href="{{url}}">{{name}}</a></h1>
 <p class="description">{{description}}</p>
 {{for field in fields}}
  <ul class="{{field}}">
  {{for value in values[field]}}
   <li>{{value}}</li>
  {{endfor}}
 {{endfor}}
 </div>

This microformat approach allows not only easy editing of the HTML
documents, but the documents may be indepently served and displayed
without the toolbox server-side. 

The HTML microformat was never implemented (though, since the model
backend is pluggable, it easily could be). Instead, the original
implementation used JSON blobs stored in one file per tool. This
approach loses the displayable aspect, though since JSON is a defined
format with several good tools for exploring and manipulating the data
perhaps this disavantage is offset.

A couch backend was also written.

      +------------+-----------+------------+
      |Displayable?|File-based?|Concurrency?|
+-----+------------+-----------+------------+
|HTML |Yes         |Yes        |No          |
+-----+------------+-----------+------------+
|JSON |Not really  |Yes        |No          |
+-----+------------+-----------+------------+
|Couch|No          |No         |Yes?        |
+-----+------------+-----------+------------+

The concurrency issue with file-based documennt backends may be
overcome by using locked files.  Ideally, this is accomplished at the
filesystem level.  If your filesystem does not promote this
functionality, it may be introduced programmatically.  A rough cartoon
of a good implementation is as follows:

1. A worker thread is spawned to write the data asynchronously. The
data is sent to the worker thread.

2. The worker checks for the presence of a lockfile (herein further
detailed). If the lockfile exists and is owned by an active process,
the worker waits until said process is done with it. (For a more
robust implementation, the worker sends a request to write the file to
some controller.)

3. The worker owns a lockfile based on its PID in some directory
parallel to the directory root under consideration (for example,
``/tmp/toolbox/lock/${PID}-${filename}.lck``).

4. The worker writes to the file.

5. The worker removes the lock

The toolbox web service uses a dispatcher->handler framework.  The
handlers are loosely pluggable (they are assigned in the dispatcher),
but could (and probably should) be made completely pluggable.  That
said, the toolbox web system features an integration of templates,
static resources (javascript, css, images), and handlers, so true
pluggability is further away than just supporting pluggable handlers
in the dispatcher.

Deployment, however, may be tailored as desired.  Any of the given
templates may be overridden via passing a ``template_dir`` parameter
with a path to a directory that have templates of the appropriate
names as found in toolbox's ``templates`` directory. 

Likewise, the static files (css, js, etc.) are served using ``paste``'s 
``StaticURLParser`` out of toolbox's ``static`` directory. (See
toolbox's ``factory.py``.) Notably this is *not* done using the WSGI
app itself.  Doing it with middleware allows the deployment to be
customizable by writing your own factory.  For example, instead of
using the ``paste`` webserver and the included ``paste.ini``, you
could use nginx or apache and ``mod_wsgi`` with a factory file
invoking ``Dispatcher`` with the desired arguments and serving the
static files with an arbitrary static file server.

It is common sense, if rarely followed, that deployment should be
simple.  If you want to get toolbox running on your desktop and/or for
testing, you should be able to do this easily (see the ``INSTALL.sh``
for a simple installation using ``bash``; you'll probably want to
perform these steps by hand for any sort of real-world deployment).
If you want a highly customized deployment, then this will require
more expertise and manual setup.

The template data and the JSON are closely tied together.  This has the
distinct advantage of avoiding data translation steps and avoiding
code duplication.

Toolbox uses several light-footprint libraries:

* webob for Request/Response handling: http://pythonpaste.org/webob/

* tempita for (HTML) templates: http://pythonpaste.org/tempita/

* whoosh for search.  This pure-python implementation of full-text
  search is relatively fast (for python) and should scale decently to
  the target scale of toolbox (1000s or 10000s of tools). While not as
  fast as lucene, whoosh is easy to deploy and has a good API and
  preserves toolbox as a deployable software product versus an
  instance that requires the expert configuration, maintainence, and
  tuning of several disparate software products that is both
  non-automatable (cannot be installed with a script) and
  time-consuming. http://packages.python.org/Whoosh/

* jQuery: jQuery is the best JavaScript library and everyone
  should use it. http://jquery.com/

* jeditable for AJAXy editing: http://www.appelsiini.net/projects/jeditable

* jquery-token for autocomplete: http://loopj.com/jquery-tokeninput/

* less for dynamic stylesheets: http://lesscss.org/


User Interaction
----------------

A user will typically interact with Toolbox through the AJAX web
interface.  The server side returns relatively simple (HTML) markup,
but structured in such a way that JavaScript may be utilized to
promote rich interaction.  The simple HTML + complex JS manifests
several things:

1. The document is a document. The tools HTML presented to the user (with
the current objectionable exception of the per-project Delete button)
is a document form of the data. It can be clearly and easily
translated to data (for e.g. import/export) or simply marked up using
(e.g.) JS to add functionality. By keeping concerns seperate
(presentation layer vs. interaction layer) a self-evident clarity is
maintained.

2. Computation is shifted client-side. Often, an otherwise lightweight
webapp loses considerable performance rendering complex templates. By
keeping the templates light-weight and doing control presentation and
handling in JS, high performance is preserved.


What Toolbox Doesn't Do
-----------------------

* versioning: toolbox exposes editing towards a canonical document.
  It doesn't do versioning.  A model instance may do whatever
  versioning it desires, and since the models are pluggable, it would
  be relatively painless to subclass e.g. the file-based model and
  have a post-save hook which does an e.g. ``hg commit``. Customized
  templates could be used to display this information.

* authentication: the information presented by toolbox is freely
  readable and editable. This is by intention, as by going to a "wiki"
  model and presenting a easy to use, context-switching-free interface
  curation is encouraged (ignoring the possibly imaginary problem of
  wiki-spam). Access-level auth could be implemented using WSGI
  middleware (e.g. repoze.who or bitsyauth) or through a front end
  "webserver" integration layer such as Apache or nginx. Finer grained
  control of the presentation layer could be realized by using custom
  templates.


What Toolbox Would Like To Do
-----------------------------

Ultimately, toolbox should be as federated as possible.  The basic
architecture of toolbox as a web service + supporting scripts makes
this feasible and more self-contained than most proposed federated
services.  The basic federated model has proved, in practice,
difficult to achieve through purely the (HTTP) client-server model, as
without complete federation and adherence to protocol offline cron
jobs should be utilized to pull external data sources. If a webservice
only desires to talk to others of its own type and are willing to keep
a queue of requests for when hosts are offline, entire HTTP federation
may be implemented with only a configuration-specified discovery
service to find the nodes.


Evolution
---------

Often, a piece software is presented as a state out of context (that
is minus the evolution which led it to be and led it to look further
out towards beyond the horizon).  While this is an interesting special
effect for an art project, software being communication this
is only conducive to software in the darkest of black-box approaches.

"Beers are like web frameworks: if they're not micro, you don't know
what you're talking about." - hipsterhacker

For sites that fit the architecture of a given framework, it may be
advisable to make use of them.  However, for most webapp/webservice
categories which have a finite scope and definitive intent, it is
often easier, more maintainable, and more legible to build a complete
HTTP->WSGI->app architecture than to try to hammer a framework into
fitting your problem or redefining the problem to fit the framework.
This approach was used for toolbox.

The GenshiView template, http://k0s.org/hg/GenshiView, was invoked to
generate a basic dispatcher->handler system.  The cruft was removed,
leaving only the basic structure and the TempitaHandler since tempita
is lightweight and it was envisioned that filesystem tempita templates
(MakeItSo!) would be used elsewhere in the project.  The basic
handlers (projects views, field-sorted view, new, etc.) were written
and soon a usable interface was constructed.

A ``sample`` directory was created to hold the JSON blobs. Because
this was done early on, two goals were achieved: 

1. the software could be dogfooded immediately using actual applicable
data. This helped expose a number of issues concerning the data format
right away.

2. There was a place to put tools before the project reached a
deployable state (previously, a few had lived in a static state using
a rough sketch of the HTML microformat discussed above on
k0s.org). Since the main point of toolbox is to record Mozilla tools,
the wealth of references mentioned in passing could be put somewhere,
instead of passed by and forgotten.  One wishes that they do not miss
the train while purchasing a ticket.

The original intent, when the file-based JSON blob approach was to be
the deployed backend, was to have two repositories: one for the code
and one for the JSON blobs.  When this approach was scrapped, the
file-based JSON blobs were relegated to the ``sample`` directory, with
the intent to be to import them into e.g. a couch database on actual
deployment (using an import script). The samples could then be used
for testing.

The model has a single "setter" function, ``def update``, used for
both creating and updating projects.  Due to this and due to the fact
the model was ABC/pluggable from the beginning, a converter ``export``
function could be trivially written at the ABC-level::

    def export(self, other):
        """export the current model to another model instance"""
        for project in self.get():
            other.update(project)

This with an accompanying CLI utility was used to migrate from JSON
blob files in the ``sample`` directory to the couch instance.  This
particular methodology as applied to an unexpected problem (the
unanticipated switch from JSON blobs to couch) is a good example of
the power of using a problem to drive the software forward (in this
case, creation of a universal export function and associated command
line utility). The alternative, a one-off manual data migration, would
have been just as time consuming, would not be repeatable, would not
have extended toolbox, and may have (like many one-offs do) infected
the code base with associated semi-permanant vestiges.  In general,
problems should be used to drive innovation.  This can only be done if
the software is kept in a reasonably good state.  Otherwise
considerable (though probably worthwhile) refactoring should be done
prior to feature extension which will become cost-prohibitive in
time-critical situations where a one-off is (more) likely to be employed.


Use Cases
---------

The target use-case is software tools for Mozilla, or, more generally,
a software index.  For this case, the default fields uses are given in
the paste.ini file: usage, author, type, language. More fields may be
added to the running instance in the future.

However, the classifier classification can be used for a wide variety
of web-locatable resources.  A few examples:

* songs: artist, album, genre, instruments
* de.li.cio.us: type, media, author, site


Resources
---------

* http://readthedocs.org/
