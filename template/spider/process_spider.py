# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     process_spider
   Description :
   Author :       dean
   date：          2021/5/31 21:31
-------------------------------------------------
   Change Activity:
                   21:31
-------------------------------------------------
"""

import asyncio
import platform
import os
import sys

now_path = os.getcwd()
root_path = now_path.split("scrapy_aio")[0] + "/scrapy_aio"
os.chdir(root_path)
sys.path.append(root_path)
from template import settings
from scrapy_aio.conf.settings import Settings
from scrapy_aio.core.crawler import Crawler
from scrapy_aio.http.request import Request
from scrapy_aio.spiders import Spider
from scrapy_aio.log_handler import LogHandler
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table

logger = log = LogHandler(__name__)

sysstr = platform.system()
if sysstr == "Windows":
    print("Call Windows tasks")
    import selectors

    selector = selectors.SelectSelector()  # New line
    loop = asyncio.SelectorEventLoop(selector)
elif sysstr == "Linux":
    print("Call Linux tasks")
    import uvloop

    loop = uvloop.new_event_loop()
else:
    loop = asyncio.get_event_loop()


class ComSpider(Spider):
    name = 'test'

    def start_requests(self):
        yield Request(url='http://youdao.com', dont_filter=True, callback=self.parse)

    async def parse(self, response):
        logger.warning(f"parse {response.meta}")
        logger.warning(f"parse {response.url}")
        meta = {
            "download_timeout": 60,
        }
        for i in range(100):
            yield Request(url=f"http://www.baidu.com/s?wd={i}", meta=meta, dont_filter=True,
                          callback=self.parse_content)

    async def parse_content(self, response):
        # while not progress.finished:
        # progress.update(task1, advance=1)
        download_process.update(job_download, advance=1)
        logger.debug(response.url)
        # logger.debug(response.status)

        yield {"result": response.url}


async def start():
    await crawler.crawl()
    await crawler.start()


download_process = job_progress = Progress(
    "{task.description}",
    SpinnerColumn(),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
)
job_download = download_process.add_task("[green]downloading")
progress_table = Table.grid()

progress_table.add_row(
    Panel.fit(job_progress, title="[b]Jobs", border_style="red", padding=(1, 2)),
)


if __name__ == '__main__':
    with Live(progress_table, refresh_per_second=10):
        s = Settings()
        s.setmodule(settings)
        crawler = Crawler(ComSpider, s, loop)
        loop.run_until_complete(start())
        loop.close()
