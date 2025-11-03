# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import json
import argparse
from numpy import log as ln
from utils.bloom_filter import BloomFilter

ln_2 = 0.693147181 # ln(2)
	
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str, required=True,
                    help="Path to the JSON file with a word list under the key `words`")
parser.add_argument("-l", "--false_positive_limit", type=float, default=.01)
parser.add_argument("-o", "--out", type=str, required=True)
args = parser.parse_args()

word_list = []

with open(args.file, "r") as f:
  wordJSON = json.loads(f.read())
  word_list = wordJSON.get("words", [])
  f.close()

print(f"Word count: {len(word_list)}")

# https://en.wikipedia.org/wiki/Bloom_filter#Optimal_number_of_hash_functions
hash_count = round(-2.08 * ln(args.false_positive_limit))
print(f"Hash count: {hash_count}")

bloom_filter = BloomFilter(len(word_list), hash_count)
for word in word_list:
  bloom_filter.add(word)

bloom_filter.save(args.out)
