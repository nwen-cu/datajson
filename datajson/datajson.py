from typing import Any, Dict, Tuple, Union, Optional, IO
import os
import sys
import io
import gzip
import base64
import json
import xxhash

optional_modules = {}

try:
    import numpy as np
    optional_modules['numpy'] = True
except ModuleNotFoundError:
    optional_modules['numpy'] = False

def dumps(obj: Any, *, generate_hash: bool = False, **kwargs) -> Union[str, Tuple[str, str]]:
    """
    Serialize an object to a JSON formatted string. Optionally generate a hash of the JSON document.

    Parameters
    ----------
    obj : Any
        The object to serialize.
    generate_hash : bool, optional
        If True, generate a hash for the JSON document, by default False.
    **kwargs
        Additional keyword arguments to pass to `json.dumps`.

    Returns
    -------
    Union[str, Tuple[str, str]]
        The JSON string, and if generate_hash is True, a tuple containing the JSON string and its hash.
    """
    doc = json.dumps(obj, cls=Encoder, sort_keys=True, **kwargs)
    if generate_hash:
        h = hash_document(doc)
        return doc, h
    return doc

def dump(obj: Any, fp: IO[str], *, generate_hash: bool = False, **kwargs) -> Optional[str]:
    """
    Serialize an object to a JSON formatted stream. Optionally generate a hash of the JSON document.

    Parameters
    ----------
    obj : Any
        The object to serialize.
    fp : IO[str]
        The file-like object to write the JSON string to.
    generate_hash : bool, optional
        If True, generate a hash for the JSON document, by default False.
    **kwargs
        Additional keyword arguments to pass to `json.dump`.

    Returns
    -------
    Optional[str]
        If generate_hash is True, the hash of the JSON document, otherwise None.
    """
    doc = json.dumps(obj, cls=Encoder, sort_keys=True, **kwargs)
    fp.write(doc)
    if generate_hash:
        return hash_document(doc)
    return None

def loads(s: str, **kwargs) -> Any:
    """
    Deserialize a JSON formatted string to an object.

    Parameters
    ----------
    s : str
        The JSON string to deserialize.
    **kwargs
        Additional keyword arguments to pass to `json.loads`.

    Returns
    -------
    Any
        The deserialized object.
    """
    return json.loads(s, cls=Decoder, **kwargs)

def load(fp: IO[str], **kwargs) -> Any:
    """
    Deserialize a JSON formatted stream to an object.

    Parameters
    ----------
    fp : IO[str]
        The file-like object containing the JSON string.
    **kwargs
        Additional keyword arguments to pass to `json.load`.

    Returns
    -------
    Any
        The deserialized object.
    """
    return json.load(fp, cls=Decoder, **kwargs)

def hash_document(doc: str) -> str:
    """
    Generate a hash for a given JSON document string.

    Parameters
    ----------
    doc : str
        The JSON document string.

    Returns
    -------
    str
        The hash of the document.
    """
    return xxhash.xxh3_128_hexdigest(doc)

def numpy_encode_v1(obj: np.ndarray) -> Dict[str, str]:
    """
    Encode a NumPy array to a base85 string with gzip compression.

    Parameters
    ----------
    obj : np.ndarray
        The NumPy array to encode.

    Returns
    -------
    Dict[str, str]
        A dictionary with the encoded array.
    """
    buf = io.BytesIO()
    np.save(buf, obj, allow_pickle=False)
    arr = base64.b85encode(gzip.compress(buf.getvalue(), mtime=0)).decode('ascii')
    buf.close()
    return {'__np1__': arr}

def numpy_decode_v1(dct: Dict[str, str]) -> np.ndarray:
    """
    Decode a base85 string with gzip compression to a NumPy array.

    Parameters
    ----------
    dct : Dict[str, str]
        The dictionary containing the encoded array.

    Returns
    -------
    np.ndarray
        The decoded NumPy array.
    """
    buf = io.BytesIO(gzip.decompress(base64.b85decode(dct['__np1__'])))
    arr = np.load(buf)
    buf.close()
    return arr

class Encoder(json.JSONEncoder):
    """
    Custom JSON Encoder that handles NumPy arrays.
    """
    def default(self, obj: Any) -> Any:
        if optional_modules['numpy'] and isinstance(obj, np.ndarray):
            return numpy_encode_v1(obj)
        return super().default(obj)

class Decoder(json.JSONDecoder):
    """
    Custom JSON Decoder that handles encoded NumPy arrays.
    """
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
        
    def object_hook(self, dct: Dict[str, Any]) -> Any:
        if '__np1__' in dct:
            if not optional_modules['numpy']:
                raise ModuleNotFoundError('Module numpy required to decode this document')
            return numpy_decode_v1(dct)
        return dct