# -*- coding:utf-8 -*-
import base64
import os

from motor.motor_asyncio import AsyncIOMotorClient
from scrapy_aio.log_handler import LogHandler

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

    def __init__(self):
        self.dir_name = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    async def open_spider(self, spider):
        now_path = os.getcwd()
        self.dir_name = now_path + "/bing/images/"
        if not os.path.exists(self.dir_name):
            logger.debug(f"创建目录{self.dir_name}")
            os.makedirs(self.dir_name)


    async def close_spider(self, spider):
        pass

    async def process_item(self, item, spider):
        # logger.debug(f"{item['name']}")
        await self.save_images(item)
        logger.warning(f"{item['name']}, '保存成功'")

    async def save_images(self,item):
        file_name = self.dir_name + item['name'] + ".jpeg"
        file = open(file_name, 'wb')
        file.write(item['data'])
        file.close()
        return file_name