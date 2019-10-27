import unittest
from hsc import metadata

class TestMetadata(unittest.TestCase):

	def setUp(self):
		self.metadata_obj = metadata.Metadata()

	def test_metadata_obj_is_not_none(self):
		self.assertIsNotNone(self.metadata_obj)


if __name__ == '__main__': 
    unittest.main() 
