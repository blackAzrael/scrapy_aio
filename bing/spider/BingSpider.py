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
from urllib.parse import urljoin

now_path = os.getcwd()
root_path = now_path.split("scrapy3")[0] + "/scrapy3"
os.chdir(root_path)
sys.path.append(root_path)
from bing import settings
from scrapy3.conf.settings import Settings
from scrapy3.core.crawler import Crawler
from scrapy3.http.request import Request
from scrapy3.spiders import Spider
from scrapy3.log_handler import LogHandler
from lxml import etree

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
    name = 'bing'

    def start_requests(self):

        yield Request(url='https://bing.ioliu.cn/', dont_filter=True, callback=self.parse)

    async def parse(self, response):
        if response.status != 200:
            logger.debug(response.status)
            return
        # logger.debug(response.status)
        # logger.debug(response.text)
        # selector = etree.HTML(response.text)
        # max_page_div = selector.xpath("//div[@class='page']/span/text()")[0]
        # # 获取最大页面数
        # max_page = max_page_div.strip().split("/")[1]
        # max_page = int(max_page)
        # logger.debug(f"max_page:{max_page}")
        max_page = 20
        for x in range(max_page):
            yield Request(url=f"https://bing.ioliu.cn/?p={x}", dont_filter=True, callback=self.parse_content)

    async def parse_content(self, response):
        # 获取页面所有的图片url
        selector = etree.HTML(response.text)
        # "//div[@class='container']/div[@class='item']/div[@class='card progressive']/a/@href"
        item = selector.xpath("//div[@class='container']/div[@class='item']")
        for i in item:
            image_url = i.xpath("div[@class='card progressive']/a/@href")[0]
            image_name = i.xpath("div/div[1]/h3/text()")[0]
            image_url = image_url.split("?")[0]
            image_url = urljoin(response.url, image_url)
            image_url = image_url + "?force=download"
            image_name = image_name.split(" ")[0]
            meta = {
                "image_name": image_name
            }
            yield Request(url=image_url, dont_filter=True, meta=meta, callback=self.img_download)

    async def img_download(self, response):
        # 获取图片内容
        image_item = {}
        image_item['url'] = response.url
        image_item['data'] = response.body
        image_item['name'] = response.meta.get("image_name")
        logger.warning(response.url)
        yield image_item


async def start():
    await crawler.crawl()
    await crawler.start()


if __name__ == '__main__':
    s = Settings()
    s.setmodule(settings)
    crawler = Crawler(ComSpider, s, loop)
    loop.run_until_complete(start())
    loop.close()
