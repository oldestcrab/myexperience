#### 中国知网网站脚本爬取
- 爬取`文献检索`搜索页下的文章的关键词
> [文献](http://kns.cnki.net/kns/brief/default_result.aspx)

### 目录
1. `kepu_net_spider.py`——爬取脚本（在windows上的vs code运行）
1. `kepu_net_spider_mysql.py`——爬取脚本（在linux运行，并保存数据到mysql数据库）
2. `kepu_net_spider_result`——爬取到的文章保存位置
3. `kepu_net_spider_result/img`——爬取的文章图片保存位置
4. `judge.txt`——保存判断值，用于判断上次爬取位置