### 启动scrapydweb
terminal 1:
scrapydweb -p 5001 

terminal 2:
scrapyd-deploy default 
scrapyd 

terminal 3:
redis-cli

### 项目目录结构

```plaintext
comment_crawl/        # 爬虫包
├── common/           # 公用方法库
│   ├── const.py      # 定义常数
│   └── errors.py     # 定义错误类
├── downloads/        # 存储传入的表格
├── logs/             # 临时日志目录
├── spiders/          # 爬虫目录
│   ├── myspider.py           # 爬虫父类
│   ├── homedepot_spider.py   # homedepot 爬虫
│   └── wayfair_spider.py     # wayfair 爬虫
├── templates/        # 简单前端（未启用）
├── util/             # 常用工具方法
│   ├── crawl_util/        # 爬虫常用方法
│   │   └── push_to_redis.py  # 将待爬取 URL 推入 Redis
│   ├── db_conn.py    # 数据库连接及操作
│   ├── hash_util.py  # 哈希方法
│   ├── process_input.py   # 处理传入表格数据
│   └── url_parser.py      # 解析不同平台的 URL
├── items.py          # 爬虫数据结构定义
├── main.py           # 程序入口
├── middlewares.py    # 中间件（未启用）
├── pipelines.py      # 数据管道（未启用）
├── scheduler.py      # 任务调度器（未启用）
└── settings.py       # Scrapy 的具体设置

  
