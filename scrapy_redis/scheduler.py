from scrapy_aio.utils.misc import load_object

from . import connection
from .dupefilter import RFPDupeFilter

from scrapy_aio.log_handler import LogHandler
logger = log = LogHandler("redis_scheduler")

# default values
SCHEDULER_PERSIST = False
QUEUE_KEY = '%(spider)s:requests'
QUEUE_CLASS = 'scrapy_redis.queue_redis.SpiderPriorityQueue'
DUPEFILTER_KEY = '%(spider)s:dupefilter'
IDLE_BEFORE_CLOSE = 0


class Scheduler(object):
    """Redis-based scheduler"""

    def __init__(self, server, server_filter, persist, queue_key, queue_cls, dupefilter_key, idle_before_close, queue_name):
        """Initialize scheduler.

        Parameters
        ----------
        server : Redis instance
        persist : bool
        queue_key : str
        queue_cls : queue class
        dupefilter_key : str
        idle_before_close : int
        """
        self.server = server
        self.server_filter = server_filter
        self.persist = persist
        self.queue_key = queue_key
        self.queue_cls = queue_cls
        self.dupefilter_key = dupefilter_key
        self.idle_before_close = idle_before_close
        self.queue_name = queue_name
        self.stats = None

    def __len__(self):
        return len(self.queue)

    @classmethod
    def from_settings(cls, settings):
        persist = settings.get('SCHEDULER_PERSIST', SCHEDULER_PERSIST)
        queue_key = settings.get('SCHEDULER_QUEUE_KEY', QUEUE_KEY)
        queue_cls = load_object(settings.get('SCHEDULER_QUEUE_CLASS', QUEUE_CLASS))
        queue_name = settings.get('REDIS_QUEUE_NAME', None)
        dupefilter_key = settings.get('DUPEFILTER_KEY', DUPEFILTER_KEY)
        idle_before_close = settings.get('SCHEDULER_IDLE_BEFORE_CLOSE', IDLE_BEFORE_CLOSE)
        server = connection.from_settings(settings)
        server_filter = connection.from_settings_filter(settings)
        return cls(server, server_filter, persist, queue_key, queue_cls, dupefilter_key, idle_before_close, queue_name)

    @classmethod
    def from_crawler(cls, crawler):
        instance = cls.from_settings(crawler.settings)
        # 修补:目前，这个构造函数只支持统计数据
        # instance.stats = crawler.stats
        return instance

    async def open_spider(self, spider):
        self.spider = spider
        self.queue = self.queue_cls(self.server, spider, self.queue_key, (self.queue_name if self.queue_name else spider.name))
        self.blockNum = spider.settings.getint("blockNum", 1)
        self.df = RFPDupeFilter(self.server_filter, self.dupefilter_key % {'spider': (self.queue_name if self.queue_name else spider.name)},self.blockNum)
        if self.idle_before_close < 0:
            self.idle_before_close = 0
        # 请注意队列中是否已经有恢复爬行的请求
        if len(self.queue):
            logger.info("Resuming crawl (%d requests scheduled)" % len(self.queue))

    async def close(self, reason):
        if not self.persist:
            self.df.clear()
            self.queue.clear()

    async def enqueue_request(self, request):
        # if not request.dont_filter and self.df.request_seen(request):
        #     return
            # 如果过滤请求加入请求队列

        if not request.dont_filter:
            # 如果请求不在过滤器加入请求队列
            if not self.df.request_seen(request):
                self.queue.push(request)
        else:
            self.queue.push(request)

        # if self.stats:
        # self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)
        # self.queue.push(request)

    async def next_request(self):
        block_pop_timeout = self.idle_before_close
        request = self.queue.pop(block_pop_timeout)
        # if request and self.stats:
        #     self.stats.inc_value('scheduler/dequeued/redis', spider=self.spider)
        # logger.info(request)
        # logger.info(f"len queue {len(self.queue)}")
        return request

    def has_pending_requests(self):
        return len(self) > 0
