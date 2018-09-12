#### 中国野生动物保护协会网站脚本爬取
- 爬取`首页 > 新闻 >新闻报道`分类下的文章
> [新闻报道](http://www.cwca.org.cn/news/tidings/)

### 目录
1. `cwca_org_spider.py`——爬取脚本（在windows/vs code运行）
1. `cwca_org_spider_mysql.py`——爬取脚本（在linux运行，并保存数据到mysql数据库）
2. `cwca_org_spider_result`——爬取到的文章保存位置
3. `cwca_org_spider_result/img`——爬取的文章图片保存位置
4. `judge.txt`——保存判断值，用于判断上次爬取位置