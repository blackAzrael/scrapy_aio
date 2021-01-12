# encoding=utf-8
import redis

from scrapy_redis.BloomfilterOnRedis import BloomFilter
from scrapy3.utils.request import request_fingerprint
from scrapy3.http import Request

rconn = redis.Redis('127.0.0.1', 6379)

bf = BloomFilter(rconn, 'spider_111:dupefilter',3)


if __name__ == '__main__':
    # while True:
        url = 'http://testphp.vulnweb.com/comment.php?aid=N'
        request = Request(url)
        print(request)
        fp = request_fingerprint(request)
        # print(fp)
        # bf.insert(fp)
        if bf.isContains(fp):
            print('exist!')
        else:
            print('not exist!')

    # list_key = rconn.keys('spider_111*')
    # print(list_key)
    # rconn.delete(*list_key)
