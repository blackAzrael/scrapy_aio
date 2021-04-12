# -*- coding:utf-8 -*-
import re


class Response(object):
    """ Response """

    def __init__(self, url, status=200, headers=None, body=b'',
                 encoding=None, request=None, resp=None):
        self._set_url(url)
        self.status = int(status)
        self.headers = dict(headers) if headers else {}
        self._set_body(body)
        self._encoding = encoding
        self.request = request
        self.resp = resp
        self.redir_url = self.get_redir_url() # 重定向real url  真正的url
        self.time = 0
    @property
    def meta(self):
        try:
            return self.request.meta
        except AttributeError:
            raise AttributeError("Response.meta not available")

    def get_redir_url(self):
        try:
            url = str(self.resp.real_url)
        except  Exception as e:
            url = self.url

        return url

    def _get_url(self):
        return self._url

    def _set_url(self, url):
        if isinstance(url, str):
            self._url = url
        else:
            raise TypeError('%s url must be str, got %s:' % (type(self).__name__, type(url).__name__))

    url = property(_get_url, _set_url)

    def _get_body(self):
        return self._body

    def _set_body(self, body):
        if body is None:
            self._body = b''
        elif not isinstance(body, bytes):
            raise TypeError('Response body must be bytes.')
        else:
            self._body = body

    body = property(_get_body, _set_body)

    @property
    def text(self, errors='strict'):
        if self._body:
            try:
                text = self._body.decode(self._encoding, errors=errors)
            except Exception as error:
                try:
                    # text = self._body.decode(encoding='gb2312', errors="ignore")
                    # searchObj = re.search(b'charset=(\w+)', self._body, re.M|re.I)
                    searchObj = re.search(b"""charset=["']?([a-zA-Z0-9_-]+)["'/]?""", self._body, re.M|re.I)
                    if searchObj:
                        encoding = searchObj.group(1)
                        encoding = str(encoding, encoding="utf-8")
                        text = self._body.decode(encoding=encoding, errors="ignore")
                    else:
                        text = self._body.decode(encoding="gb2312", errors="ignore")

                except Exception as error:
                    return f"网页解码出现问题 {error}"
                return text
            else:
                return text
        else:
            return ""

    def __str__(self):
        return "<%d %s %s>" % (self.status, self.request.method, self._url)

    __repr__ = __str__
