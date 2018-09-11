#### 维普网网站脚本爬取
- 爬取`文献检索`搜索页下的文章的关键词
> [文献](http://cqvip.com/)

### 目录
1. `cqvip_spider.py`——爬取脚本（在windows上的vs code运行）
1. `cqvip_spider_mysql.py`——爬取脚本（在linux运行，并保存数据到mysql数据库）
2. `cqvip_spider_result`——爬取到的文章保存位置
3. `cqvip_spider_result/img`——爬取的文章图片保存位置
4. `judge_page*.txt`——保存页数判断值，用于判断上次爬取页数
5. `kw*.txt`——爬取的关键词
6. `user-agent.txt`——user-agent列表


### 过程分析
主要有IP限制，若爬取太快，IP会被封，要几个小时之后才能访问，但脚本爬取的时间太长的话，也会有链接不上的情况，最好通过代理IP访问，现只能爬取五页之后通过更换user-agent,同时time.sleep(4)慢慢爬
