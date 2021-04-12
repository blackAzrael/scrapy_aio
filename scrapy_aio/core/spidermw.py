# -*- coding:utf-8 -*-
import asyncio
import logging
from collections import Iterable
from itertools import chain

from scrapy_aio.core.middleware import MiddlewareManager
from scrapy_aio.http import Response, Request
from scrapy_aio.utils.conf import build_component_list
from scrapy_aio.utils.misc import call_func_spider_mw

logger = logging.getLogger(__name__)


def _isiterable(possible_iterator):
    return hasattr(possible_iterator, '__iter__')


class SpiderMiddlewareManager(MiddlewareManager):
    component_name = 'spider middleware'

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        return build_component_list(settings.getwithbase('SPIDER_MIDDLEWARES'))

    def _add_middleware(self, mw):
        super(SpiderMiddlewareManager, self)._add_middleware(mw)
        if hasattr(mw, 'process_spider_input'):
            self.methods['process_spider_input'].append(mw.process_spider_input)
        if hasattr(mw, 'process_start_requests'):
            self.methods['process_start_requests'].appendleft(mw.process_start_requests)
        self.methods['process_spider_output'].appendleft(getattr(mw, 'process_spider_output', None))
        self.methods['process_spider_exception'].appendleft(getattr(mw, 'process_spider_exception', None))

    async def scrape_response(self, scrape_func, response, request, spider):
        fname = lambda f: '%s.%s' % (
            f.__self__.__class__.__name__,
            f.__func__.__name__)

        async def process_spider_input(response, request, spider):
            """
            输出到spider
            :param response:
            :return:
            """
            for method in self.methods['process_spider_input']:
                ret = method(request, response, spider)
                if asyncio.iscoroutine(ret):
                    ret = await ret
                if isinstance(ret, Response):
                    response = ret

            return scrape_func(response)

        async def process_spider_exception(exception):

            for method in self.methods['process_spider_exception']:
                response = method(exception, spider)
                if asyncio.iscoroutine(response):
                    response = await response
                if response:
                    return str(response)
            return str(exception)

        async def process_spider_output(request):
            """
            输出到scheduler
            :param result:
            :param start_index:
            :return:
            """
            # items in this iterable do not need to go through the process_spider_output
            # chain, they went through it already from the process_spider_exception method
            ret = None
            for method in self.methods["process_spider_output"]:
                ret = method(request, response, spider)
                if asyncio.iscoroutine(ret):
                    ret = await ret
                if not ret:
                    return ret
                if isinstance(ret, Request):
                    request = ret

            # return chain(ret, None)
            return request

        return await call_func_spider_mw(process_spider_input, process_spider_output, process_spider_exception, response=response,request = request,spider = spider)

    async def process_start_requests(self, start_requests, spider):
        return await self._process_chain('process_start_requests', start_requests, spider)
