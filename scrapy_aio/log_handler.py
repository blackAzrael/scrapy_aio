# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     log_handler
   Description :
   Author :       dean
   date：          2020/7/2 17:30
   日志模块
-------------------------------------------------
   Change Activity:
                   17:30
-------------------------------------------------
"""
import os

import logging
import time

import colorlog
from logging.handlers import TimedRotatingFileHandler
from rich.logging import RichHandler
# import redis

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.join(CURRENT_PATH, os.pardir)
LOG_PATH = os.path.join(ROOT_PATH, 'log')

try:
    os.mkdir(LOG_PATH)
except FileExistsError:
    pass


class LogHandler(logging.Logger):
    """
    LogHandler
    """

    def __new__(cls, *args, **kwargs):

        return super(LogHandler, cls).__new__(cls)

    def __init__(self, name, level='DEBUG', stream=False, file=True, redis=True):
        # print(name)
        self.name = name
        self.level = level
        logging.Logger.__init__(self, self.name, level=level)
        if stream:
            self.__setStreamHandler__()
        else:
            self.__seRichHandler__()
        if file:
            self.__setFileHandler__()
        # if redis:
        #     self.__setRedisHandler__()

    def __setFileHandler__(self, level=None):
        """
        set file handler
        :param level:
        :return:
        """
        file_name = os.path.join(LOG_PATH, '{name}.log'.format(name=self.name))
        # 设置日志回滚, 保存在log目录, 一天保存一个文件, 保留15天
        file_handler = ParallelTimedRotatingHandler(filename=file_name, when='D', interval=1,
                                                    backupCount=15, encoding="utf-8")
        file_handler.suffix = '%Y%m%d.log'
        if not level:
            file_handler.setLevel(self.level)
        else:
            file_handler.setLevel(level)
        # formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        formatter = logging.Formatter('%(asctime)s [%(name)s][%(process)d][line:%(lineno)d] %(levelname)s: %(message)s')

        file_handler.setFormatter(formatter)
        self.file_handler = file_handler
        self.addHandler(file_handler)

    def __setRedisHandler__(self, level=None):
        """
        set file handler
        :param level:
        :return:
        """

        redis_handler = LoggerHandlerToRedis()
        redis_handler.suffix = '%Y%m%d.log'
        if not level:
            redis_handler.setLevel(self.level)
        else:
            redis_handler.setLevel(level)
        # formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        formatter = logging.Formatter('%(asctime)s [%(name)s][%(process)d][line:%(lineno)d] %(levelname)s: %(message)s')

        redis_handler.setFormatter(formatter)
        self.redis_handler = redis_handler
        self.addHandler(redis_handler)

    def __setStreamHandler__(self, level=None):
        """
        set stream handler
        :param level:
        :return:
        """
        stream_handler = colorlog.StreamHandler()
        # formatter = colorlog.ColoredFormatter('%(log_color)s%(asctime)s %(filename)s[line:%(lineno)d] '
        #                                       '%(levelname)s %(message)s', "%Y-%m-%d %H:%M:%S")
        formatter = colorlog.ColoredFormatter('%(log_color)s%(asctime)s [%(filename)s][line:%(lineno)d] '
                                              '%(levelname)s %(message)s', "%Y-%m-%d %H:%M:%S")
        stream_handler.setFormatter(formatter)
        if not level:
            stream_handler.setLevel(self.level)
        else:
            stream_handler.setLevel(level)
        self.addHandler(stream_handler)

    def __seRichHandler__(self, level=None):
        """
        set file handler
        :param level:
        :return:
        """

        # 设置rich 日志
        rich_handler = RichHandler()
        rich_handler.suffix = '%Y%m%d.log'
        if not level:
            rich_handler.setLevel(self.level)
        else:
            rich_handler.setLevel(level)
        # formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        # formatter = logging.Formatter('%(asctime)s [%(filename)s][%(process)d][line:%(lineno)d] %(levelname)s: %(message)s')

        # rich_handler.setFormatter(formatter)
        self.rich_handler = rich_handler
        self.addHandler(rich_handler)

    def resetName(self, name):
        """
        reset name
        :param name:
        :return:
        """
        self.name = name
        self.removeHandler(self.file_handler)
        self.__setFileHandler__()


class LoggerHandlerToRedis(logging.Handler):
    def __init__(self, *args, **kwargs):
        self.website_abbr = kwargs.get("website_abbr") or ""
        super(LoggerHandlerToRedis, self).__init__()
        self.redis_client = redis.StrictRedis(host="localhost", port="6379")

    def emit(self, record):
        """
        无论日志输出到数据库还是websocker输出到前端都可以在此实现
        :param record:
        :return:
        """
        msg = str(self.format(record))
        self.redis_client.publish("redis_log", msg)


class ParallelTimedRotatingHandler(TimedRotatingFileHandler):
    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the
        filename when the rollover happens.  However, you want the file to
        be named for the start of the interval, not the current time.
        If there is a backup count, then we have to get a list of matching
        filenames, sort them and remove the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if not os.path.exists(dfn):
            os.rename(self.baseFilename, dfn)
        if self.backupCount > 0:
            # find the oldest log file and delete it
            for s in self.getFilesToDelete():
                os.remove(s)
        self.mode = 'a'
        self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) \
                and not self.utc:
            dstNow = time.localtime(currentTime)[-1]
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                # DST kicks in before next rollover, so we need to deduct an hour
                if not dstNow:
                    newRolloverAt = newRolloverAt - 3600
                # DST bows out before next rollover, so we need to add an hour
                else:
                    newRolloverAt = newRolloverAt + 3600
        self.rolloverAt = newRolloverAt


if __name__ == '__main__':
    log = LogHandler('test')
    log.debug('this is a test msg')
    log.info('this is a test msg')
    log.warning('this is a test msg')
    log.error('this is a test msg')
