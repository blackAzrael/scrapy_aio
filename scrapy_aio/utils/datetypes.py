# -*- coding:utf-8 -*-
import collections
import weakref


class LocalCache(collections.OrderedDict):
    """Dictionary with a finite number of keys.

    Older items expires first.
    """

    def __init__(self, limit=None):
        super(LocalCache, self).__init__()
        self.limit = limit

    def __setitem__(self, key, value):
        if self.limit:
            while len(self) >= self.limit:
                self.popitem(last=False)
        super(LocalCache, self).__setitem__(key, value)


class LocalWeakReferencedCache(weakref.WeakKeyDictionary):
    """
    A weakref.WeakKeyDictionary implementation that uses LocalCache as its
    underlying data structure, making it ordered and capable of being size-limited.

    Useful for memoization, while avoiding keeping received
    arguments in memory only because of the cached references.

    Note: like LocalCache and unlike weakref.WeakKeyDictionary,
    it cannot be instantiated with an initial dictionary.
    """

    def __init__(self, limit=None):
        super(LocalWeakReferencedCache, self).__init__()
        self.data = LocalCache(limit=limit)

    def __setitem__(self, key, value):
        try:
            super(LocalWeakReferencedCache, self).__setitem__(key, value)
        except TypeError:
            pass  # key is not weak-referenceable, skip caching

    def __getitem__(self, key):
        try:
            return super(LocalWeakReferencedCache, self).__getitem__(key)
        except TypeError:
            return None  # key is not weak-referenceable, it's not cached
