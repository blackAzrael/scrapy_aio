# -*- coding:utf-8 -*-
"""
use aiohttp wrap download handler
"""
import asyncio
import random
import time

import cchardet
import aiohttp
from aiohttp.client import ClientTimeout

from scrapy3.http import Response


class DownloadHandler2(object):

    def __init__(self, crawler):
        self.settings = crawler.settings
        self.loop = crawler.loop
        self.timeout = self.settings.getint('DOWNLOAD_TIMEOUT')
        self.conn = self._create_connector(self.settings)

    def _create_connector(self, settings):
        conn = aiohttp.ClientSession(loop=self.loop)
        # self.resolver = aiodns.DNSResolver(loop=self.loop)
        return conn

    async def fetch(self,request):
        download_timeout = self.timeout
        resp = await asyncio.wait_for(self._fetch(request), download_timeout+1)
        return resp

    async def _fetch(self, request):
        # print(request)
        proxy = request.meta.get("proxy")
        download_timeout = request.meta.get('download_timeout') or self.timeout
        timeout = ClientTimeout(total=download_timeout)
        async with self.conn.request(
                method=request.method,
                url=request.url,
                params=request.params,
                data=request.data,
                headers=request.headers,
                json=request.json,
                timeout=timeout, proxy=proxy
        ) as resp:
            body = await resp.read()
            headers = resp.headers
            encoding = cchardet.detect(body)['encoding']
            response = Response(request.url, status=resp.status, headers=headers, body=body, request=request,
                                encoding=encoding)
            return response

    async def close(self):
        await self.conn.close()


class DownloadHandler1(object):

    def __init__(self, crawler):
        self.settings = crawler.settings
        self.loop = crawler.loop
        self.timeout = self.settings.getint('DOWNLOAD_TIMEOUT')
        self.conn = self._create_connector(self.settings)

    def _create_connector(self, settings):
        conn = aiohttp.ClientSession(loop=self.loop)
        return conn

    async def fetch(self, request):
        proxy = request.meta.get("proxy")
        download_timeout = request.meta.get('download_timeout') or self.timeout
        timeout = ClientTimeout(total=download_timeout)
        async with aiohttp.ClientSession() as client:
            start_time = time.time()
            async with client.request(
                    method=request.method,
                    url=request.url,
                    params=request.params,
                    cookies=request.cookies,
                    data=request.data,
                    headers=request.headers,
                    json=request.json,
                    timeout=timeout,
                    proxy=proxy,
                    verify_ssl=False
            ) as resp:
                body = await resp.read()
                headers = resp.headers
                encoding = cchardet.detect(body)['encoding']

                response = Response(request.url, status=resp.status, headers=headers,
                                    body=body, request=request, encoding=encoding, resp=resp)
                response.time = time.time() - start_time
                return response

    async def close(self):
        await self.conn.close()


class DownloadHandler(object):

    def __init__(self, crawler):
        self.settings = crawler.settings
        self.loop = crawler.loop
        self.timeout = self.settings.getint('DOWNLOAD_TIMEOUT')
        self.conn = self._create_connector(self.settings)

    def _create_connector(self, settings):
        # limit = settings.getint('CONCURRENT_REQUESTS')
        limit = settings.getint('CONCURRENT_REQUESTS') + settings.getint('MAX_POOL')
        use_dns_cache = settings.getbool('DNSCACHE_ENABLED')
        ttl_dns_cache = settings.getint('DNS_TIMEOUT')
        conn = aiohttp.TCPConnector(limit=limit, use_dns_cache=use_dns_cache, ttl_dns_cache=ttl_dns_cache,
                                    force_close=True, loop=self.loop, verify_ssl=False)
        return conn

    async def fetch(self,request):
        download_timeout = request.meta.get('download_timeout') or self.timeout
        resp = await asyncio.wait_for(self._fetch(request), download_timeout+5)
        return resp

    async def _fetch(self, request):
        proxy = request.meta.get("proxy")
        download_timeout = request.meta.get('download_timeout') or self.timeout
        timeout = ClientTimeout(total=download_timeout)
        start_time = time.time()
        async with aiohttp.request(method=request.method,
                                   url=request.url,
                                   cookies=request.cookies,
                                   params=request.params,
                                   data=request.data,
                                   headers=request.headers,
                                   json=request.json,
                                   allow_redirects=request.allow_redirects,
                                   timeout=timeout, proxy=proxy, connector=self.conn, loop=self.loop) as resp:
            body = await resp.read()
            headers = resp.headers
            encoding = cchardet.detect(body)['encoding']
            response = Response(request.url, status=resp.status, headers=headers,
                                body=body, request=request, encoding=encoding, resp=resp)
            response.time = time.time() - start_time
            return response

    async def close(self):
        await self.conn.close()
