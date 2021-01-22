# -*- coding:utf-8 -*-
import json
import random
import socket

import aiohttp
import redis
from fake_useragent import UserAgent

from scrapy3.http import Response

from scrapy3.log_handler import LogHandler
logger = log = LogHandler(__name__)


class DefaultDownloadMiddle(object):
    name = 'default download middle'

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    async def process_request(self, request, spider):
        # print(request)
        return request

    async def process_response(self, request, response, spider):
        # print(response.url)
        return response


class ProcessAllExceptionMiddleware(object):
    ''':cvar 异常处理中间件'''
    ALL_EXCEPTIONS = (TimeoutError, aiohttp.ClientError,aiohttp.ClientPayloadError,
                      ConnectionRefusedError,aiohttp.InvalidURL,
                      IOError,aiohttp.ClientResponseError,aiohttp.WSServerHandshakeError,
                      aiohttp.ContentTypeError,aiohttp.TooManyRedirects,aiohttp.ClientConnectionError,
                      aiohttp.ClientOSError,aiohttp.ClientConnectorError, aiohttp.ClientProxyConnectionError,
                      aiohttp.ServerConnectionError,aiohttp.ClientSSLError,aiohttp.ClientConnectorSSLError,
                      aiohttp.ClientConnectorCertificateError,aiohttp.ServerDisconnectedError,
                      socket.error
                      )

    def process_response(self, request, response, spider):
        # 捕获状态码为40x/50x的response
        if str(response.status).startswith('4') or str(response.status).startswith('5'):
            # 随意封装，直接返回response，spider代码中根据url==''来处理response
            # print(response.body)
            response = Response(url=f"599 状态码：{response.status} url:{request.url}", status=599)
            return response
            # return request
        # 其他状态码不处理
        return response

    def process_exception(self, request, exception, spider):
        # 捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            # 在日志中打印异常类型
            logger.error('发现异常: %s %s' % (exception,request.url))
            # 随意封装一个response，返回给spider
            response = Response(url=f'599 exception  url:{request.url}', status=599)
            return response
        else:
            # 打印出未捕获到的异常
            logger.error('未知异常 exception: %s %s' % (exception,request.url))
            response = Response(url=f'599 未知异常 exception  url:{request.url}', status=599)
            return response



class RotateUserAgentMiddleware(object):
    ''':arg 随机请求头中间件'''

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    async def process_request(self, request, spider):
        if "http" not in request.url:
            request.url = "http://" + request.url
        ua = UserAgent().random
        request.headers.setdefault('User-Agent', ua)


# 批量对拦截到的请求进行ip更换
class ProxyMiddleware(object):

    def __init__(self):
        # self.rc = redis.StrictRedis(host="47.100.88.79",port=6379,password="627510")
        self.rc = redis.StrictRedis(host="127.0.0.1", port=6379)

    async def process_request(self, request, spider):
        proxy = await self.get_proxy()
        if not proxy:
            return
        proxy = proxy.get("proxy")
        # 对拦截到请求的url进行判断（协议头到底是http还是https）
        # request.url返回值：http://www.xxx.com
        h = request.url.split(':')[0]  # 请求的协议头
        # if h == 'https':
        #     request.meta['proxy'] = 'https://' + proxy
        # else:
        request.meta['proxy'] = 'http://' + proxy



    async def get_proxy(self):
        proxies = self.rc.hkeys("proxy_real")
        proxy = random.choice(proxies) if proxies else None
        if proxy:
            res = self.rc.hget("proxy_real", proxy)
            return json.loads(res)
        else:
            return None


