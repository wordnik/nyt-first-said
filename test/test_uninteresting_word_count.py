import unittest
from utils.uninteresting_words import *

class UnintererstingWordCountSuite(unittest.TestCase):
  def test_basic(self):
      word = "unrealwordasdf"
      reset_uninteresting_count_for_word(word)
      count = get_uninteresting_count_for_word(word)
      self.assertEqual(count, 0, "Reset sets the count to 0.")

      increment_uninteresting_count_for_word(word)
      count = get_uninteresting_count_for_word(word)
      self.assertEqual(count, 1, "Incrementing takes the count to 1.")

      for i in range(50):
        increment_uninteresting_count_for_word(word)

      count = get_uninteresting_count_for_word(word)
      self.assertEqual(count, 51, "Incrementing 50 times takes the count to 51.")

      reset_uninteresting_count_for_word(word)
      count = get_uninteresting_count_for_word(word)
      self.assertEqual(count, 0, "Reset sets the count to 0.")

      count = get_uninteresting_count_for_word("htnsueoa")
      self.assertEqual(count, 0, "The count for an unrecorded word is 0")

if __name__ == '__main__':
    unittest.main()
