import json
from datetime import datetime
import scrapy


from comment_crawl.spiders.myspider import BaseSpider, insert_reviews_sql
from comment_crawl.common.const import WAYFAIR_PLATFORM_ID, WAYFAIR_COOKIES, DB_UPDATE

from comment_crawl.util.crawl_util.push_to_redis import push_retry_url_to_redis


# 每次可以爬取任意数量reviews
class WayfairSpider(BaseSpider):
    name = 'wayfair_spider'
    redis_key = 'wayfair_spider:urls'

    def __init__(self, *args, **kwargs):
        super(WayfairSpider, self).__init__(*args, **kwargs)

        self.platform_id = WAYFAIR_PLATFORM_ID
        # hash值在js里写死的
        self.params = {
            "hash": "a636f23a2ad15b342db756fb5e0ea093"
        }
        self.wayfair_max_reviews = self.max_reviews
        self.cookies = WAYFAIR_COOKIES

    def make_request_from_data(self, data):
        data = json.loads(data)
        url = data['url']
        headers = data['headers']
        uuid = data['uuid']
        product_id = data['product_id']
        payload = data['payload']
        is_first_time = data['is_first_time']


        return scrapy.Request(
            url=url,
            method="POST",
            headers=headers,
            cookies= self.cookies,
            body=json.dumps(payload),  # 使用 body 传递 JSON 数据
            callback=self.parse,  # 回调函数处理响应
            meta={'product_id': product_id, 'uuid': uuid, 'is_first_time': is_first_time},  # 可选：将 product_id 传递给下一个方法
            dont_filter=True,
            errback = self.handle_error
        )


    def parse_response_data(self, response, uuid, product_id, is_first_time):
        # 解析json
        try:
            response_data = json.loads(response.text)  # 确保解析 JSON
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for product ID {product_id}: {str(e)}")
            return

        customer_reviews = response_data['data']['product']['customerReviews']
        reviews = customer_reviews['reviews']
        ratingCount = customer_reviews['ratingCount']

        #如果读取的review数量少于总数，需要重新加入队列放大threshold
        # TODO: bugs here
        # 第一次更新总数据，并且记录rating总数据
        if is_first_time:
            self.save_rating_info(product_id, uuid, customer_reviews)
            push_retry_url_to_redis(self.platform_id, product_id, uuid, 1, ratingCount)
        # 非第一次更新评论数据
        else:
            if ratingCount > 0:
                self.save_reviews(product_id, reviews)

    def save_rating_info(self, product_id, uuid, customer_reviews_stats):
        rating_count_total = customer_reviews_stats['ratingCount']
        average_rating_value = customer_reviews_stats['averageRatingValue']
        histogram_stats = customer_reviews_stats.get('histogramStats', [])
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for stat in histogram_stats:
            rating = stat['rating']
            count = stat['count']
            rating_counts[rating] = count

        rating_info = {
            'rating_count_total': rating_count_total,
            'average_rating_value': average_rating_value,
            'rating_counts': rating_counts
        }

        self.save_rating_info_to_db(product_id, uuid, rating_info)

    def populate_review_loader(self, loader, review):
        loader.add_value('review_id', review['reviewId'])
        loader.add_value('reviewer_name', review.get('reviewerName'))
        loader.add_value('platform_id', self.platform_id)
        # 是否为验证购买
        has_verified_buyer_status = review.get('hasVerifiedBuyerStatus', False)
        loader.add_value('is_verified', has_verified_buyer_status)

        # 验证类型
        if has_verified_buyer_status:
            verified_type = "verified_buyer" if review.get("reviewerBadgeId", 1) == 0 else review.get(
                "reviewerBadgeText", "verified_buyer")
        else:
            verified_type = "unverified_buyer"
        loader.add_value('verified_type', verified_type)

        # 处理日期格式
        review_date = datetime.strptime(review['date'], "%m/%d/%Y").strftime("%Y-%m-%d")
        loader.add_value('review_date', review_date)

        # 其他字段处理
        # rating是0-10 需要变成0-5
        loader.add_value('rating_stars', int(review.get('ratingStars')) / 2)
        loader.add_value('product_comments_title', review.get('headline', ''))
        loader.add_value('product_comments_content', review.get('productComments', ''))
        loader.add_value('language_code', review.get('languageCode', ''))
        loader.add_value('reviewer_location', review.get('reviewerLocation', ''))
        loader.add_value('review_helpful_count', review.get('reviewHelpful', 0))
        loader.add_value('review_unhelpful_count', review.get('reviewUnhelpful', 0))

        # 多值字段的处理
        loader.add_value('product_photos_thumbnail', ','.join([photo['thumbnail'] for photo in review.get('customerPhotos', [])]))
        loader.add_value('product_photos', ','.join([photo['src'] for photo in review.get('customerPhotos', [])]))
        loader.add_value('product_options',
                         ','.join([f"{option['name']}:{option['value']}" for option in review.get('options', [])]))


        # 不存在的字段
        loader.add_value('product_videos','')
        loader.add_value('reviewer_id', '')
        loader.add_value('is_recommended', 0)
        return True


