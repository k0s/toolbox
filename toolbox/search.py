import os
import shutil
import tempfile

from whoosh import fields
from whoosh import index
from whoosh.query import Or
from whoosh.query import Term
#from whoosh import store
from whoosh.qparser import QueryParser

class WhooshSearch(object):
    """full-text search"""

    def __init__(self, whoosh_index=None):
        """
        - whoosh_index : whoosh index directory
        """
        self.schema = fields.Schema(name=fields.ID(unique=True, stored=True),
                                    description=fields.TEXT)
        self.keywords = set([])
        self.tempdir = False
        if whoosh_index is None:
            whoosh_index = tempfile.mkdtemp()
            self.tempdir = True
        if not os.path.exists(whoosh_index):
            os.makedirs(whoosh_index)
        self.index = whoosh_index
        self.ix = index.create_in(self.index, self.schema)

    def update(self, name, description, **kw):
        """update adocument"""

        writer = self.ix.writer()

        # add keywords
        for key in kw:
            if key not in self.keywords:
                writer.add_field(key, fields.KEYWORD)
                self.keywords.add(key)
            if not isinstance(kw[key], basestring):
                kw[key] = ' '.join(kw[key])
            kw[key] = unicode(kw[key])

        # convert to unicode for whoosh
        # really whoosh should do this for us
        # and really python should be unicode-based :(
        name = unicode(name)
        description = unicode(description)

        writer.update_document(name=name, description=description, **kw)
        writer.commit()

    def __call__(self, query):
        """search"""
        query = unicode(query)
        query_parser = QueryParser("description", schema=self.ix.schema)
        myquery = query_parser.parse(query)
        extendedquery = Or([myquery] +
                           [Term(field, query) for field in self.keywords])
        searcher = self.ix.searcher()
        return [i['name'] for i in searcher.search(extendedquery)]
        
    def __del__(self):
        if self.tempdir:
            # delete the temporary directory, if present
            shutil.rmtree(self.index)
