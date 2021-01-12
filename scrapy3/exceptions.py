# -*- coding:utf-8 -*-

class NotConfigured(Exception):
    """Indicates a missing configuration situation"""
    pass


class IgnoreRequest(Exception):
    """Indicates a decision was made not to process a request"""


class DontCloseSpider(Exception):
    """Request the spider not to be closed yet"""
    pass


class CloseSpider(Exception):
    """Raise this from callbacks to request the spider to be closed"""

    def __init__(self, reason='cancelled'):
        super(CloseSpider, self).__init__()
        self.reason = reason


# Items


class DropItem(Exception):
    """Drop item from the item pipeline"""
    pass
