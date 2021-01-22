# -*- coding:utf-8 -*-
import base64
import os

from motor.motor_asyncio import AsyncIOMotorClient
from scrapy3.log_handler import LogHandler

logger = LogHandler(__name__)


class DefaultPipelines(object):
    name = 'default pipeline'

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    async def open_spider(self, spider):
        logger.info("加载默认管道")
        pass

    async def close_spider(self, spider):
        # print("close spider 00000")
        pass

    async def process_item(self, item, spider):
        # logger.debug(f"{self.name}, '管道结果', {item}")
        pass


class ImageSavePipelines(object):
    name = '图片保存 pipeline'

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    async def open_spider(self, spider):
        logger.info("加载默认管道")
        pass

    async def close_spider(self, spider):
        # print("close spider 00000")
        pass

    async def process_item(self, item, spider):
        logger.debug(f"{item['name']}")
        logger.warning(f"{self.name}, '管道结果'")
        await self.save_images(item)

    async def save_images(self,item):
        now_path = os.getcwd()
        file_name = now_path + "/bing/images/" + item['name'] + ".jpeg"
        file = open(file_name, 'wb')
        file.write(item['data'])
        file.close()
        return file_name