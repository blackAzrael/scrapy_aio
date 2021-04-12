# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test
   Description :
   Author :       dean
   date：          2020/7/20 14:24
-------------------------------------------------
   Change Activity:
                   14:24
-------------------------------------------------
"""
import redis

from scrapy_aio.log_handler import LogHandler
logger = log = LogHandler("test")

rconn = redis.Redis('127.0.0.1', 6379)

if __name__ == '__main__':
    logger.debug("11111111")
    logger.info("11111111")
    logger.warning("22222222")
    logger.error("22222222")