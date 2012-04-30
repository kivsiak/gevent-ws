__author__ = 'kivsiak'

import unittest


from bson import BSON

class MyTestCase(unittest.TestCase):
    def testSerialization(self):
        message  =  {"test": "me"}
        sm = BSON.encode(message)
        self.assertEqual(message, BSON(sm).decode())

if __name__ == '__main__':
    unittest.main()
