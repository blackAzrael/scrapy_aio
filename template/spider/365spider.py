# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     365spider
   Description :
   Author :       dean
   date：          2020/7/24 17:55
-------------------------------------------------
   Change Activity:
                   17:55
-------------------------------------------------
"""
import asyncio
import platform
import os
import sys
now_path = os.getcwd()
root_path = now_path.split("scrapy3")[0]+"scrapy3"
os.chdir(root_path)
sys.path.append(root_path)
from template import settings
from scrapy3.conf.settings import Settings
from scrapy3.core.crawler import Crawler
from scrapy3.http.request import Request
from scrapy3.spiders import Spider
from scrapy3.log_handler import LogHandler

logger = log = LogHandler(__name__)

sysstr = platform.system()
if sysstr == "Windows":
    print("Call Windows tasks")
    import selectors
    selector = selectors.SelectSelector()  # New line
    loop = asyncio.SelectorEventLoop(selector)
elif sysstr == "Linux":
    print("Call Linux tasks")
    import uvloop

    loop = uvloop.new_event_loop()
else:
    loop = asyncio.get_event_loop()


class ComSpider(Spider):
    name = 'test'

    def start_requests(self):

        yield Request(url='http://youdao.com', dont_filter=True, callback=self.parse)

    async def parse(self, response):
        logger.warning(f"parse {response.meta}")
        logger.warning(f"parse {response.url}")
        for i in range(5):

            yield Request(url=f"https://www.baidu.com/", dont_filter=True, callback=self.parse_content)

    async def parse_content(self,response):
        logger.debug(response.url)

        yield {"result": response.url}


async def start():

    await crawler.crawl()
    await crawler.start()


if __name__ == '__main__':
    s = Settings()
    s.setmodule(settings)
    crawler = Crawler(ComSpider, s, loop)
    # import_plugin("template/plugin", "template.plugin")
    loop.run_until_complete(start())
    loop.close()
