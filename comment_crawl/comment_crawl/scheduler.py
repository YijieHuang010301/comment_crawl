from apscheduler.schedulers.blocking import BlockingScheduler
import time
from comment_crawl.main import redis_conn


def push_task_to_redis():
    # 定义你需要爬取的 URL
    url = "http://example.com"

    # 将 URL 推入 Redis 队列
    redis_conn.lpush("myspider:start_urls", url)
    print(f"任务已推送到 Redis: {url} at {time.ctime()}")


# 使用 APScheduler 每小时推送一次任务
scheduler = BlockingScheduler()
scheduler.add_job(push_task_to_redis, 'interval', hours=1)

# 启动调度器
scheduler.start()
