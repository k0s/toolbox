import os
import shutil
import tempfile

from whoosh import fields
from whoosh import index
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
        self.tempdir = False
        if whoosh_index is None:
            whoosh_index = tempfile.mkdtemp()
            self.tempdir = True
        if not os.path.exists(whoosh_index):
            os.makedirs(whoosh_index)
        self.index = whoosh_index
        self.ix = index.create_in(self.index, self.schema)

    def update(self, name, description):
        """update adocument"""
        writer = self.ix.writer()
        writer.update_document(name=name, description=description)
        writer.commit()

    def __call__(self, query):
        """search"""
        q = QueryParser("description", schema=self.ix.schema).parse(unicode(query))
        searcher = self.ix.searcher()
        return [i['name'] for i in searcher.search(q)]
        
    def __del__(self):
        if self.tempdir:
            # delete the temporary directory, if present
            shutil.rmtree(self.index)
