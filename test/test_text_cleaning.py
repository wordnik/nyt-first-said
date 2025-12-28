import unittest
from utils.text_cleaning import remove_punctuation, remove_trouble_characters, has_username

class TestCleaningSuite(unittest.TestCase):
    def test_punctuation(self):
        self.assertEqual(remove_punctuation("Joe’s"), "Joe", "Special apostrophe removed.")

    def test_clean_trouble_chars(self):
        self.assertEqual(remove_trouble_characters("\u200Dhas\u200D"), "has", "Zero-width joiner removed.")
        self.assertEqual(remove_trouble_characters("to\u00A0"), "to", "Non-breaking space removed.")

    def test_has_username(self):
        self.assertEqual(has_username("@ausmencricket"), True, "@-based username found.")
        self.assertEqual(has_username("cricket"), False, "Normal word identified.")
        self.assertEqual(has_username("ab@normal.com"), True, "Email found.")

if __name__ == '__main__':
    unittest.main()
