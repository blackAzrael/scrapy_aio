# from scrapy_aio import spiders, signals
# from scrapy.exceptions import DontCloseSpider

from scrapy_aio.spiders import Spider
from . import connection
from scrapy_aio.log_handler import LogHandler
from .utils import bytes_to_str
import asyncio

logger = log = LogHandler(__name__)


class RedisMixin(object):
    """Mixin class to implement reading urls from a redis queue."""
    redis_key = None  # use default '<spider>:start_urls'
    MAX_TIMES = 60
    try_max_times = MAX_TIMES  # 分钟
    def start_requests(self):
        """Returns a batch of start requests from redis."""
        # logger.debug("into start_requests")
        yield self.next_request()

    def setup_redis(self):
        """Setup redis connection and idle signal.

        This should be called after the spider has set its crawler object.
        """
        if not self.redis_key:
            self.redis_key = '%s:start_urls' % self.name

        logger.debug("初始化redis")
        logger.debug(self.redis_key)
        self.server = connection.from_settings(self.crawler.settings)
        self.fetch_data = self.pop_list_queue
        # 每次从%s:start_urls 里面取多少个URL 到request_url 队列里面
        self.redis_batch_size = 50
        # idle signal is called when the spider has no requests left,
        # that's when we will schedule new requests from redis queue
        # self.crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)
        # self.crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)
        # self.log("Reading URLs from redis list '%s'" % self.redis_key)
        logger.debug("Reading URLs from redis list '%s'" % self.redis_key)

    def pop_list_queue(self, redis_key, batch_size):
        with self.server.pipeline() as pipe:
            pipe.lrange(redis_key, 0, batch_size - 1)
            pipe.ltrim(redis_key, batch_size, -1)
            datas, _ = pipe.execute()
        return datas

    async def next_request(self):
        """Returns a request to be scheduled or none."""
        # logger.debug("into next_request")
        found = 0
        datas = self.fetch_data(self.redis_key, self.redis_batch_size)
        # logger.debug(datas)
        if datas:
            self.try_max_times = self.MAX_TIMES
        for data in datas:
            req = self.make_request_from_data(data)
            if req:
                yield req
            else:
                logger.debug("Request not made from data: %r", data)
            # url = self.server.lpop(self.redis_key)
        # if url:
        #     yield self.make_request_from_data(url)


    def make_request_from_data(self, data):
        """Returns a Request instance from data coming from Redis.
        By default, ``data`` is an encoded URL. You can override this method to
        provide your own message decoding.
        Parameters
        ----------
        data : bytes
            Message from redis.
        """
        url = bytes_to_str(data, "utf-8")
        return self.make_requests_from_url(url)

    async def schedule_next_request(self):
        """Schedules a request if available"""
        # req = self.next_request()
        # logger.debug(req)

        async for req in self.next_request():
            if asyncio.iscoroutine(req):
                req = await req
            await self.crawler.engine.crawl(req, spider=self)

    async def spider_idle(self):

        """Schedules a request if available, otherwise waits."""
        # time.sleep(10)
        llen = self.server.llen(self.redis_key)
        logger.debug(f"len {llen}")
        if llen == 0:
            logger.debug("线程空闲")
            self.try_max_times -= 1
            await asyncio.sleep(5)  # 等待60秒
        await self.schedule_next_request()
        if self.try_max_times <= 1:
            logger.info("redis spider 结束进程")
            return True
        # raise DontCloseSpider
        return False

    def item_scraped(self, *args, **kwargs):
        """Avoids waiting for the spider to  idle before scheduling the next request
            避免在调度下一个请求之前等待爬行器空闲
        """
        self.schedule_next_request()


class RedisSpider(RedisMixin, Spider):
    """Spider that reads urls from redis queue when idle."""

    def _set_crawler(self, crawler):
        super(RedisSpider, self)._set_crawler(crawler)
        self.setup_redis()
