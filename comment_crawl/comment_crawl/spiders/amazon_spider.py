import json
import math
import re
import threading
import time
import random

import requests
import scrapy

from datetime import datetime
from lxml import etree

from comment_crawl.common.const import AMAZON_PLATFORM_ID
from comment_crawl.spiders.myspider import BaseSpider, get_fake_user_agent
from comment_crawl.util.crawl_util.push_to_redis import push_retry_url_to_redis


class AmazonSpider(BaseSpider):
    # TODO: 因为考虑后期维护，暂时考虑使用第三方api解决
    # TODO: 此解决方案解析html，可能会随网页升级失效，后期维护困难。
    name = 'amazon_spider'
    redis_key = 'amazon_spider:urls'
    def __init__(self, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.platform_id = AMAZON_PLATFORM_ID
        self.review_per_page = 10
        self.max_review_page = 10
        self.sorted_by_options = ["top", "recent"]
        self.cookies = {
            "session-id": "142-5966024-7696716",
            "x-main": "\"n@EDwbAhxgxU1AU1GPqHkmx1uH2PkR2Bf4cxIlfSTaJLf5NVIs0y@UTCNpp5lI7a\"",
            "at-main": "Atza|IwEBIARmwUgrbI7aaRivNEA1i8Gn2_lYAKRfrjDbHAGCZjUfxyLGL7B21egjeOaT3XT-jfy0J28IFRteKi0rZd37jlpX7G5a5AhX67ETi1jnYlPzIk46qOfujarFVyGGPJ4ETbf1xE_Rfgc3j8D_TVpeJhgdSkIRQa3K52ApopVUpKiQOezrN6fT7cc2IHFOcghpoQc4U6Oa9nI8x4NLHRbAY_4bXpXSozu4BVJYLGthgHxs7g",
            "sess-at-main": "\"I4ST3WOJ+5VxQhdQX3yGkvWIuFvQhja4lUpR5/+raZo=\"",
            "aws-target-data": "%7B%22support%22%3A%221%22%7D",
            "i18n-prefs": "USD",
            "lwa-context": "67804cd8205046edc43dd659d3290309",
            "session-id-time": "2082787201l",
            "aws_lang": "cn",
            "AMCVS_7742037254C95E840A4C98A6%40AdobeOrg": "1",
            "s_cc": "true",
            "aws-mkto-trk": "id%3A112-TZM-766%26token%3A_mch-aws.amazon.com-1726862760901-81638",
            "AMCV_7742037254C95E840A4C98A6%40AdobeOrg": "1585540135%7CMCIDTS%7C19999%7CMCMID%7C91533090113266480473442688361025228582%7CMCAAMLH-1728510654%7C9%7CMCAAMB-1728510654%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1727913054s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0",
            "aws-target-visitor-id": "1711426409907-731209.45_0",
            "lc-main": "en_US",
            "session-token": "1sDMgjTGpdtghVcVKBNC6CoazQU0Re4N4otJn4H7pq7MNWB7HD0owJ2T0IBmjp59eAqBRUGqMcYcO8QzTmnKe9LVym/e2X1U/SQ63djHDFxVf234gpxM/7ByDKy+Z9Y4Wx3z/4zz6kGFpJxkpfFNDH/I332sqJt6tqc/zhva3xSPUsninLp1NlGzA6PKjH4jNypK/e5YtCezBpu4oc3J/1Pg90Q5ErBhkG4xmzNSaHd6FTgsutgdEwFv58TtrcAa3dLSJD0MomCxtggPnvdn55cfrtfKSvD8c+TVAysEsaX19qXRNAQsWdIVFIYyehleRTdd/bfUUW56eMMil+sF/8Ygq9tIK8NGuG3p/Qo7gNEpu1i489emxtLUTb3bp1De",
            "csm-hit": "s-MM5E4EFQ1RP1HBXZHB0J|1732413326353"
        }
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
            "cache-control": "max-age=0",
            "device-memory": "8",
            "downlink": "5.7",
            "dpr": "2",
            "ect": "4g",
            "priority": "u=0, i",
            "rtt": "100",
            "sec-ch-device-memory": "8",
            "sec-ch-dpr": "2",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-ch-viewport-width": "161",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": get_fake_user_agent(),
        }
        self.amazon_url =  "https://www.amazon.com/product-reviews"

        threading.Thread(target=self.update_cookies_task, daemon=True).start()

    def make_request_from_data(self, data):
        data = json.loads(data)
        url = data['url']
        uuid = data['uuid']
        product_id = data['product_id']
        is_first_time = data['is_first_time']

        return scrapy.Request(
            url=url,
            method="POST",
            headers=self.headers,
            cookies = self.cookies,
            callback=self.parse,  # 回调函数处理响应
            meta={'product_id': product_id, 'uuid': uuid, 'is_first_time': is_first_time},  # 将 product_id 传递给下一个方法
            dont_filter=True,
            errback=self.handle_error
        )


    def parse_response_data(self, response, uuid, product_id, is_first_time):

        try:
            response_html_etree = etree.HTML(response.text)  # 确保解析 HTML
        except json.JSONDecodeError as e:
            print(f"Error parsing HTML response for product ID {product_id}: {str(e)}")
            return
        # self.write_to_log(response.text, product_id, self.platform_id)

        # 储存rating的信息
        if is_first_time:
            #存储总的rating信息，并且把需要爬取的网址按照filter加入redis
            self.save_rating_info(product_id, uuid, None)
        else:# 解析html
            reviews = response_html_etree.xpath('//div[@id="cm_cr-review_list"]//li')
            self.save_reviews(product_id, reviews)

    def save_rating_info(self, product_id, uuid, customer_reviews_stats):
        rating_counts = self.get_each_rating_info_by_requests(product_id, uuid)

        # 计算总评分数量
        rating_count_total = sum(rating_counts.values())
        print(rating_counts)
        # 计算平均评分
        weighted_sum = sum(star * count for star, count in rating_counts.items())
        average_rating_value = weighted_sum / rating_count_total if rating_count_total > 0 else 0

        rating_info = {
            'rating_count_total': rating_count_total,
            'average_rating_value': average_rating_value,
            'rating_counts': rating_counts
        }
        self.save_rating_info_to_db(product_id, uuid, rating_info)

    def populate_review_loader(self, loader, review):
        # 解析html

        review_id = review.xpath('.//@id') # Fetch the `id` attribute

        if len(review_id) == 0:
            print("Cannot get review id")
            return False
        review_id = review_id[0]

        loader.add_value('review_id', review_id)
        loader.add_value('platform_id', self.platform_id)
        # 提取用户名
        reviewer_name = review.xpath(".//div[@class='a-profile-content']/span/text()")
        reviewer_name = " ".join([name.strip() for name in reviewer_name]) if reviewer_name else "Anonymous"
        loader.add_value('reviewer_name', reviewer_name)

        #用户认证情况
        verified_type = review.xpath(".//span[@data-hook='msrp-avp-badge-linkless']/text()")
        verified_type = ",".join([v_type.strip().lower() for v_type in verified_type]) if verified_type else "unverified buyer"
        is_verified = True
        if verified_type == "unverified buyer":
            is_verified = False

        loader.add_value('is_verified', is_verified)
        loader.add_value('verified_type', verified_type)

        # 提取评论日期
        review_date_location = review.xpath(".//span[@data-hook='review-date']/text()")
        # 设置默认值
        reviewer_location = ""
        review_date = "1970-01-01"

        # 确保 review_date_location 非空
        if review_date_location:
            review_date_location_text = review_date_location[0].strip()  # 获取第一个匹配项
            if "Reviewed in " in review_date_location_text:
                parts = review_date_location_text.split("Reviewed in ")
                if len(parts) > 1 and " on " in parts[1]:
                    reviewer_location = parts[1].split(" on ")[0].strip()  # 提取地区
                    date_text = parts[1].split(" on ")[1].strip()  # 提取日期
                    # 转换日期格式
                    try:
                        review_date = datetime.strptime(date_text, "%B %d, %Y").strftime("%Y-%m-%d")
                    except ValueError:
                        review_date = ""  # 如果日期格式不正确，保持为空

        loader.add_value('review_date', review_date)
        loader.add_value('reviewer_location', reviewer_location)

        # 提取评论评分
        rating_text = review.xpath(".//i[@data-hook='review-star-rating']/span/text()")
        if rating_text:
            rating = int(float(rating_text[0].split(" out of")[0]))  # 提取评分并转换为整数
        else:
            rating = -1
        loader.add_value('rating_stars', rating)

        # 提取评论标题
        title = review.xpath(".//*[@data-hook='review-title']/span/text()")
        title = title[0].strip()
        print(title)

        loader.add_value('product_comments_title', title or '')

        # 提取评论正文
        body = review.xpath('.//span[@data-hook="review-body" and @class="review-text-sub-contents"]/text()')
        body = " ".join([text.strip() for text in body])
        loader.add_value('product_comments_content', body or '')
        print(body)

        # 评论点赞数
        helpful_counts = 0
        helpful_counts_text = review.xpath(".//span[@data-hook='helpful-vote-statement']/text()")
        if helpful_counts_text:
            helpful_votes_text = helpful_counts_text[0].strip()  # 提取第一个文本并去掉空格
            first_word = helpful_votes_text.split(" ")[0]  # 提取第一个单词
            if first_word == "One":
                helpful_counts = 1
            elif first_word.isdigit():  # 确保是数字后再转换
                helpful_counts = int(first_word)
        loader.add_value('review_helpful_count', helpful_counts)

        # 产品具体信息
        product_option = review.xpath(".//span[@data-hook='format-strip-linkless']/text()")
        product_options = " ".join([option.strip() for option in product_option])
        loader.add_value('product_options', product_options or '')

        #提取照片地址
        review_image_urls = review.xpath(".//div[@class='review-image-thumbnail']/@style")
        image_urls = []
        # 遍历每个 style 属性并提取 URL
        for style_attribute in review_image_urls:
            url_start = style_attribute.find("url(") + 4
            url_end = style_attribute.find(")", url_start)
            if url_start >= 4 and url_end != -1:  # 确保找到 "url(" 和 ")"
                image_url = style_attribute[url_start:url_end].strip('"')  # 去掉可能的双引号
                image_urls.append(image_url)

        # 将 URL 列表拼接成逗号分隔的字符串
        image_urls_str = ','.join(image_urls)
        loader.add_value('product_photos', image_urls_str)

        # 解析视频
        video_elements = review.xpath('.//video[@class="cr-review-video-thumbnail cr-review-video-thumbnail-mash"]')
        # 提取 <source> 标签中的视频 URL
        if video_elements:
            video_sources = video_elements[0].xpath('./source/@src')  # 提取 <source> 标签的 src 属性
        else:
            video_sources = ''
        loader.add_value('product_videos', video_sources)


        #不存在的值
        loader.add_value('reviewer_id', '')
        loader.add_value('is_recommended', False)
        loader.add_value('review_unhelpful_count', 0)
        loader.add_value('language_code', '')
        loader.add_value('product_photos_thumbnail', '')
        return True



    def get_each_rating_info_by_requests(self, product_id, uuid):
        star_mapping = {
            "one_star": 1,
            "two_star": 2,
            "three_star": 3,
            "four_star": 4,
            "five_star": 5
        }
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for suffix in star_mapping.keys():
            # 随机延迟
            # time.sleep(random.uniform(0.5, 1))

            rating_url = self.amazon_url + f'''/{product_id}/ref=cm_cr_unknown'''
            params = {
                "filterByStar": suffix,  # 添加当前星级过滤参数
            }
            # 发起请求
            rating_response = requests.post(rating_url, headers=self.headers, cookies=self.cookies, params=params)
            rating_etree = etree.HTML(rating_response.text)


            try:
                # 提取当前星级的评价数量
                rating_total, num_reviews = self.extract_rating_info(rating_etree)
                star_level = star_mapping[suffix]  # 将 suffix 转换为对应的星级
                rating_counts[star_level] = rating_total
                self.send_new_request_by_filter(suffix, num_reviews, product_id, uuid)

            except Exception as e:
                print(f"{product_id} 解析 {suffix} 星级信息失败: {e}")

        return rating_counts

    def extract_rating_info(self, input_html):
        try:
            # 提取包含总评价数和评论数的文本
            element = input_html.xpath('//div[@data-hook="cr-filter-info-review-rating-count"]/text()')
            if not element:
                raise ValueError("未找到匹配的 XPath 元素")

            text = element[0].strip()


            # 使用正则表达式提取数字并去掉逗号
            numbers = re.findall(r'\d[,?\d]*', text)
            numbers = [int(num.replace(',', '')) for num in numbers]

            # 检查提取结果是否包含两个数字
            if len(numbers) != 2:
                raise ValueError("提取的数字数量不正确，应包含两个数字")

            return numbers
        except Exception as e:
            print(f"提取评分信息失败: {e}")


    def update_cookies_task(self):
        while True:
            cookies = {}
            url = "https://www.amazon.com/product-reviews"
            response = requests.get(url, headers = self.headers, cookies=cookies)
            self.cookies.update(response.cookies.get_dict())
            self.logger.info(f"Cookies updated: {self.cookies}")
            time.sleep(300)

    def send_new_request_by_filter(self, rating_level, num_reviews, product_id, uuid):
        #return

        page_num = math.ceil(num_reviews / self.review_per_page)
        max_page_num_idx = min(page_num, self.max_review_page)
        # 把剩下所有page从第二页开始都加入队列等待爬取 最多10页 一页10个

        for curr_page in range(1, max_page_num_idx + 1):
            for sorted_by in self.sorted_by_options:
                sorted_args = {"sortedBy": sorted_by, "filtering": rating_level}
                push_retry_url_to_redis(self.platform_id, product_id, uuid, curr_page, num_reviews, **sorted_args)






