#### 复旦大学医学神经生物学国际重点实验室文章爬取脚本
- 爬取[资讯动态](http://skmn.fudan.edu.cn/Data/List/zxdt1)分类下的文章


### 目录
1. `skmn_fudan_spider.py`——爬取脚本（在windows上的vs code运行，并保存数据到mysql数据库）
1. `skmn_fudan_spider_v2.py`——爬取脚本（在linux运行，并保存数据到mysql数据库）
2. `skmn_fudan_spider_threading`——多线程爬取脚本
3. `skmn_fudan_spider_result`——爬取到的文章保存位置
4. `skmn_fudan_spider_result/img`——爬取的文章图片保存位置
5. `judge*.txt`——保存判断值，用于判断上次爬取位置
5. `user-agents.txt`——user-agents