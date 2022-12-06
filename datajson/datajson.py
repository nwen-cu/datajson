from typing import Any
from typing import Dict, List

import os
import sys
import io

import gzip
import base64
import json

optional_modules = {}


import xxhash


try:
    import numpy as np
    optional_modules['numpy'] = True
except ModuleNotFoundError:
    optional_modules['numpy'] = False

    
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


def numpy_encode_v1(obj):
    buf = io.BytesIO()
    np.save(buf, obj, allow_pickle=False)
    arr = base64.b85encode(gzip.compress(buf.getvalue(), mtime=0)).decode('ascii')
    buf.close()
    return {'__np1__': arr}

def numpy_decode_v1(dct):
    buf = io.BytesIO(gzip.decompress(base64.b85decode(dct['__np1__'])))
    arr = np.load(buf)
    buf.close()
    return arr

    
class Encoder(json.JSONEncoder):
    def default(self, obj):
        if optional_modules['numpy']:
            if isinstance(obj, np.ndarray):
                return numpy_encode_v1(obj)
        return json.JSONEncoder.default(self, obj)
    
    
class Decoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
        
    def object_hook(self, dct):
        if '__np1__' in dct:
            if not optional_modules['numpy']:
                raise ModuleNotFoundError('Module numpy required for decode this document')
            return numpy_decode_v1(dct)
        return dct
            
    
            
            