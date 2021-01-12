# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     depth
   Description :
   Author :       dean
   date：          2020/7/28 16:12
-------------------------------------------------
   Change Activity:
                   16:12
-------------------------------------------------
"""
import logging

from scrapy3.http import Request, Response

logger = logging.getLogger(__name__)


class DepthMiddleware:

    def __init__(self, maxdepth, prio=1):
        self.maxdepth = maxdepth
        self.prio = prio

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        maxdepth = settings.getint('DEPTH_LIMIT')
        prio = settings.getint('DEPTH_PRIORITY')
        return cls(maxdepth, prio)

    async def process_spider_input(self,  request, response, spider):
        logger.debug(f"进入process_spider_input {response.meta}")
        if 'depth' not in response.meta:
            response.meta['depth'] = 0
        return response

    async def process_spider_output(self, request, response, spider):
        # logger.info(f"process_spider_output {request}")

        if 'depth' not in request.meta:
            request.meta['depth'] = 0
            # return request

        if isinstance(request, Request):
            depth = response.meta['depth'] + 1
            request.meta['depth'] = depth
            request.priority += depth * self.prio
            maxdepth = self.maxdepth
            if "maxdepth" in request.meta:
                maxdepth = request.meta['maxdepth']
                maxdepth = int(maxdepth)
            if maxdepth and depth >= maxdepth:
                return

        return request

    async def process_spider_exception(self, exception, spider):

        logger.exception(exception)
        return
