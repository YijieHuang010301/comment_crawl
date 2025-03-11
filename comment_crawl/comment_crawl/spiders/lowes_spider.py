import json
import math
from datetime import datetime
import scrapy
from comment_crawl.common.const import LOWES_PLATFORM_ID
from comment_crawl.spiders.myspider import BaseSpider
from comment_crawl.util.crawl_util.push_to_redis import push_retry_url_to_redis


class WalmartSpider(BaseSpider):
    name = 'lowes_spider'
    redis_key = 'lowes_spider:urls'

    def __init__(self, *args, **kwargs):
        super(WalmartSpider, self).__init__(*args, **kwargs)
        self.platform_id = LOWES_PLATFORM_ID

    def make_request_from_data(self, data):
        data = json.loads(data)
        url = data['url']
        headers = data['headers']
        uuid = data['uuid']
        product_id = data['product_id']
        # payload = data['payload']
        is_first_time = data['is_first_time']

        return scrapy.Request(
            url=url,
            method="GET",
            headers=headers,
            #body=json.dumps(payload),  # 使用 body 传递 JSON 数据
            callback=self.parse,  # 回调函数处理响应
            meta={'product_id': product_id, 'uuid': uuid, 'is_first_time': is_first_time},  # 将 product_id 传递给下一个方法
            dont_filter=True,
            errback=self.handle_error
        )

    def parse_response_data(self, response, uuid, product_id, is_first_time):
        try:
            response_data = json.loads(response.text)  # 确保解析 JSON
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for product ID {product_id}: {str(e)}")
            return

        if is_first_time:
            total_reviews_count = response_data["reviewStatistics"]["totalReviewCount"]
            # TODO: 无法通过response判断商品是否下架

            if total_reviews_count > 0:
                #print(f'{product_id} is start parsing with total reviews count {total_reviews_count}')
                self.save_rating_info(product_id, uuid, response_data["reviewStatistics"])
                reviews_per_page = 10
                for i in range(math.ceil(total_reviews_count / reviews_per_page)):
                    start_idx = i + 1
                    push_retry_url_to_redis(self.platform_id, product_id, uuid, start_idx, total_reviews_count)
        else:
            reviews = response_data["results"]
            self.save_reviews(product_id, reviews)

    # process per review
    def populate_review_loader(self, loader, review):
        loader.add_value('platform_id', self.platform_id)
        loader.add_value('review_id', review['id'])
        loader.add_value('reviewer_name', review.get('userNickname', '') or 'Anonymous')
        loader.add_value('reviewer_id', review['authorReference']['id'])
        has_verified_buyer_status = review['verifiedPurchaser']
        loader.add_value('is_verified', has_verified_buyer_status)
        if has_verified_buyer_status:
            verified_type = "verified_buyer"
        else:
            verified_type = "unverified_buyer"
        loader.add_value('verified_type', verified_type)
        review_date = datetime.strptime(review['submissionTime'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
        loader.add_value('review_date', review_date)

        loader.add_value('rating_stars', review.get('rating'))
        loader.add_value('product_comments_title', review.get('title') or '')
        loader.add_value('product_comments_content', review.get('reviewText') or '')
        loader.add_value('language_code', review.get('contentLocale', '').split('_')[0])
        loader.add_value('reviewer_location', review.get('contentLocale', '').split('_')[1])
        loader.add_value('review_helpful_count', review.get('helpfulVoteCount', 0))
        loader.add_value('review_unhelpful_count', review.get('notHelpfulVoteCount', 0))

        loader.add_value('is_recommended', review.get('is_recommended', False))

        photosUrl = ','.join(review.get('photoUrls') or [])
        loader.add_value('product_photos', photosUrl)
        if photosUrl:
            product_photos_thumbnail = ','.join(
                photo['sizes']['thumbnail']['url'] for photo in review.get('photos', []) if
                'thumbnail' in photo.get('sizes', {})
            )
            loader.add_value('product_photos_thumbnail', product_photos_thumbnail)
        else:
            loader.add_value('product_photos_thumbnail', '')

        loader.add_value('product_videos', ','.join(review.get('videos') or []))

        ### 不存在字段
        loader.add_value('product_options', '')
        return True


    def save_rating_info(self, product_id, uuid, customer_reviews_stats):
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        average_rating_value = customer_reviews_stats["averageOverallRating"]
        rating_count_total = customer_reviews_stats["totalReviewCount"]
        histogram_stats = customer_reviews_stats.get("ratingDistribution", [])
        for stat in histogram_stats:
            rating = stat['ratingValue']
            count = stat['reviewCount']
            rating_counts[rating] = count

        rating_info = {
            'rating_count_total': rating_count_total,
            'average_rating_value': average_rating_value,
            'rating_counts': rating_counts
        }

        self.save_rating_info_to_db(product_id, uuid, rating_info)
