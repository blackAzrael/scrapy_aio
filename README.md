
<img alt="python3.7+" src="https://img.shields.io/badge/python-3.7%2B-green" />

# scrapy_aio
Windows and Linux
重构scrapy使用python3.7+ 、aiohttp、uvloop、asyncio简化代码，实现大量并发

Refactor scrapy to use python3.7+, aiohttp, uvloop, asyncio to simplify the code and achieve a lot of concurrency


## 基础版本来自
https://github.com/xiaochonzi/mavic

---
经过自己大量的修改形成现在的版本
- 完美支持 python3.7 
- 添加scrapy_redis模块支持分布式部署
- 支持本地多进程方式部署
- 使用信号量控制协程数目
 
---


## 使用 
> pip3 install -r requirements.txt
> 
>pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

## 示例
``` shell script
cd scrapy3
python3 template/spider/365spider.py

```

### 相关配置在setting下


## bing壁纸爬取
```shell script
cd scrapy3
python3 bing/spider/BingSpider.py

```

