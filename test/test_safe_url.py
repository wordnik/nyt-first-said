import unittest
from parsers.utils import make_url_safe

class TestSafeURLSuite(unittest.TestCase):
  def test_basic(self):
      self.assertEqual(make_url_safe("https://test.test/path with spaces"), "https://test.test/path%20with%20spaces")

if __name__ == '__main__':
    unittest.main()
