# -*- coding:utf-8 -*-
import logging
import os

from scrapy_aio.utils.request import referer_str

SCRAPEDMSG = u"Scraped from %(src)s" + os.linesep + "%(item)s"
DROPPEDMSG = u"Dropped: %(exception)s" + os.linesep + "%(item)s"
CRAWLEDMSG = u"Crawled (%(status)s) %(request)s (referer: %(referer)s)"
ERRORMSG = u"'Error processing %(item)s'"


class LogFormatter(object):

    def crawled(self, request, response, spider):
        """Logs a message when the crawler finds a webpage."""
        return {
            'level': logging.DEBUG,
            'msg': CRAWLEDMSG,
            'args': {
                # 'status': response.status,
                'request': request,
                'referer': referer_str(request),
                # backward compatibility with Scrapy logformatter below 1.4 version
            }
        }

    def scraped(self, item, response, spider):
        """Logs a message when an item is scraped by a spider."""
        if isinstance(response, Exception):
            src = response.message
        else:
            src = response
        return {
            'level': logging.DEBUG,
            'msg': SCRAPEDMSG,
            'args': {
                'src': src,
                'item': item,
            }
        }

    def dropped(self, item, exception, response, spider):
        """Logs a message when an item is dropped while it is passing through the item pipeline."""
        return {
            'level': logging.WARNING,
            'msg': DROPPEDMSG,
            'args': {
                'exception': exception,
                'item': item,
            }
        }

    def error(self, item, exception, response, spider):
        """Logs a message when an item causes an error while it is passing through the item pipeline."""
        return {
            'level': logging.ERROR,
            'msg': ERRORMSG,
            'args': {
                'item': item,
            }
        }

    @classmethod
    def from_crawler(cls, crawler):
        return cls()
