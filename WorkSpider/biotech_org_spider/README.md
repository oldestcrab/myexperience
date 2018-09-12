#### 中国生物技术信息网站脚本爬取
- 爬取`文献导读、重点关注、新闻扫描：基础与前沿、新闻扫描：工业生物、新闻扫描：农业生物、新闻扫描：医药生物`分类下的文章
> [生物技术信息网](http://www.biotech.org.cn/)

### 目录
1. `biotech_org_spider.py`——爬取脚本（在windows上的vs code运行）
1. `biotech_org_spider_mysql.py`——爬取脚本（在linux运行，并保存数据到mysql数据库）
2. `biotech_org_spider_result`——爬取到的文章保存位置
3. `biotech_org_spider_result/img`——爬取的文章图片保存位置
4. `judge_*.txt`——保存判断值，用于判断上次爬取位置