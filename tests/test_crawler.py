import unittest
from hsc import Crawler

class TestCrawler(unittest.TestCase):

	def setUp(self):
		self.crawler_obj = Crawler()

	def test_crawler_obj_is_not_none(self):
		self.assertIsNotNone(self.crawler_obj)


if __name__ == '__main__': 
    unittest.main() 
