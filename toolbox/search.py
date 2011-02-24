import os
import shutil
import tempfile

from whoosh import fields
from whoosh import index
#from whoosh import store

class WhooshSearch(object):
    """full-text search"""

    def __init__(self, whoosh_index=None):
        """
        - whoosh_index : whoosh index directory
        """
        self.schema = fields.Schema(name=fields.ID,
                                    description=fields.TEXT)
        self.tempdir = False
        if whoosh_index is None:
            whoosh_index = tempfile.mkdtemp()
            self.tempdir = True
        if not os.path.exists(whoosh_index):
            os.makedirs(whoosh_index)
        self.index = whoosh_index
        self.ix = index.create_in(self.index, self.schema)

    def __del__(self):
        if self.tempdir:
            shutil.rmtree(self.index)
