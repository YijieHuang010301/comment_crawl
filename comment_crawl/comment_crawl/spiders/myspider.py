import json
import os
import random
from abc import abstractmethod
from datetime import datetime
from scrapy_redis.spiders import RedisSpider
from fake_useragent import UserAgent
from sqlalchemy import text
from scrapy.loader import ItemLoader

from comment_crawl.common.const import MAX_REVIEWS, ALL_PRODUCTS_TABLE, DB_UPDATE, PRODUCT_REVIEWS_TABLE
from comment_crawl.items import ReviewItem
from comment_crawl.util.db_conn import set_isDelete_ALL_PRODUCTS_TABLE, execute_sql

# 插入总评分信息
insert_rating_sql = text(
        f'''
        UPDATE {ALL_PRODUCTS_TABLE}
        SET 
            RatingCount = :RatingCount,
            AverageRatingValue = :AverageRatingValue,
            Rating_5_Count = :Rating_5_Count,
            Rating_4_Count = :Rating_4_Count,
            Rating_3_Count = :Rating_3_Count,
            Rating_2_Count = :Rating_2_Count,
            Rating_1_Count = :Rating_1_Count,
            UpdateTime = :UpdateTime
        WHERE id = :id AND ProductId = :ProductId
        '''
    )

# 插入用户评论信息
insert_reviews_sql = text(f'''
    INSERT INTO {PRODUCT_REVIEWS_TABLE} (
        review_id,
        platform_id,
        product_id,
        reviewer_name,
        reviewer_id,
        is_verified,
        verified_type,
        review_date,
        rating_stars,
        product_comments_title,
        product_comments_content,
        language_code,
        reviewer_location,
        is_recommended,
        review_helpful_count,
        review_unhelpful_count,
        product_photos,
        product_photos_thumbnail,
        product_videos,
        product_options,
        update_time
    ) VALUES (
        :review_id,
        :platform_id,
        :product_id,
        :reviewer_name,
        :reviewer_id,
        :is_verified,
        :verified_type,
        :review_date,
        :rating_stars,
        :product_comments_title,
        :product_comments_content,
        :language_code,
        :reviewer_location,
        :is_recommended,
        :review_helpful_count,
        :review_unhelpful_count,
        :product_photos,
        :product_photos_thumbnail,
        :product_videos,
        :product_options,
        :update_time
    )
    ON DUPLICATE KEY UPDATE
        reviewer_name = VALUES(reviewer_name),
        reviewer_id = VALUES(reviewer_id),
        is_verified = VALUES(is_verified),
        verified_type = VALUES(verified_type),
        review_date = VALUES(review_date),
        rating_stars = VALUES(rating_stars),
        product_comments_title = VALUES(product_comments_title),
        product_comments_content = VALUES(product_comments_content),
        language_code = VALUES(language_code),
        reviewer_location = VALUES(reviewer_location),
        is_recommended = VALUES(is_recommended),
        review_helpful_count = VALUES(review_helpful_count),
        review_unhelpful_count = VALUES(review_unhelpful_count),
        product_photos = VALUES(product_photos),
        product_photos_thumbnail = VALUES(product_photos_thumbnail),
        product_videos = VALUES(product_videos),
        product_options = VALUES(product_options),
        update_time = VALUES(update_time)
''')


# 虚拟移动端用户访问agent
def get_fake_mobile_user_agent():
    user_agents = [
        "Linux; U; Android 11; Xiaomi; MI 11",
        "Linux; U; Android 13; Google; Pixel 7 Pro",
        "Linux; U; Android 10; OnePlus; ONEPLUS A6010",
        "Linux; U; Android 12; OPPO; CPH2025",
        "Linux; U; Android 9; Sony; G8341",
        "Linux; U; Android 13; Samsung; SM-F926B",
        "Linux; U; Android 10; Huawei; P40 Pro",
        "Linux; U; Android 11; Vivo; V2056A",
        "Linux; U; Android 12; Motorola; XT2125",
        "Linux; U; Android 11; Asus; ROG Phone 5"
    ]
    return random.choice(user_agents)

# 虚拟用户访问agent
def get_fake_user_agent():
    ua = UserAgent()
    return ua.random


