# -*- coding:utf-8 -*-
import asyncio
from collections import Iterable
from importlib import import_module
from inspect import isfunction

from scrapy3.http import Request
# from utils.log_handler import LogHandler

# logger = log = LogHandler(__name__)


def load_object(path):
    """Load an object given its absolute object path, and return it.

    object can be a class, function, variable or an instance.
    path ie: 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware'
    """

    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)

    module, name = path[:dot], path[dot + 1:]
    mod = import_module(module)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError("Module '%s' doesn't define any object named '%s'" % (module, name))

    return obj


def create_instance(objcls, settings, crawler, *args, **kwargs):
    """Construct a class instance using its ``from_crawler`` or
    ``from_settings`` constructors, if available.

    At least one of ``settings`` and ``crawler`` needs to be different from
    ``None``. If ``settings `` is ``None``, ``crawler.settings`` will be used.
    If ``crawler`` is ``None``, only the ``from_settings`` constructor will be
    tried.

    ``*args`` and ``**kwargs`` are forwarded to the constructors.

    Raises ``ValueError`` if both ``settings`` and ``crawler`` are ``None``.
    """
    if settings is None:
        if crawler is None:
            raise ValueError("Specify at least one of settings and crawler.")
        settings = crawler.settings
    if crawler and hasattr(objcls, 'from_crawler'):
        return objcls.from_crawler(crawler, *args, **kwargs)
    elif hasattr(objcls, 'from_settings'):
        return objcls.from_settings(settings, *args, **kwargs)
    else:
        return objcls(*args, **kwargs)


async def call_func(func, callback=None, errback=None, *args, **kwargs):
    """
    :param func:
    :param errback:
    :param callback:
    :param args:
    :param kwargs:
    :return:
    """
    try:
        result = await func(*args, **kwargs)
    except Exception as exc:
        #     # 异常回调函数
        if errback:
            result = await errback(exc)
            return result
    else:
        if callback:
            result = await callback(result)
        return result


async def call_func_spider_mw(func, callback=None, errback=None, *args, **kwargs):
    """
    :param func: spider 函数
    :param errback:
    :param callback:  执行process_spider_output
    :param args:
    :param kwargs:
    :return: 返回的结果交给 reqser 判断是request加入crawl 是 dic 加入管道
    """
    try:
        result = await func(*args, **kwargs)  # 已经经过spider处理过的结果 可能是[item] [request]  或者item request
    except Exception as exc:
        #     # 异常回调函数
        if errback:
            result = await errback(exc)
            return result
    else:
        if callback:
            if asyncio.iscoroutine(result):
                result = await result
            if isinstance(result, dict):  # 如果spider返回的是个字典 直接进入管道
                return result
            if isinstance(result, Request):  # 如果spider返回的是个请求
                return await callback(result)
            if isinstance(result, Iterable):  # 如果spider 返回的是个 yield
                res = []
                res = await for_each_generator(result,callback)
                result = iter(res)

            if result.__class__.__name__ == "async_generator":  # 如果是一个异步生成器
                res = await for_each_async_generator(result, callback)
                result = iter(res)

        return result


async def for_each_async_generator(result,callback):
    """
    遍历异步生成器 返回一个列表
    :param result:  spider 的返回值
    :param callback:
    :return:
    """

    # logger.info("spider return async_generator")
    res = []
    async for item in result:
        if asyncio.iscoroutine(item) and not isinstance(item, Iterable):
            item = await item
        if isinstance(item, Request):
            ret = await callback(item)  # 获取每个process_spider_output 的结果
            # logger.info(ret)
            if ret:
                res.append(ret)
                continue
        if isinstance(item, dict):
            res.append(item)
            continue
        if isinstance(item, Iterable):
            tmp = await for_each_generator(item,callback)
            res.extend(tmp)
        if item.__class__.__name__ == "async_generator":
            tmp = await for_each_async_generator(item, callback)
            res.extend(tmp)
    # result = iter(res)

    return res


async def for_each_generator(result, callback):
    """
    遍历生成器 返回一个列表
    :param result:  spider 的返回值
    :param callback:
    :return:
    """

    # logger.info("spider return generator")
    res = []
    for item in result:
        if isinstance(item, Request):
            ret = await callback(item)  # 获取每个process_spider_output 的结果
            if ret:
                res.append(ret)
                continue
        if isinstance(item, dict):
            res.append(item)
            continue
        if isinstance(item, Iterable):
            tmp = await for_each_generator(item, callback)
            res.extend(tmp)
        if item.__class__.__name__ == "async_generator":
            tmp = await for_each_async_generator(item, callback)
            res.extend(tmp)
    # logger.info(res)
    # result = iter(res)

    return res