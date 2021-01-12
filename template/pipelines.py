# -*- coding:utf-8 -*-
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
        print("close spider 00000")
        pass

    async def process_item(self, item, spider):
        # logger.debug(f"{self.name}, '管道结果', {item}")
        pass


class DefaultPipelines1(object):
    name = 'default pipeline'

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    async def open_spider(self, spider):
        pass

    async def close_spider(self, spider):
        pass

    async def process_item(self, item, spider):
        pass
        # print(self.name, 'process_item', item)


class MongoDBPipeline:
    name = 'mongo pipeline'

    # 连接数据库
    async def open_spider(self, spider):
        client = AsyncIOMotorClient(host=spider.settings.get('MONGO_HOST'),
                                    port=spider.settings.get('MONGO_PORT'))
        self.db = client[spider.settings.get('MONGO_DB')]  # 获得数据库的句柄
        self.coll = self.db[spider.settings.get('MONGO_COLL')]  # 获得collection的句柄
        self.coll.create_index("url")  # 对url创建索引
        # 数据库登录需要帐号密码的话
        # self.db.authenticate(db_params('MONGO_USER'), db_params('MONGO_PSW'))
        logger.info("加载 MongoDB")

    async def process_item(self, item, spider):
        await self.insert_db(item)
        return item

    async def insert_db(self, item):
        _item = {}
        for key in item:
            _item[key] = item[key]
        # _item['web_type'] = json.dumps(_item['web_type'],ensure_ascii=False)
        res = await self.coll.find_one_and_update({"url": _item["url"]}, {"$set": _item})
        if not res:
            # logger.info(f"mongo 更新 {item['url']}")
            await self.coll.insert_one(_item)
        else:
            logger.info(f"mongo 插入 {item['url']}")
        # logger.info("存入MongoDB")
        # logger.info(_item)


class MongoDBPipelineAsyncio:
    name = 'mongo asyncio pipeline'

    # 连接数据库
    async def open_spider(self, spider):
        client = AsyncIOMotorClient(host=spider.settings.get('MONGO_HOST'),
                                    port=spider.settings.get('MONGO_PORT'))
        self.db = client[spider.settings.get('MONGO_DB')]  # 获得数据库的句柄
        self.coll = self.db[spider.settings.get('MONGO_COLL')]  # 获得collection的句柄
        self.coll.create_index("start_url")  # 对url创建索引
        # 数据库登录需要帐号密码的话
        # self.db.authenticate(db_params('MONGO_USER'), db_params('MONGO_PSW'))

    async def process_item(self, item, spider):
        await self.insert_db(item)
        return item

    async def insert_db(self, item):
        _item = {}
        for key in item:
            _item[key] = item[key]
        res = await self.coll.find_one_and_update({"url": _item["url"]}, {"$set": _item})
        if not res:
            # logger.info(f"mongo 更新 {item['url']}")
            await self.coll.insert_one(_item)
        else:
            logger.info(f"mongo 插入 {item['url']}")


class MongoDBPipelineAsyncioIllgal:
    name = 'mongo asyncio pipeline'

    # 连接数据库
    async def open_spider(self, spider):
        client = AsyncIOMotorClient(host=spider.settings.get('MONGO_HOST'),
                                    port=spider.settings.get('MONGO_PORT'))
        self.db = client[spider.settings.get('MONGO_DB')]  # 获得数据库的句柄
        self.coll = self.db[spider.settings.get('MONGO_COLL')]  # 获得collection的句柄
        self.coll.create_index("start_url")  # 对url创建索引
        # 数据库登录需要帐号密码的话
        # self.db.authenticate(db_params('MONGO_USER'), db_params('MONGO_PSW'))

    async def process_item(self, item, spider):
        await self.insert_db(item)
        # logger.debug(item['url'])
        return item

    async def insert_db(self, item):
        _item = {}
        for key in item:
            _item[key] = item[key]
        await self.coll.insert_one(_item)


