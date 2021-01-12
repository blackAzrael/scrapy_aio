# -*- coding:utf-8 -*-
"""
Downloader Middleware manager
"""
import asyncio

from scrapy3.core.middleware import MiddlewareManager
from scrapy3.http import Request, Response
from scrapy3.utils.conf import build_component_list
from scrapy3.utils.misc import call_func


class DownloaderMiddlewareManager(MiddlewareManager):

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        return build_component_list(settings.getwithbase('DOWNLOADER_MIDDLEWARES'))

    def _add_middleware(self, miw):
        if hasattr(miw, "process_request"):
            self.methods['process_request'].append(miw.process_request)
        if hasattr(miw, "process_response"):
            self.methods['process_response'].append(miw.process_response)
        if hasattr(miw, "process_exception"):
            self.methods['process_exception'].append(miw.process_exception)

    async def download(self, download_func, request, spider):
        async def process_request(request):
            for method in self.methods['process_request']:
                ret = method(request, spider)
                if asyncio.iscoroutine(ret):
                    ret = await ret
                if isinstance(ret, Request):
                    request = ret
                if isinstance(ret, Response):
                    return ret
            task = asyncio.ensure_future(download_func(request))
            return await task

        async def process_response(response):
            for method in self.methods["process_response"]:
                ret = method(request, response, spider)
                if asyncio.iscoroutine(ret):
                    ret = await ret
                if isinstance(ret, Request):
                    return ret
                if isinstance(ret, Response):
                    response = ret
            return response

        async def process_exception(exception):
            for method in self.methods['process_exception']:
                response = method(request, exception, spider)
                if asyncio.iscoroutine(response):
                    response = await response
                if response:
                    return response
            return exception

        return await call_func(process_request, process_response, process_exception, request)
