# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy

class ReviewItem(scrapy.Item):
    platform_id = scrapy.Field()
    product_id = scrapy.Field()

    review_id = scrapy.Field()

    reviewer_name = scrapy.Field(default='Anonymous')
    reviewer_id = scrapy.Field()

    is_verified = scrapy.Field()
    verified_type = scrapy.Field()

    review_date = scrapy.Field()

    rating_stars = scrapy.Field()
    product_comments_title = scrapy.Field()
    product_comments_content = scrapy.Field()

    language_code = scrapy.Field()
    reviewer_location = scrapy.Field()
    is_recommended = scrapy.Field(default=False)
    review_helpful_count = scrapy.Field(default=0)
    review_unhelpful_count = scrapy.Field(default=0)
    product_photos = scrapy.Field(defualt='')
    product_photos_thumbnail = scrapy.Field(defualt='')
    product_videos = scrapy.Field(defualt='')
    product_options = scrapy.Field()
    update_time = scrapy.Field()

