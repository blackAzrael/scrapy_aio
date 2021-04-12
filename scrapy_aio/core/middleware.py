# -*- coding:utf-8 -*-
import asyncio
from collections import defaultdict, deque

from scrapy_aio.exceptions import NotConfigured
from scrapy_aio.utils.misc import load_object, create_instance


class MiddlewareManager(object):
    """Base class for implementing middleware managers"""

    component_name = 'root middleware'

    def __init__(self, *middlewares):
        self.middlewares = middlewares
        self.methods = defaultdict(deque)
        for mw in middlewares:
            self._add_middleware(mw)

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        raise NotImplementedError

    @classmethod
    def from_settings(cls, settings, crawler=None):
        mwlist = cls._get_mwlist_from_settings(settings)
        middlewares = []
        enabled = []
        for clspath in mwlist:
            try:
                mwcls = load_object(clspath)
                mw = create_instance(mwcls, settings, crawler)
                middlewares.append(mw)
                enabled.append(clspath)
            except NotConfigured as e:
                pass
        return cls(*middlewares)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings, crawler)

    def _add_middleware(self, mw):
        if hasattr(mw, 'open_spider'):
            self.methods['open_spider'].append(mw.open_spider)
        if hasattr(mw, 'close_spider'):
            self.methods['close_spider'].appendleft(mw.close_spider)

    async def _process_parallel(self, methodname, obj, *args):
        """
        并行执行所有方法
        :param methodname:
        :param obj:
        :param args:
        :return:
        """
        coros = [method(obj, *args) for method in self.methods[methodname]]
        return await asyncio.gather(*coros)

    async def _process_chain(self, methodname, obj, *args):
        """
        顺序执行所有方法
        :param methodname:
        :param obj:
        :param args:
        :return:
        """
        for method in self.methods[methodname]:
            await method(obj, *args)

    async def open_spider(self, spider):
        return await self._process_chain('open_spider', spider)

    async def close_spider(self, spider):
        return await self._process_chain('close_spider', spider)
