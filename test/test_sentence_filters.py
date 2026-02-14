import unittest
from utils.sentence_filters import has_balanced_punctuation

class SentenceFiltersSuite(unittest.TestCase):
    def test_punctuation_check(self):
        self.maxDiff = None
        self.assertEqual(has_balanced_punctuation("So many up and downs, but where there’s a will, there’s a way.”"), False)
        self.assertEqual(has_balanced_punctuation("“So many up and downs, but where there’s a will, there’s a way.”"), True)
        self.assertEqual(has_balanced_punctuation('They said, "OK."'), True)
        self.assertEqual(has_balanced_punctuation('"OK," they said.'), True)
        self.assertEqual(has_balanced_punctuation('"OK, they said.'), False)
        self.assertEqual(has_balanced_punctuation('OK, they" said.'), False)
        self.assertEqual(has_balanced_punctuation('"Supposedly, there were "real" "concerns about this," she said.'), False)

if __name__ == '__main__':
    unittest.main()
