# -*- coding:utf-8 -*-
from scrapy3.utils.request import request_fingerprint


class BaseDupeFilter(object):
    @classmethod
    def from_settings(cls, settings):
        return cls()

    async def request_seen(self, request):
        return False

    def open(self, spider):
        pass

    def close(self, reason):
        pass

    def log(self, request, spider):
        pass


class RFPDupeFilter(BaseDupeFilter):

    def __init__(self):
        self.fingerprints = set()

    async def request_seen(self, request):
        fp = self.request_fingerprint(request)
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)
        return False

    def request_fingerprint(self, request):
        return request_fingerprint(request)
