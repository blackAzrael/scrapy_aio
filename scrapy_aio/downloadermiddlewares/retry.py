# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     retry
   Description :
   Author :       dean
   date：          2020/7/24 10:03
-------------------------------------------------
   Change Activity:
                   10:03
-------------------------------------------------
"""
import asyncio
import logging

import aiohttp

from scrapy_aio.http import Response
logger = logging.getLogger(__name__)


class RetrayMiddleware(object):
    ''':cvar 异常处理中间件'''
    TIMEOUT_EXCEPTIONS = (aiohttp.ServerTimeoutError,aiohttp.ClientTimeout,
                          asyncio.TimeoutError
                      )

    def __init__(self, settings):
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):

        if response.status in self.retry_http_codes:
            return self._retry(request,spider,response.status)
        return response

    def process_exception(self, request, exception, spider):
        # 捕获超时异常
        if isinstance(exception, self.TIMEOUT_EXCEPTIONS):
            # 在日志中打印异常类型
            # RETRY_TIMES
            return self._retry(request,spider,'超时')


    def _retry(self,request,spider,info):
        # RETRY_TIMES = spider.crawler.settings.getint(name="RETRY_TIMES")
        # print(f"RETRY_TIMES:{RETRY_TIMES}")
        # print(f"request.retry_times:{request.retry_times}")
        if request.meta.get('dont_retry', False):
            return Response(url=f'599 time out {request.url}', status=599)
        retries = request.meta.get('retry_times', 0) + 1
        if retries < self.max_retry_times:

            retryreq = request.copy()
            retryreq.priority = request.priority + self.priority_adjust
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            logger.info(f"{info}: retry {retries} {request}")
        else:
            # 随意封装一个response，返回给spider
            retryreq = Response(url=f'599 time out {request.url}', status=599)
        return retryreq