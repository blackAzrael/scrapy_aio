# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     download_hander
   Description : 重写下载模块  可用Chrome
   Author :       dean
   date：          2020/9/24 10:35
-------------------------------------------------
   Change Activity:
                   2020/9/24 10:35
-------------------------------------------------
"""
import asyncio
import time

import aiohttp
import platform


async def start():
    pass


if __name__ == '__main__':
    sysstr = platform.system()
    loop = asyncio.get_event_loop()
    if sysstr == "Windows":
        print("Call Windows tasks")
    elif sysstr == "Linux":
        print("Call Linux tasks")
        import uvloop

        loop = uvloop.new_event_loop()
    else:
        print("Other System tasks")

    loop.run_until_complete(start())
    loop.close()
