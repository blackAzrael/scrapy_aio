# -*- coding:utf-8 -*-



ITEM_PIPELINES = {
    # "bing.pipelines.DefaultPipelines": 300,
    "bing.pipelines.ImageSavePipelines": 301,

}
SPIDER_MIDDLEWARES = {

    # 'bing.middlewares.DeduplicateUrlMiddleware': 543,        # 对URL框架进行去重 使用redis

}

DOWNLOADER_MIDDLEWARES = {

    # 'bing.middlewares.RetrayMiddleware': 633,
    'bing.middlewares.ProcessAllExceptionMiddleware': 643,
    'bing.middlewares.RotateUserAgentMiddleware': 743,       # 随机浏览器UA
    # 'bing.middlewares.ProxyMiddleware': 843,                 # 代理中间件
}
# SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
# SCHEDULER_PERSIST = True  # 默认true   是否保存 过滤的url  true 为保存
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue_redis.SpiderPriorityQueue'      # redis 优先级队列
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue_redis.SpiderQueue'
# REDIS_QUEUE_NAME = 'spider'
# SCHEDULER_QUEUE_CLASS = 'scrapy3-master.scrapy_redis.queue.SpiderSimpleQueue'

# 下载器
# DOWNLOAD_HANDLER = "bing.download_handler.DownloadHandler"               # chrome动态下载器

# 种子队列的信息
# REDIE_URL = None
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379


# MongoDB配置
# MONGO_HOST = "localhost"  # 主机IP
# MONGO_PORT = 27017  # 端口号
# MONGO_DB = "web_scrapy1"  # 库名
# MONGO_COLL = "web_spider1"  # collection名
# MONGO_USER = "simple" #用户名
# MONGO_PSW = "test" #用户密码
# ES配置
# ES_HOST = "localhost"
# ES_PORT = 9200
# ES_AUTH = ()  # ('user','password')

# 去重队列的信息
# FILTER_URL = None
# FILTER_HOST = 'localhost'
# FILTER_PORT = 6379
# FILTER_DB = 0
# REDIS_QUEUE_NAME = 'OneName'      # 如果不设置或者设置为None，则使用默认的，每个spider使用不同的去重队列和种子队列。
                                    # 如果设置了，则不同spider共用去重队列和种子队列


LOG_LEVEL = 'INFO'
# LOG_LEVEL = 'DEBUG'
# CONCURRENT_REQUESTS = 100  # 并发
MAX_POOL = 8  # 并发

DNS_TIMEOUT = 20  # DNS解析超时时间设置
RETRY_TIMES = 2  # initial response retries = 3 requests  一共访问次数

DOWNLOAD_TIMEOUT = 60 # 下载超时时间

# 爬虫计数日志
SCRAPY_COUNT = False

# 扫描深度设置
DEPTH_LIMIT = 3
# 深度权值
DEPTH_PRIORITY = 1

# redis 过滤器 RFPDupeFilter 个数
blockNum = 1