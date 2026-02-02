import unittest
from parsers.utils import split_words_by_unicode_punctuation

class SplitByUnicodeSuite(unittest.TestCase):
  def test_basic(self):
      self.assertEqual(split_words_by_unicode_punctuation("Hey—:you"), ["Hey", ":you"])
      self.assertEqual(split_words_by_unicode_punctuation("“Sarcasm”"), ["Sarcasm"])
      self.assertEqual(split_words_by_unicode_punctuation("Hey…you"), ["Hey", "you"])

if __name__ == '__main__':
    unittest.main()
