import unittest
from src.extractors.base_extractor import BaseExtractor

class TestBaseExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = BaseExtractor()

    def test_extract(self):
        with self.assertRaises(NotImplementedError):
            self.extractor.extract()

if __name__ == '__main__':
    unittest.main()