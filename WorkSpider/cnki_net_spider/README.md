#### 中国知网网站脚本爬取
- 爬取`文献检索`搜索页下的文章的关键词
> [文献](http://kns.cnki.net/kns/brief/default_result.aspx)

### 目录
1. `cnki_net_spider.py`——爬取脚本（在windows上的vs code运行）
1. `cnki_net_spider_mysql.py`——爬取脚本（在linux运行，并保存数据到mysql数据库）
2. `cnki_net_spider_result`——爬取到的文章保存位置
3. `cnki_net_spider_result/img`——爬取的文章图片保存位置
4. `judge_*.txt`——保存页数判断值，用于判断上次爬取页数
5. `kw_*.txt`——爬取的关键词
6. `config.py`——配置文件
7. `user-agent.txt`——user-agent列表


### 过程分析
知网即使不用time.sleep()，也不会出现封IP的情况，但是，每爬取15页之后需要输入验证码才可以继续爬取，尝试等待10分钟之后更换user-agent继续访问，有时可以绕过验证码，有时不行，同时，页数过高的情况下，相应的页面会出现没有内容返回的情况，同样尝试等待延时，再访问，还是不行。同时效率不够高，解决办法是每次把爬取的页数存入文件，下次爬取时读取文件，从该页数开始爬取，就是一个关键词，要运行很多次。后续尝试代理IP解决。