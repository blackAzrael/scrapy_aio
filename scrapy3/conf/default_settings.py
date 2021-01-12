# -*- coding:utf-8 -*-
from importlib import import_module

BOT_NAME = 'mavicbot'

CONCURRENT_ITEMS = 100

MAX_POOL = 20  # 并发

CONCURRENT_REQUESTS = 20
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 9

COOKIES_ENABLED = True
COOKIES_DEBUG = False

DEFAULT_ITEM_CLASS = 'scrapy3.item.Item'

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

DNSCACHE_ENABLED = True
DNS_TIMEOUT = 20

DOWNLOADER_MIDDLEWARES = {}

DOWNLOADER_MIDDLEWARES_BASE = {
    'scrapy3.downloadermiddlewares.retry.RetrayMiddleware':550,

}

SPIDER_MIDDLEWARES = {}

SPIDER_MIDDLEWARES_BASE = {
    'scrapy3.spidermiddlewares.depth.DepthMiddleware':550,

}


DOWNLOAD_TIMEOUT = 20

DOWNLOADER = 'scrapy3.core.downloader.Downloader'
DOWNLOAD_HANDLER = 'scrapy3.core.downloader.handler.DownloadHandler'
DUPEFILTER_CLASS = 'scrapy3.dupefilters.RFPDupeFilter'  # 过滤器

ITEM_PROCESSOR = 'scrapy3.pipelines.ItemPipelineManager'

ITEM_PIPELINES = {}
ITEM_PIPELINES_BASE = {}

LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
LOG_FORMATTER = 'scrapy3.logformatter.LogFormatter'
LOG_FORMAT = '%(asctime)s [%(name)s][line:%(lineno)d] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
LOG_STDOUT = False
LOG_LEVEL = 'DEBUG'
LOG_FILE = None
LOG_SHORT_NAMES = False

RANDOMIZE_DOWNLOAD_DELAY = 20

REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 20  # uses Firefox default setting
REDIRECT_PRIORITY_ADJUST = +2

RETRY_ENABLED = True
RETRY_TIMES = 3  # initial response retries = 3 requests
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
RETRY_PRIORITY_ADJUST = 1

# 扫描深度设置
DEPTH_LIMIT = 0
# 深度权值
DEPTH_PRIORITY = 1

SCHEDULER = 'scrapy3.core.scheduler.Scheduler'
# SCHEDULER_PRIORITY_QUEUE = 'asyncio.queues.PriorityQueue'
SCHEDULER_PRIORITY_QUEUE = 'asyncio.queues.Queue'

# USER_AGENT = 'Scrapy/%s (+https://scrapy.org)' % import_module('scrapy').__version__

PLUGIN_MAP = {}  # 用于保存加载插件的全局变量
PLUGIN_CMS_MAP = {}  # 用于保存加载cms插件的全局变量
