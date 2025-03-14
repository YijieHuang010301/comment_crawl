import json
import math
from datetime import datetime

import scrapy

from comment_crawl.common.const import OVERSTOCK_PLATFORM_ID
from comment_crawl.spiders.myspider import BaseSpider
from comment_crawl.util.crawl_util.push_to_redis import push_retry_url_to_redis


class OverstockSpider(BaseSpider):
    name = 'overstock_spider'
    redis_key = 'overstock_spider:urls'

    def __init__(self, *args, **kwargs):
        super(OverstockSpider, self).__init__(*args, **kwargs)
        self.platform_id = OVERSTOCK_PLATFORM_ID
        self.max_review_per_page = 100

    def make_request_from_data(self, data):
        data = json.loads(data)
        url = data['url']
        headers = data['headers']
        uuid = data['uuid']
        product_id = data['product_id']
        is_first_time = data['is_first_time']
        return scrapy.Request(
            url=url,
            method="GET",
            headers=headers,
            callback=self.parse,  # 回调函数处理响应
            meta={'product_id': product_id, 'uuid': uuid, 'is_first_time': is_first_time},  # 将 product_id 传递给下一个方法
            dont_filter=True,
            errback=self.handle_error
        )

    def parse_response_data(self, response, uuid, product_id, is_first_time):
        # print(response.text)
        # print()
        try:
            response_data = json.loads(response.text)  # 确保解析 JSON
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for product ID {product_id}: {str(e)}")
            return

        if is_first_time:
            total_reviews_count = response_data["totalItems"]
            self.save_rating_info(product_id, uuid, response_data)
            for i in range(0, math.ceil(total_reviews_count/self.max_review_per_page)):
                push_retry_url_to_redis(self.platform_id, product_id, uuid, i, 100)
        else:
            reviews = response_data["items"]
            self.save_reviews(product_id, reviews)



    def save_rating_info(self, product_id, uuid, customer_reviews_stats):
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        average_rating_value = 0
        total_reviews_count = customer_reviews_stats["totalItems"]
        rating_info = {
            'rating_count_total': total_reviews_count,
            'average_rating_value': average_rating_value,
            'rating_counts': rating_counts
        }

        self.save_rating_info_to_db(product_id, uuid, rating_info)
        pass

    def populate_review_loader(self, loader, review):
        loader.add_value('platform_id', self.platform_id)
        loader.add_value('review_id', review['reviewId'])
        loader.add_value('reviewer_name', review.get('screenName', '') or 'Anonymous')

        has_verified_buyer_status = review['verifiedPurchase']
        loader.add_value('is_verified', has_verified_buyer_status)

        if has_verified_buyer_status:
            verified_type = "verified_buyer"
        else:
            verified_type = "unverified_buyer"
        loader.add_value('verified_type', verified_type)

        review_date = datetime.utcfromtimestamp(review['submissionTime'] / 1000).strftime("%Y-%m-%d")
        loader.add_value('review_date', review_date)

        loader.add_value('rating_stars', review.get('rating'))
        loader.add_value('product_comments_title', review.get('reviewTitle') or '')
        loader.add_value('product_comments_content', review.get('reviewText') or '')
        loader.add_value('reviewer_location', review.get('reviewerLocation', '') or '')
        loader.add_value('review_helpful_count', review.get('numPositiveFeedback', 0))
        loader.add_value('review_unhelpful_count', review.get('numNegativeFeedback', 0))

        loader.add_value('is_recommended', review.get('isRecommended') or False)

        photosUrl = ','.join(image.get('full', '') for image in (review.get('images') or[]) if 'full' in image)
        loader.add_value('product_photos', photosUrl)

        thumbnailsUrl = ','.join(image.get('thumbnail', '') for image in  (review.get('images') or[]) if 'thumbnail' in image)
        loader.add_value('product_photos_thumbnail', thumbnailsUrl)

        loader.add_value('product_videos', review.get('reviewVideoList') or '')
        loader.add_value('product_options', review.get('optionName') or '')



        #不存在的
        loader.add_value('reviewer_id', -1)
        loader.add_value('language_code', '')
        return True
