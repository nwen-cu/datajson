from typing import Any
from typing import Dict, List

import os
import sys
import io

import base64
import json

optional_modules = {}


import xxhash


try:
    import numpy as np
    optional_modules['numpy'] = True
except ModuleNotFoundError:
    optional_modules['numpy'] = False
    

config = {
    'use_bson': False, 
}            


def dump_json(obj, generate_hash=False):
    doc = json.dumps(obj, cls=Encoder, sort_keys=True)
    if generate_hash:
        h = hash_document(doc)
        return doc, h
    else:
        return doc


def load_json(s):
    return json.loads(s, cls=Decoder)


def hash_document(doc):
    return xxhash.xxh3_128_hexdigest(doc)
      
    
class Encoder(json.JSONEncoder):
    def default(self, obj):
        if optional_modules['numpy']:
            if isinstance(obj, np.ndarray):
                buf = io.BytesIO()
                np.save(buf, obj, allow_pickle=False)
                arr = base64.urlsafe_b64encode(buf.getvalue()).decode('ascii')
                buf.close()
                return {'__numpy__': arr}
        return json.JSONEncoder.default(self, obj)
    
    
class Decoder(json.JSONDecoder):
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
            
            
            