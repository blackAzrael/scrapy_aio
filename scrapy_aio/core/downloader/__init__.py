# -*- coding:utf-8 -*-
import logging
import random
import time
from collections import deque
from datetime import datetime

from scrapy_aio.core.downloader.handler import DownloadHandler
from scrapy_aio.core.downloader.middleware import DownloaderMiddlewareManager
from scrapy_aio.utils.datetypes import LocalCache
from scrapy_aio.utils.http import urlparse_cached
from scrapy_aio.utils.misc import load_object

logger = logging.getLogger(__name__)
dnscache = LocalCache(10000)


class Slot(object):

    def __init__(self, concurrency, delay, randomize_delay):
        self.concurrency = concurrency
        self.delay = delay
        self.randomize_delay = randomize_delay

        self.active = set()
        self.queue = deque()
        self.transferring = set()
        self.lastseen = 0
        self.latercall = None

    def free_transfer_slots(self):
        return self.concurrency - len(self.transferring)

    def download_delay(self):
        if self.randomize_delay:
            return random.uniform(0.5 * self.delay, 1.5 * self.delay)
        return self.delay

    def close(self):
        if self.latercall and self.latercall.active():
            self.latercall.cancel()

    def __repr__(self):
        cls_name = self.__class__.__name__
        return "%s(concurrency=%r, delay=%0.2f, randomize_delay=%r)" % (
            cls_name, self.concurrency, self.delay, self.randomize_delay)

    def __str__(self):
        return (
                "<downloader.Slot concurrency=%r delay=%0.2f randomize_delay=%r "
                "len(active)=%d len(queue)=%d len(transferring)=%d lastseen=%s>" % (
                    self.concurrency, self.delay, self.randomize_delay,
                    len(self.active), len(self.queue), len(self.transferring),
                    datetime.fromtimestamp(self.lastseen).isoformat()
                )
        )


def _get_concurrency_delay(concurrency, spider, settings):
    delay = settings.getfloat('DOWNLOAD_DELAY')
    if hasattr(spider, 'download_delay'):
        delay = spider.download_delay

    if hasattr(spider, 'max_concurrent_requests'):
        concurrency = spider.max_concurrent_requests
    return concurrency, delay


class Downloader(object):
    DOWNLOAD_SLOT = 'download_slot'

    def __init__(self, crawler):
        self.loop = crawler.loop
        self.settings = crawler.settings
        self.slots = {}
        self.active = set()
        # self.handler = DownloadHandler(crawler)
        down_handler = load_object(self.settings.get('DOWNLOAD_HANDLER'))
        self.handler = down_handler if down_handler else DownloadHandler
        self.handler = self.handler(crawler)
        self.total_concurrency = self.settings.getint('CONCURRENT_REQUESTS')
        self.domain_concurrency = self.settings.getint('CONCURRENT_REQUESTS_PER_DOMAIN')
        self.ip_concurrency = self.settings.getint('CONCURRENT_REQUESTS_PER_IP')
        self.randomize_delay = self.settings.getbool('RANDOMIZE_DOWNLOAD_DELAY')
        self.middleware = DownloaderMiddlewareManager.from_crawler(crawler)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    async def fetch(self, request, spider):
        self.active.add(request)
        response = await self.middleware.download(self._download, request, spider)  # 执行下载中间件 请求到响应
        self.active.remove(request)
        return response

    def _get_slot(self, request, spider):
        key = self._get_slot_key(request, spider)
        if key not in self.slots:
            conc = self.ip_concurrency if self.ip_concurrency else self.domain_concurrency
            conc, delay = _get_concurrency_delay(conc, spider, self.settings)
            self.slots[key] = Slot(conc, delay, self.randomize_delay)
        return key, self.slots[key]

    def _get_slot_key(self, request, spider):
        if self.DOWNLOAD_SLOT in request.meta:
            return request.meta[self.DOWNLOAD_SLOT]

        key = urlparse_cached(request).hostname or ''
        if self.ip_concurrency:
            key = dnscache.get(key, key)
        return key

    async def _enqueue_request(self, request, spider):
        key, slot = self._get_slot(request, spider)
        request.meta[self.DOWNLOAD_SLOT] = key
        return await self._download(request)

    async def _download(self, request):
        return await self.handler.fetch(request)

    async def close(self):
        await self.handler.close()
