# scrapy3
重写scrapy使用python3.7+ 异步asyncio+aiohttp


## 基础版本来自
https://github.com/xiaochonzi/mavic

---
经过自己大量的修改形成现在的版本
- 完美支持 python3.7 
- 添加scrapy_redis模块支持分布式部署
- 支持本地多进程方式部署
- 使用信号量控制协程数目
 
---
## 觉得好的朋友不要吝啬你的小星星

## 若有问题欢迎大家提交issue和PR 

## 使用 
> pip3 install -r requirements.txt
> 
>pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

### 使用方法同 scrapy 大致相同

``` bash
cd template/spider
python3 365spider.py

```

### 相关配置在setting下


## 添加bing壁纸爬取
```shell script
cd bing
python3 BingSpider.py

```
