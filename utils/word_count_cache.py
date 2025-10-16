# -*- coding: utf-8 -*-

# A cheap Redis stand-in

class WordCountCache():
    cache = {}

    def get(self, key):
        return self.cache.get(key)

    def incr(self, key):
        val = self.cache.get(key, 0)
        val += 1
        self.cache[key] = val

    def expire(self, key, duration):
        pass

    def set(self, key, value):
        self.cache[key] = int(value)

