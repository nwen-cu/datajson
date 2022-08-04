from typing import Any
from typing import Dict, List

import os
import sys
import io

import base64
import json

optional_modules = {}

try:
    import numpy as np
    optional_modules['numpy'] = True
    print('numpy loaded')
except ModuleNotFoundError:
    optional_modules['numpy'] = False
    print('numpy not found')

config = {'use_bson': False}


def dumps(obj):
    return json.dumps(obj, cls=NumDocEncoder, sort_keys=True)


def loads(s):
    return json.loads(s, cls=NumDocDecoder)
      
    
class NumDocEncoder(json.JSONEncoder):
    def default(self, obj):
        if optional_modules['numpy']:
            if isinstance(obj, np.ndarray):
                buf = io.BytesIO()
                np.save(buf, obj, allow_pickle=False)
                arr = base64.urlsafe_b64encode(buf.getvalue()).decode('ascii')
                buf.close()
                return {'__numpy__': arr}
        return json.JSONEncoder.default(self, obj)
    
    
class NumDocDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
        
    def object_hook(self, dct):
        if '__numpy__' in dct:
            if not optional_modules['numpy']:
                raise ModuleNotFoundError('Module numpy required for decode this document')
            buf = io.BytesIO(base64.urlsafe_b64decode(dct['__numpy__']))
            arr = np.load(buf)
            buf.close()
            return arr
        return dct
            
            
            