class BaseSpider(RedisSpider):
    name = 'BaseSpider'
    redis_key = 'myspider:start_urls'

    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        self.max_reviews = MAX_REVIEWS

    # 预处理返回的response
    def parse(self, response):
        uuid = response.meta.get('uuid')
        product_id = response.meta.get('product_id')
        is_first_time = response.meta.get('is_first_time')

        # 如果访问失败，设置is_delete属性为1(true)
        if response.status != 200:
            print(f"delete {product_id}")
            self.set_isDelete(uuid)
            return

        try:
            response_data = json.loads(response.text)  # 确保解析 JSON
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for product ID {product_id}: {str(e)}")
            return

        # 调用子类，处理解析后的数据
        self.parse_response_data(response_data, uuid, product_id, is_first_time)


    @abstractmethod
    def parse_response_data(self, response_data, uuid, product_id, is_first_time):
        """
        子类需要实现的方法，处理解析后的数据
        """
        pass

    @abstractmethod
    def read_data_from_db(self):
        raise NotImplementedError("Subclasses must implement the read_data_from_db method.")

    @abstractmethod
    def save_rating_info(self, product_id, uuid, customer_reviews_stats):
        raise NotImplementedError("Subclasses must implement the save_rating_info method.")

    def save_reviews(self, product_id, reviews):
        parsed_reviews = []

        for review in reviews:
            loader = ItemLoader(item=ReviewItem())
            loader.add_value('product_id', product_id)
            loader.add_value('update_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            # 调用子类实现的填充方法
            self.populate_review_loader(loader, review)

            # 将加载后的 ReviewItem 添加到列表
            parsed_reviews.append(loader.load_item())

        # 保存到数据库
        rows, error = execute_sql(insert_reviews_sql, DB_UPDATE, params=parsed_reviews)
        if error:
            print(f"Error occurred: {error}")
        else:
            print(f"Updated {rows} rows comment successfully for ProductId {product_id}.")

    @abstractmethod
    def populate_review_loader(self, loader, review):
        """
        子类需要实现此方法，将特定的 review 字段填充到 loader 中。
        """
        pass

    def save_rating_info_to_db(self, product_id, uuid, rating_info):
        """
        构建共享的 params 字典。

        :param product_id: 产品ID
        :param uuid: 唯一标识符
        :param rating_info: 包含评分信息的字典，需包含以下键：
            - rating_count_total
            - average_rating_value
            - rating_counts (字典，键为评分，值为数量)
        :return: 构建好的 params 字典
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rating_counts = rating_info.get('rating_counts', {})
        params = {
            'id': uuid,  # 根据 uuid 更新对应记录
            'ProductId': product_id,
            'RatingCount': rating_info.get('rating_count_total', 0),  # 评分数量
            'AverageRatingValue': rating_info.get('average_rating_value', 0),  # 平均评分
            'Rating_5_Count': rating_counts.get(5, 0),  # 5 星的评论数量
            'Rating_4_Count': rating_counts.get(4, 0),  # 4 星的评论数量
            'Rating_3_Count': rating_counts.get(3, 0),  # 3 星的评论数量
            'Rating_2_Count': rating_counts.get(2, 0),  # 2 星的评论数量
            'Rating_1_Count': rating_counts.get(1, 0),  # 1 星的评论数量
            'UpdateTime': current_time  # 更新时间
        }
        rows, error = execute_sql(insert_rating_sql, DB_UPDATE, params=params)

        if error:
            print(f"Error occurred: {error}")
        else:
            print(f"Rating info updated successfully for ProductId {product_id}.")


    def set_isDelete(self, uuid):
        set_isDelete_ALL_PRODUCTS_TABLE(uuid)

    def write_to_log(self, response_data, product_id, platform_id):
        # ------ debug ------
        # 定义日志文件名
        log_file = f"comment_crawl/log/{platform_id}.log"
        if os.path.exists(log_file):
            os.remove(log_file)
            self.logger.info(f"Previous log file {log_file} deleted.")
        # 写入文件，将 response.text 写入日志文件
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"Response for product ID {product_id}:\n")
            f.write(str(response_data))
            f.write("\n" + "=" * 50 + "\n")

        # 打印日志位置
        self.logger.info(f"Response saved to {log_file}")
        pass


