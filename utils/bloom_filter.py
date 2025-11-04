# https://molecularsciences.org/content/implementing-a-bloom-filter-in-python-a-detailed-guide/
from bitarray import bitarray
import hashlib

class BloomFilter:
  def __init__(self, size, num_hashes):
    self.size = size
    self.num_hashes = num_hashes
    self.bit_array = bitarray(size)
    self.bit_array.setall(0)

  def add(self, element):
    for i in range(self.num_hashes):
      index = self.hash_element(element, i) % self.size
      self.bit_array[index] = 1

  def contains(self, element):
    for i in range(self.num_hashes):
      index = self.hash_element(element, i) % self.size
      if not self.bit_array[index]:
        return False
    return True

  def hash_element(self, element, seed):
    hash_func = hashlib.sha256()
    hash_func.update((str(element) + str(seed)).encode('utf-8'))
    return int(hash_func.hexdigest(), 16)

  def save(self, path):
    with open(path, "wb") as f:
      self.bit_array.tofile(f)
      f.close()
    # print(f"Saved: {self.bit_array.tolist()}")

  def load(self, path):
    # print(f"Before load: {self.bit_array.tolist()}")
    self.bit_array = bitarray(0)
    # fromfile extends the array, so we want to start with 0.
    with open(path, "rb") as f:
      self.bit_array.fromfile(f)
      f.close()
    # print(f"Loaded: {self.bit_array.tolist()}")
    
