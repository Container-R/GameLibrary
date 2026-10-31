"""Pure ABI/record tests: importing child does not load the Vulkan library."""
import unittest
from child import abi, classify_fill
from consume import validate_report, strict

class Pure(unittest.TestCase):
    def test_abi(self):
        self.assertTrue(abi()[1])
    def test_fill(self):
        self.assertEqual(classify_fill(0,2,2,[True,True]),'ENUMERATED_NONZERO')
        self.assertEqual(classify_fill(5,2,1,[True]),'ENUMERATED_PARTIAL')
        for result in (0,5):
            self.assertEqual(classify_fill(result,2,3,[]),'PROTOCOL_ANOMALY')
            self.assertEqual(classify_fill(result,2,1,[False]),'PROTOCOL_ANOMALY')
    def test_create_negative_trace(self):
        trace=[{'call':1,'name':'create','phase':'attempt'}, {'call':1,'name':'create','phase':'returned','result':-9}]
        record={'category':'INSTANCE_CREATION_FAILED','trace':trace,'create_result':-9}
        self.assertEqual(validate_report(record,trace),'INSTANCE_CREATION_FAILED')
        with self.assertRaises(ValueError): validate_report(record,trace[:1])
    def test_json(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}'):
            with self.assertRaises(ValueError): strict(text)

if __name__=='__main__': unittest.main()
