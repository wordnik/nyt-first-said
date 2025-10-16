import unittest
from utils.word_count_cache import WordCountCache

class WordCountCacheSuite(unittest.TestCase):
  def test_basic(self):
      cache = WordCountCache()
      cache.incr("word:hi")
      cache.incr("word:hi")
      self.assertEqual(cache.get("word:hi"), 2, "Incrementing a key twice sets the value to 2.")
      cache.incr("word:hi")
      self.assertEqual(cache.get("word:hi"), 3, "Incrementing a key thrice sets the value to 3.")

      self.assertEqual(cache.get("word:hey"), None, "Getting a key not set returns None")
    
      cache.set("word:hey", 4)
      self.assertEqual(cache.get("word:hey"), 4, "Getting a key set to 4 returns 4")

      cache.incr("word:hey")
      self.assertEqual(cache.get("word:hey"), 5, "Incrementing a set key works")

if __name__ == '__main__':
    unittest.main()
