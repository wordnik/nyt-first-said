import unittest
from utils.bloom_filter import BloomFilter

class BloomFilterSuite(unittest.TestCase):
  def test_basic(self):
    bloom_filter = BloomFilter(100, 3)
    bloom_filter.add("apple")
    bloom_filter.add("banana")
    self.assertTrue(bloom_filter.contains("apple"))
    self.assertFalse(bloom_filter.contains("orange"))

  def test_persistence(self):
    bloom_filter = BloomFilter(size=100, num_hashes=3)
    bloom_filter.add("apple")
    bloom_filter.add("banana")
    bloom_filter.save("test/tmp/test_persistence.txt")

    loaded_bloom_filter = BloomFilter(100, 3)
    loaded_bloom_filter.load("test/tmp/test_persistence.txt")
    self.assertTrue(loaded_bloom_filter.contains("apple"))
    self.assertFalse(loaded_bloom_filter.contains("orange"))

  def test_prebuilt(self):
    bloom_filter = BloomFilter(size=26576494, num_hashes=10)
    bloom_filter.load("data/bloom_filter.bits")

    is_there = ["apple", "orange", "#OccupyYourNeighborhood", "rizzle", "yougotdunkedon"]
    for word in is_there:
        self.assertTrue(bloom_filter.contains(word))

    not_there = ["?????aoeuaoeuaoeuasoethusar", "urobiome", "mommune", "rizzless", "wozzle"]
    for word in not_there:
      self.assertFalse(bloom_filter.contains(word))

if __name__ == '__main__':
    unittest.main()
