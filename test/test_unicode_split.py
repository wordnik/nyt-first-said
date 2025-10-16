import unittest
from parsers.utils import split_words_by_unicode_chars

class SplitByUnicodeSuite(unittest.TestCase):
  def test_basic(self):
      self.assertEqual(split_words_by_unicode_chars("Hey—:you"), ["Hey", ":you"])
      self.assertEqual(split_words_by_unicode_chars("“Sarcasm”"), ["Sarcasm"])

if __name__ == '__main__':
    unittest.main()
