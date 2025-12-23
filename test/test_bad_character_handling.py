import unittest
from utils.text_cleaning import remove_punctuation 

class BadCharacterHandlingSuite(unittest.TestCase):
  def test_basic(self):
      self.assertEqual(remove_punctuation("Joe’s"), "Joe", "Special apostrophe removed.")

if __name__ == '__main__':
    unittest.main()
