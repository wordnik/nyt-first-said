import unittest
from utils.text_cleaning import remove_punctuation, remove_trouble_characters

class BadCharacterHandlingSuite(unittest.TestCase):
    def test_punctuation(self):
        self.assertEqual(remove_punctuation("Joe’s"), "Joe", "Special apostrophe removed.")

    def test_clean_trouble_chars(self):
        self.assertEqual(remove_trouble_characters("\u200Dhas\u200D"), "has", "Zero-width joiner removed.")
        self.assertEqual(remove_trouble_characters("to\u00A0"), "to", "Non-breaking space removed.")

if __name__ == '__main__':
    unittest.main()
