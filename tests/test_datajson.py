import unittest
import json
from datajson import dumps, dump, loads, load, hash_document

class TestDataJson(unittest.TestCase):
    def test_dumps_loads(self):
        data = {'key': 'value'}
        json_str = dumps(data)
        self.assertEqual(loads(json_str), data)

    def test_dump_load(self):
        data = {'key': 'value'}
        with open('test.json', 'w') as f:
            dump(data, f)
        with open('test.json', 'r') as f:
            self.assertEqual(load(f), data)
    
    def test_hash_document(self):
        data = {'key': 'value'}
        json_str = dumps(data)
        h = hash_document(json_str)
        self.assertIsInstance(h, str)

if __name__ == '__main__':
    unittest.main()