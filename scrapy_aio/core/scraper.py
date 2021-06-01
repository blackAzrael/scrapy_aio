# -*- coding:utf-8 -*-
import asyncio
import threading

from scrapy_aio.core.spidermw import SpiderMiddlewareManager
from scrapy_aio.http import Request
from scrapy_aio.item import BaseItem
from scrapy_aio.utils.misc import load_object
from scrapy_aio.utils.python import get_result_list

from scrapy_aio.log_handler import LogHandler

logger = log = LogHandler(__name__)


class Slot(object):
    def __init__(self):
        self.req_all_num = 0
        self.itm_all_num = 0
        self.req_last_num = 0
        self.itm_last_num = 0
        self.interval = 60.0
        self.multiplier = 60.0 / self.interval
        self.active = True
        self.run = True

    async def is_idle(self):
        if not self.run:
            return
        self.active = False
        await asyncio.sleep(self.interval)
        self.new_loop.stop()
        return self.active

    async def log_status(self):
        while self.active:
            await asyncio.sleep(self.interval)
            riate = int((self.req_all_num - self.req_last_num))
            iiate = int((self.itm_all_num - self.itm_last_num))
            logger.info(f"完成请求总数{self.req_all_num} 平均每分钟完成数目{riate}  "
                        f"完成item总数{self.itm_all_num} 平均每分钟完成数目{iiate}")
            self.req_last_num = self.req_all_num
            self.itm_last_num = self.itm_all_num

    def start_log_loop(self, new_loop):
        logger.info("into start_log_loop")
        asyncio.set_event_loop(new_loop)
        new_loop.run_forever()

    async def log_start(self):
        if not self.run:
            return
        coroutine = self.log_status()
        self.new_loop = asyncio.new_event_loop()  # 在当前线程下创建时间循环，（未启用），在start_loop里面启动它
        self.t = threading.Thread(target=self.start_log_loop, args=(self.new_loop,))  # 通过当前线程开启新的线程去启动事件循环
        self.t.setDaemon(True)
        self.t.start()
        self.coro = asyncio.run_coroutine_threadsafe(coroutine, self.new_loop)  # 这几个是关键，代表在新线程中事件循环不断“游走”执行


class Scraper(object):

    def __init__(self, crawler):
        self.crawler = crawler
        itemproc_cls = load_object(crawler.settings['ITEM_PROCESSOR'])
        self.itemproc = itemproc_cls.from_crawler(crawler)
        self.concurrent_items = crawler.settings.getint('CONCURRENT_ITEMS')
        self.spidermw = SpiderMiddlewareManager.from_crawler(crawler)
        self.active = set()
        self.slot = Slot()
        self.slot.run = crawler.settings.getbool('SCRAPY_COUNT', True)  # 默认开启爬虫计数统计

    async def open_spider(self, spider):
        await self.slot.log_start()
        await self.itemproc.open_spider(spider)

    async def close_spider(self, spider):
        await self.itemproc.close_spider(spider)
        await self.slot.is_idle()
        logger.info("关闭scraper 成功")

    async def enqueue_scrape(self, response, request, spider):
        self.active.add(response)
        self.slot.req_all_num += 1
        # logger.info("开始处理 scrape")
        response.request = request
        try:
            # await self._scrape(response, request, spider)
            await asyncio.wait_for(self._scrape(response, request, spider), 10 * 60.0)
        # logger.info("处理结束 scrape")
        except Exception as e:
            logger.exception(e)
        finally:
            self.active.remove(response)

    async def _scrape(self, response, request, spider):
        """
        spider中间件
        处理下载器来的response 到spider 在到scheduler
        :param response:
        :param request:
        :param spider:
        :return:
        """
        if not response:
            return
        callback = request.callback or spider.parse
        result = await self.spidermw.scrape_response(callback, response, request, spider)

        if asyncio.iscoroutinefunction(result) or asyncio.iscoroutine(result):
            result = await result
        # logger.debug(type(result))
        # logger.debug(response)
        ret = await get_result_list(result)
        await self.handle_spider_output(ret, request, response, spider)

    async def handle_spider_output(self, result, request, response, spider):

        for each in result:
            if each is None:
                continue
            elif isinstance(each, Request):
                # logger.info(each)
                await self.crawler.engine.crawl(each, spider)
            elif isinstance(each, (BaseItem, dict)):
                await self.itemproc.process_item(each, spider)
                self.slot.itm_all_num += 1

            else:
                pass
