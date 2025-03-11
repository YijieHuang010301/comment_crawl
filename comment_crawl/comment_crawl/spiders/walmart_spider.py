import json

from comment_crawl.common.const import WALMART_PLATFORM_ID
from comment_crawl.spiders.myspider import BaseSpider



class WalmartSpider(BaseSpider):
    # TODO: 未完成
    name = 'walmart_spider'
    redis_key = 'walmart_spider:urls'

    def __init__(self, *args, **kwargs):
        super(WalmartSpider, self).__init__(*args, **kwargs)
        self.platform_id = WALMART_PLATFORM_ID

    def make_request_from_data(self, data):
        data = json.loads(data)
        url = data['url']
        headers = data['headers']
        uuid = data['uuid']
        product_id = data['product_id']
        payload = data['payload']
        is_first_time = data['is_first_time']


    def parse_response_data(self, response_data, uuid, product_id, is_first_time):

        pass

