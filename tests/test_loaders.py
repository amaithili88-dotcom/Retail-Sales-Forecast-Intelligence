import unittest
from src.loaders.base_loader import BaseLoader

class TestBaseLoader(unittest.TestCase):

    def setUp(self):
        self.loader = BaseLoader()

    def test_load(self):
        with self.assertRaises(NotImplementedError):
            self.loader.load()

if __name__ == '__main__':
    unittest.main()