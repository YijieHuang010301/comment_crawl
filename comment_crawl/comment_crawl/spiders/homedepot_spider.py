import json
import math
from datetime import datetime

import scrapy

from comment_crawl.common.const import HOMEDEPOT_PLATFORM_ID, MAX_REVIEWS
from comment_crawl.spiders.myspider import BaseSpider
from comment_crawl.util.crawl_util.push_to_redis import push_retry_url_to_redis


# Homedepot's spider
# 每次可以爬取最多100 reviews
class HomeDepotSpider(BaseSpider):
    name = 'homedepot_spider'
    redis_key = 'homedepot_spider:urls'
    def __init__(self, *args, **kwargs):
        super(HomeDepotSpider, self).__init__(*args, **kwargs)
        self.platform_id = HOMEDEPOT_PLATFORM_ID

    def make_request_from_data(self, data):
        data = json.loads(data)
        url = data['url']
        headers = data['headers']
        uuid = data['uuid']
        product_id = data['product_id']
        is_first_time = data['is_first_time']
        payload = data['payload']

        return scrapy.Request(
            url=url,
            method="POST",
            headers=headers,
            body=json.dumps(payload),  # 使用 body 传递 JSON 数据
            callback=self.parse,  # 回调函数处理响应
            meta={'product_id': product_id, 'uuid': uuid, 'is_first_time': is_first_time},  # 将 product_id 传递给下一个方法
            dont_filter=True
        )

    def parse_response_data(self, response_data, uuid, product_id, is_first_time):
        # 如果product不存在了
        if response_data["data"]["reviews"]["Includes"]["Products"] is None:
            self.set_isDelete(uuid)
            return

        customer_reviews_stats = response_data["data"]["reviews"]["Includes"]["Products"]["store"]["FilteredReviewStatistics"]
        total_results = response_data["data"]["reviews"]["TotalResults"]
        if is_first_time:
            self.save_rating_info(product_id, uuid, customer_reviews_stats)

            for i in range(math.ceil(total_results / MAX_REVIEWS)):
                start_idx = i * MAX_REVIEWS + 1
                push_retry_url_to_redis(self.platform_id, product_id, uuid, start_idx, MAX_REVIEWS)
        else:
            if total_results > 0:
                reviews = response_data["data"]["reviews"]["Results"]
                self.save_reviews(product_id, reviews)



    def save_rating_info(self, product_id, uuid, customer_reviews_stats):
        average_rating_value = customer_reviews_stats.get("AverageOverallRating", '0')
        rating_count_total = int(customer_reviews_stats.get("TotalReviewCount", 0))
        rating_distribution = customer_reviews_stats.get("RatingDistribution", [])
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for item in rating_distribution:
            rating_value = int(item.get('RatingValue', 0))
            count = int(item.get('Count', 0))
            if rating_value in rating_counts:
                rating_counts[rating_value] = count

        rating_info = {
            'rating_count_total': rating_count_total,
            'average_rating_value': average_rating_value,
            'rating_counts': rating_counts
        }
        self.save_rating_info_to_db(product_id, uuid, rating_info)

    def populate_review_loader(self, loader, review):
        loader.add_value('review_id', review.get('Id'))
        loader.add_value('reviewer_id', review.get('AuthorId'))
        loader.add_value('reviewer_name', review.get('UserNickname'))
        loader.add_value('platform_id', self.platform_id)

        badges = review.get("BadgesOrder") or []
        is_verified = "verifiedPurchaser" in badges
        verified_type = ",".join(badges) if badges else "unverified_buyer"

        loader.add_value('is_verified', is_verified)
        loader.add_value('verified_type', verified_type)

        submission_time = review.get("SubmissionTime")
        if submission_time:
            review_date = datetime.strptime(submission_time, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d")
        else:
            review_date = "1970-01-01"  # 设置一个默认日期，防止日期缺失的情况
        loader.add_value('review_date', review_date)

        loader.add_value('rating_stars', review.get('Rating'))
        loader.add_value('product_comments_title', review.get('Title') or '')
        loader.add_value('product_comments_content', review.get('ReviewText') or '')

        loader.add_value('is_recommended', review.get("IsRecommended") or False)
        reviewer_location = review.get('UserLocation') or ''
        loader.add_value('reviewer_location', reviewer_location)
        loader.add_value('review_helpful_count', review.get('TotalPositiveFeedbackCount', 0))
        loader.add_value('review_unhelpful_count', review.get('TotalNegativeFeedbackCount', 0))

        Videos = review.get("Videos") or ''
        loader.add_value('product_videos', Videos)

        product_photos = review.get('Photos') or ''


        loader.add_value('product_photos', ','.join(
            [photo.get('Sizes', {}).get('normal', {}).get('Url', '') for photo in product_photos if 'Sizes' in photo]
        ))
        loader.add_value('product_photos_thumbnail', ','.join(
            [photo.get('Sizes', {}).get('thumbnail', {}).get('Url', '') for photo in product_photos if 'Sizes' in photo]
        ))


        # 不存在的字段: 暂时没有product_options和language code
        loader.add_value('language_code', review.get('LanguageCode', ''))
        loader.add_value('product_options', '')









