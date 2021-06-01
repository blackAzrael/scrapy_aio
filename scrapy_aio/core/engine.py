# -*- coding:utf-8 -*-
import asyncio
from time import time
from typing import Iterable

from scrapy_aio.log_handler import LogHandler
from scrapy_aio.core.scraper import Scraper
from scrapy_aio.http import Request
from scrapy_aio.utils.misc import load_object

# logger = logging.getLogger(__name__)

logger = LogHandler("engine")
logger.setLevel("DEBUG")


class CallLaterOnce(object):

    def __init__(self, func, loop=None, *args, **kwargs):
        self._func = func
        self.args = args
        self.kwargs = kwargs
        self.canced = False
        self.loop = loop

    async def schedule(self):
        if not self.canced:
            await self._func(*self.args, **self.kwargs)

    def cancel(self):
        self.canced = True


class Slot(object):
    def __init__(self, start_requests, close_if_idle, nextcall, scheduler):
        self.closing = False
        self.inprogress = set()
        self.start_requests = iter(start_requests)
        self.close_if_idle = close_if_idle
        self.nextcall = nextcall
        self.scheduler = scheduler

    async def close(self):
        self.closing = True
        if self.closing:
            if self.nextcall:
                self.nextcall.cancel()


class Engine(object):

    def __init__(self, crawler, loop=None):
        self.settings = crawler.settings
        self.crawler = crawler
        self.logformatter = crawler.logformatter
        self.loop = loop
        self.slot = None
        self.spider = None
        self.running = False
        self.paused = False
        self.max_pool = self.settings['MAX_POOL'] or 20
        self.scheduler_cls = load_object(self.settings['SCHEDULER'])
        self.downloader_cls = load_object(self.settings['DOWNLOADER'])
        self.downloader = self.downloader_cls.from_crawler(crawler)
        self.scraper = Scraper(crawler)

    def _loader_spider(self):
        self.spider = self.crawler.spider

    async def open_spider(self, spider, start_requests=(), close_if_idle=True):
        logger.info('spider opened', extra={'spider': spider})
        nextcall = CallLaterOnce(self._next_request, self.loop, spider)
        scheduler = self.scheduler_cls.from_crawler(self.crawler)
        slot = Slot(start_requests, close_if_idle, nextcall, scheduler)
        self.slot = slot
        self.spider = spider
        await scheduler.open_spider(spider)
        await self.scraper.open_spider(spider)

    async def start(self):
        await self._start()

    async def _start(self):

        logger.info("engine start")
        self.start_time = time()
        self.running = True
        routines = [self.slot.nextcall.schedule()]
        await asyncio.gather(*routines)

    async def stop(self):
        assert self.running, 'Engine not running'
        self.running = False
        await self._close_all_spiders()

    async def close(self):
        if self.running:
            await self.stop()
        elif self.open_spiders:
            await self._close_all_spiders()
        else:
            self.downloader.close()

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    @property
    def open_spiders(self):
        return [self.spider] if self.spider else []

    async def _close_all_spiders(self):
        await self.close_spider(self.spider, reason='finished')

    async def _get_result(self, request, spider, semaphore):

        response = await self.download(request, spider)  # 获得下载器响应
        await self._handle_downloader_output(response, request, spider)  # 将响应输入到下载中间件
        semaphore.release()  # 释放信号量，使内部计数器增加一。可以唤醒等待获取信号量的任务。
        # logger.info(semaphore._value)

    async def get_result(self, spider):
        '''
        使用信号量控制
        :param spider:
        :return:
        '''
        slot = self.slot
        # logger.debug("into get_result crawl ")
        # 信号量 控制同时进行的协程个数
        semaphore = asyncio.Semaphore(value=self.max_pool)
        # logger.info(self.max_pool)
        while True:
            request = await slot.scheduler.next_request()  # 获取下一个request请求
            # logger.info(request)
            if request:
                await semaphore.acquire()  # 如果内部计数器大于零，则将其递减一并True立即返回。如果为零，请等待直到release()调用a并返回
                # logger.info(semaphore._value)
                # await asyncio.sleep(1)
                self.loop.create_task(self._get_result(request, spider, semaphore))
            else:
                await asyncio.sleep(1)
                break

    async def _next_request(self, spider):
        logger.debug("into _next_request ")
        while True and not self.slot.closing:
            slot = self.slot
            await self.get_result(spider)
            try:
                # request = next(slot.start_requests)
                for req in slot.start_requests:
                    if req.__class__.__name__ == "async_generator":
                        async for r in req:
                            if asyncio.iscoroutine(r):
                                r = await r
                            await self.crawl(r, spider)
                        continue
                    if asyncio.iscoroutine(req):
                        req = await req
                    await self.crawl(req, spider)
            except StopIteration:
                slot.start_requests = []
            except Exception as e:
                logger.exception(e)
            ret = await self._spider_idle(spider)
            if ret:
                return
            logger.info("等待任务")
            await asyncio.sleep(0.5)
        # await slot.nextcall.schedule()

    async def crawl(self, request, spider):
        if isinstance(request, Iterable):
            logger.debug("request 是迭代器")
            # logger.info(request)
            for req in request:
                if not req:
                    continue
                logger.debug(req)
                await self.slot.scheduler.enqueue_request(req)
        else:
            await self.slot.scheduler.enqueue_request(request)

    async def download(self, request, spider):
        task = asyncio.ensure_future(self.downloader.fetch(request, spider))
        return await task

    async def _handle_downloader_output(self, response, request, spider):
        if isinstance(response, Request):
            await self.crawl(response, spider)
            return
        await self.scraper.enqueue_scrape(response, request, spider)

    async def spider_is_idle(self, spider):
        '''
        判断spider 是否可以结束
        :param spider:
        :return: 返回false 说明还未结束
        '''
        # logger.info(f"scraper.active {len(self.scraper.active) }")
        # logger.info(f"downloader.active len {len(self.downloader.active) }")
        if self.downloader.active:
            # 进入这里说明 还有正在下载的任务 从request 队列已经取不到任务
            await asyncio.sleep(1)
            logger.debug(f"downloader.active {self.downloader.active}")
            # if not await self.spider.spider_idle():
            #     #  取出start_url
            #     #  scheduler是否停止 若没有结束scheduler继续取出任务 如果是redis_spider 从redis里面取
            #     return False
            return False
        if self.slot.scheduler.has_pending_requests():
            # 待下载队列不为空
            logger.debug(f"self.slot.scheduler.has_pending_requests() {self.slot.scheduler.has_pending_requests()}")
            return False
        if len(self.scraper.active):
            # scraper 是否停止  判断SPIDER_MIDDLEWARES中间件是否还有正在处理的函数
            logger.debug(self.scraper.active)
            return False

        if not await self.spider.spider_idle():
            #  取出start_url
            #  scheduler是否停止 是否还拿得到URL
            return False

        logger.info("关闭爬虫")
        return True

    async def _spider_idle(self, spider):
        if await self.spider_is_idle(spider):
            await self.close_spider(spider, reason='finished')
            return True

    async def close_spider(self, spider, reason='cancelled'):
        slot = self.slot
        if slot.closing:
            return
        # await asyncio.sleep(5)
        logger.info("Closing spider (%(reason)s)",
                    {'reason': reason},
                    extra={'spider': spider})

        await slot.close()
        logger.info("close engine slot")
        await self.downloader.close()
        logger.info("close engine downloader")
        await self.scraper.close_spider(spider)
        logger.info("close engine scraper")
        await slot.scheduler.close(reason)
        logger.info("close engine scheduler")
        spider.close(spider, reason)
        logger.info("close engine spider")
