# -*- coding:utf-8 -*-
from scrapy_aio.http import Request


def to_unicode(text, encoding=None, errors='strict'):
    """Return the unicode representation of a bytes object ``text``. If
    ``text`` is already an unicode object, return it as-is."""
    if isinstance(text, str):
        return text
    if not isinstance(text, (bytes, str)):
        raise TypeError('to_unicode must receive a bytes or str '
                        'object, got %s' % type(text).__name__)
    if encoding is None:
        encoding = 'utf-8'
    return text.decode(encoding, errors)


def to_bytes(text, encoding=None, errors='strict'):
    """Return the binary representation of ``text``. If ``text``
    is already a bytes object, return it as-is."""
    if isinstance(text, bytes):
        return text
    if not isinstance(text, str):
        raise TypeError('to_bytes must receive a str or bytes '
                        'object, got %s' % type(text).__name__)
    if encoding is None:
        encoding = 'utf-8'
    return text.encode(encoding, errors)


def without_none_values(iterable):
    """Return a copy of ``iterable`` with all ``None`` entries removed.

    If ``iterable`` is a mapping, return a dictionary where all pairs that have
    value ``None`` have been removed.
    """
    try:
        return {k: v for k, v in iterable.items() if v is not None}
    except AttributeError:
        return type(iterable)((v for v in iterable if v is not None))


async def get_result_list(result: list) -> list:

    if result is None:
        return []
    if isinstance(result, (dict, str)):
        # print("这是一个字典")
        return [result]
    if isinstance(result, Request):
        # print("这是一个请求")
        return [result]
    if hasattr(result, "__iter__"):
        # 如果是生成器对象
        # print("这是一个同步生成器")
        res = []
        for item in result:
            res.append(item)
            # print(item)
        return res
    if result.__class__.__name__ == "async_generator":
        # print("这是一个异步生成器")
        res = []
        async for item in result:
            res.append(item)

        return res
