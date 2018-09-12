#### 生物通网站脚本爬取
- 爬取相关分类下的文章
> [生物谷](http://www.bioon.com/)

### 目录
1. `ebiotrade_spider.py`——爬取脚本（在windows上的vs code运行）
1. `ebiotrade_spider_mysql.py`——爬取脚本（在linux运行，并保存数据到mysql数据库）
2. `ebiotrade_spider_result`——爬取到的文章保存位置
3. `ebiotrade_spider_result/img`——爬取的文章图片保存位置
4. `judge_*.txt`——保存判断值，用于判断上次爬取位置
5. `user-agent.txt`——user-agent列表


http://www.bioon.com/
先只爬这个，版权问题
http://www.bioon.com/load_more.do?p=6
ajax加载|异步刷新
变得只有P参数，最简单的那种
页数也是对的