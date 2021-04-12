# -*- coding:utf-8 -*-
import asyncio

from scrapy_aio.utils.misc import load_object, create_instance


class Scheduler(object):

    def __init__(self, dupefilter, pqclass=None):
        self.df = dupefilter
        self.queue = pqclass()

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        dupefilter_cls = load_object(settings['DUPEFILTER_CLASS'])
        dupefilter = create_instance(dupefilter_cls, settings, crawler)
        pqclass = load_object(settings['SCHEDULER_PRIORITY_QUEUE'])
        return cls(dupefilter, pqclass)

    async def open_spider(self, spider):
        self.df.open(spider)

    async def enqueue_request(self, request):

        # 如果过滤请求加入请求队列
        # print(f"队列大小{self.queue.qsize} ")
        # print(f"队列大小{self.queue.qsize()} ")
        if not request.dont_filter:
            # 如果请求不在过滤器加入请求队列
            if not await self.df.request_seen(request):
                if isinstance(self.queue,asyncio.queues.PriorityQueue):
                    await self.queue.put(-request.priority,request)
                else:
                    await self.queue.put(request)
        else:
            await self.queue.put(request)


    async def next_request(self):
        if self.queue.empty():
            return None
        # print(f"队列大小{self.queue.qsize()} ")
        return await self.queue.get()

    def __len__(self):
        return self.queue.qsize()

    def has_pending_requests(self):
        return len(self) > 0

    async def close(self, reason):
        self.df.close(reason)
