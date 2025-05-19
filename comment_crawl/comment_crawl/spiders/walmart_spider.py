import json
import math
import random
import time

import requests
import scrapy
from lxml import etree

from comment_crawl.common.const import WALMART_PLATFORM_ID
from comment_crawl.spiders.myspider import BaseSpider
from comment_crawl.util.crawl_util.push_to_redis import push_retry_url_to_redis


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
        cookies = {
            "_pxvid": self._pxvid_get(input_headers=headers),
        }
        return scrapy.Request(
            url=url,
            method="GET",
            headers=headers,
            cookies=cookies,
            body=json.dumps(payload),  # 使用 body 传递 JSON 数据
            callback=self.parse,  # 回调函数处理响应
            meta={'product_id': product_id, 'uuid': uuid, 'is_first_time': is_first_time},  # 可选：将 product_id 传递给下一个方法
            dont_filter=True,
            errback=self.handle_error
        )

    def _pxvid_get(self, input_headers):
        hosturl = "https://www.walmart.com/"
        '''获取临时令牌'''
        # url 混淆服务器的路径
        url = f"{hosturl}reviews/product/{random.randint(1, 10000)}{str(time.time())}{str(random.randint(1, 10000))}{str(time.time())}{str(random.randint(1, 10000))}"
        # 使用 head 请求，不请求正文资源，只请求响应头，【正文没有用，都是一些我们不需要的东西，而且还浪费流量】
        # verify 关闭证书验证，可以更快的获取到响应头，虽然会返回404或其他状态码，但丝毫不影响我们参数获取
        response = requests.head(url, headers=input_headers, verify=False)
        # 从 cookie 里获取 _pxhd 数据信息，然会提取出 _pxvid 参数
        _pxvid = response.cookies.get('_pxhd').split(':')[-1]
        print(f'获取到令牌 {_pxvid}')
        return _pxvid

    def parse_response_data(self, response_data, uuid, product_id, is_first_time):
        try:
            response_html_etree = etree.HTML(response_data.text)  # 确保解析 HTML
        except json.JSONDecodeError as e:
            print(f"Error parsing HTML response for product ID {product_id}: {str(e)}")
            return
        script_element = response_html_etree.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if not script_element:
            print(f"__NEXT_DATA__ not found for product ID {product_id}")
            return
        json_str = script_element[0]
        data = json.loads(json_str)
        reviews_data = data["props"]["pageProps"]["initialData"]["data"]["reviews"]
        rating_count_total = reviews_data["pagination"]["total"]
        if is_first_time:
            self.save_rating_info(product_id, uuid, reviews_data)
            for i in range(1, math.ceil(rating_count_total / 10)):
                push_retry_url_to_redis(self.platform_id,product_id,uuid,i,)

        pass

    def save_rating_info(self, product_id, uuid, customer_reviews_stats):
        average_rating_value = customer_reviews_stats.get("averageOverallRating", 0)
        rating_count_total = customer_reviews_stats["pagination"]["total"]
        rating_counts = {
            1: customer_reviews_stats.get("ratingValueOneCount", 0),
            2: customer_reviews_stats.get("ratingValueTwoCount", 0),
            3: customer_reviews_stats.get("ratingValueThreeCount", 0),
            4: customer_reviews_stats.get("ratingValueFourCount", 0),
            5: customer_reviews_stats.get("ratingValueFiveCount", 0),
        }


        rating_info = {
            'rating_count_total': rating_count_total,
            'average_rating_value': average_rating_value,
            'rating_counts': rating_counts
        }
        self.save_rating_info_to_db(product_id, uuid, rating_info)


