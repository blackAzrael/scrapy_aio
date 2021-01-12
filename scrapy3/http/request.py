# -*- coding:utf-8 -*-
import asyncio
import logging

from w3lib.url import safe_url_string

logger = logging.getLogger(__name__)
from http.cookies import SimpleCookie


class Request(object):

    def __init__(self, url, callback=None, method='GET', params=None, data=None, json=None,
                 headers=None, cookies=None, encoding='utf-8', meta=None, priority=0, dont_filter=False,
                 errback=None, allow_redirects=True):
        self._encoding = encoding
        self.method = str(method).upper()
        self._set_url(url)
        self._set_params(params)
        if data is not None and json is not None:
            raise ValueError('data and json parameters can not be used at the same time')
        self._set_data(data)
        self._set_json(json)
        assert isinstance(priority, int), 'Request priority not an integer:%r' % priority
        self.priority = priority
        if callback is not None and (not callable(callback) or asyncio.iscoroutine(callback)):
            raise TypeError('callback must be callable or coroutine')
        if errback is not None and (not callback(errback) or asyncio.iscoroutinefunction(errback)):
            raise TypeError('errback must be callable or coroutine')

        self.callback = callback
        self.errback = errback
        if isinstance(cookies, dict):
            self.cookies = dict(cookies) if cookies else {}
        elif isinstance(cookies, str):
            try:
                self.cookies = SimpleCookie(cookies)
            except Exception as e:
                logger.exception(e)
        else:
            self.cookies = {}
        self.headers = dict(headers) if headers else {}
        self.dont_filter = dont_filter
        self.allow_redirects = allow_redirects
        self._meta = dict(meta) if meta else None

    @property
    def meta(self):
        if self._meta is None:
            self._meta = {}
        return self._meta

    def _get_url(self):
        return self._url

    def _set_url(self, url):
        if not isinstance(url, str):
            raise TypeError('Request url must be str or unicode, got %s:' % type(url).__name__)

        s = safe_url_string(url, self.encoding)
        self._url = s

    url = property(_get_url, _set_url)

    def _get_params(self):
        return self._params

    def _set_params(self, params):
        self._params = params

    params = property(_get_params, _set_params)

    def _set_data(self, data):
        self._data = data

    def _get_data(self):
        return self._data

    data = property(_get_data, _set_data)

    def _get_json(self):
        return self._json

    def _set_json(self, json):
        self._json = json

    json = property(_get_json, _set_json)

    def copy(self):
        """Return a copy of this Request"""
        return self.replace()

    @property
    def encoding(self):
        return self._encoding

    def replace(self, *args, **kwargs):
        for x in ['url', 'method', 'headers', 'data', 'json', 'cookies', 'meta',
                  'encoding', 'priority', 'dont_filter', 'allow_redirects', 'callback', 'errback']:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)

    def __str__(self):
        return "<%s %s>" % (self.method, self.url)

    __repr__ = __str__
