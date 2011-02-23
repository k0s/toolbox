"""
utilities for toolbox
"""

try:
    import json
except ImportError:
    import simplejson as json

class JSONEncoder(json.JSONEncoder):
    """provide additional serialization for JSON"""

    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)

        return json.JSONEncoder.default(self, obj)

if __name__ == '__main__':
    # test the encoder
    testjson = {}

    # test date encoding
    from datetime import datetime
    testjson['date'] = datetime.now()

    # test set encoding
    testjson['set'] = set([1,2,3,2])

    print json.dumps(testjson, cls=JSONEncoder)
