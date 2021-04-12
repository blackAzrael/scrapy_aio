import time

from scrapy_aio.utils.request import request_fingerprint

from . import connection
from .BloomfilterOnRedis import BloomFilter


class BaseDupeFilter:

    @classmethod
    def from_settings(cls, settings):
        return cls()

    def request_seen(self, request):
        return False

    def open(self):  # can return deferred
        pass

    def close(self, reason):  # can return a deferred
        pass

    def log(self, request, spider):  # log that a request has been filtered
        pass

class RFPDupeFilter(BaseDupeFilter):
    """Redis-based request duplication filter"""

    def __init__(self, server, key,blockNum):
        """Initialize duplication filter

        Parameters
        ----------
        server : Redis instance
        key : str
            Where to store fingerprints
        """
        self.server = server
        self.key = key
        self.blockNum = blockNum
        self.bf = BloomFilter(server, key, blockNum=self.blockNum)  # you can increase blockNum if your are filtering too many urls
                                                        # 如果你过滤了太多的url，你可以增加blockNum

    @classmethod
    def from_settings(cls, settings):
        server = connection.from_settings_filter(settings)
        # create one-time key. needed to support to use this
        # class as standalone dupefilter with scrapy's default scheduler
        # if scrapy passes spider on open() method this wouldn't be needed
        key = "dupefilter:%s" % int(time.time())
        blockNum = settings.getint("blockNum")
        return cls(server, key, blockNum)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def request_seen(self, request):
        fp = request_fingerprint(request)
        if self.bf.isContains(fp):
            return True
        else:
            self.bf.insert(fp)
            return False
        # added = self.server.sadd(self.key, fp)
        # return not added

    def close(self, reason):
        """Delete data on close. Called by scrapy's scheduler"""
        self.clear()

    def clear(self):
        """Clears fingerprints data"""
        key = self.key + "*"
        key_list = self.server.keys(key)
        for tmp_key in key_list:
            self.server.delete(tmp_key)
