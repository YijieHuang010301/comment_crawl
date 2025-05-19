
import json
import random

import hashlib
import time

from random import random

from comment_crawl.common.const import *
from comment_crawl.spiders.myspider import get_fake_mobile_user_agent, get_fake_user_agent
from comment_crawl.util.db_conn import select_data_from_db_by_platform

class HeaderFactory:
    @staticmethod
    def build_header(platform_id, product_id, uuid, is_first_time, start_idx, total_reviews, **kwargs):
        if platform_id == WAYFAIR_PLATFORM_ID:
            return HeaderFactory.build_wayfair_header(product_id, uuid, is_first_time, total_reviews)
        elif platform_id == HOMEDEPOT_PLATFORM_ID:
            return HeaderFactory.build_homedepot_header(product_id, uuid, is_first_time, start_idx, total_reviews)
        elif platform_id == AMAZON_PLATFORM_ID:
            return HeaderFactory.build_amazon_header(product_id, uuid, is_first_time, start_idx, **kwargs)
        elif platform_id == WALMART_PLATFORM_ID:
            return HeaderFactory.build_walmart_header(product_id, uuid)
        elif platform_id == OVERSTOCK_PLATFORM_ID or platform_id == BEDBATHANDBEYOND_PLATFORM_ID:
            # 共享构建方法
            return HeaderFactory.build_overstock_bedbathandbeyond_header(product_id, uuid, is_first_time, start_idx, total_reviews)
        elif platform_id == LOWES_PLATFORM_ID:
            return HeaderFactory.build_lowes_header(product_id, uuid, is_first_time, start_idx)
        else:
            raise ValueError(f"Unsupported platform_id: {platform_id}")

    @staticmethod
    def build_wayfair_header(product_id, uuid, is_first_time, total_reviews):
        url = "https://www.wayfair.com/graphql"
        headers = {
            "accept": "application/json",
            "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
            "apollographql-client-name": "@wayfair/sf-ui-product-details",
            "apollographql-client-version": "a335e00d97c883253ca972a643bc851e9c19dd80",
            "content-type": "application/json",
            "origin": "https://www.wayfair.com",
            "priority": "u=1, i",
            "referer": "https://www.wayfair.com/storage-organization/pdp/mercer41-36-pair-shoe-storage-cabinet-w110152845.html?piid=1983010793",
            "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "use-web-hash": "true",
            "user-agent": f'WayfairApp {WAYFAIR_APP_VERSION} Tablet({get_fake_mobile_user_agent()})',
            "x-parent-txid": "I+F9OmcNs/AS9I1ETVQTAg=="
        }

        variables = {
            "sku": product_id,
            "language_code": "en",
            "sort_order": "RELEVANCE",
            "reviews_per_page": total_reviews
        }
        # TODO: hash 需要规范下
        payload = {"hash": "a636f23a2ad15b342db756fb5e0ea093", "variables": variables}

        data = {
            'url': url,
            'product_id': product_id,
            'uuid': uuid,
            'headers': headers,
            'payload': payload,
            "is_first_time": is_first_time
        }
        return json.dumps(data)

    @staticmethod
    def build_homedepot_header(product_id, uuid, is_first_time, start_idx, total_reviews):
        url = "https://www.homedepot.com/federation-gateway/graphql?opname=reviews"
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'apollographql-client-name': 'hd-home',
            'apollographql-client-version': '0.0.0',
            'content-type': 'application/json',
            'origin': 'https://www.homedepot.com',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': get_fake_user_agent(),
            'x-api-cookies': '{}',
            'x-current-url': '',
            'x-debug': 'false',
            'x-experience-name': 'hd-home',
            'x-hd-dc': 'origin',
        }

        payload = {
            "operationName": "reviews",
            "variables": {
                "itemId": product_id,
                "pagesize": MAX_REVIEWS,
                "recfirstpage": MAX_REVIEWS,
                "searchTerm": None,
                "sortBy": "newest",
                "startIndex": start_idx
            },
            "query": "query reviews($itemId: String!, $searchTerm: String, $sortBy: String, $startIndex: Int, $recfirstpage: String, $pagesize: String, $filters: ReviewsFilterInput) {\n  reviews(itemId: $itemId, searchTerm: $searchTerm, sortBy: $sortBy, startIndex: $startIndex, recfirstpage: $recfirstpage, pagesize: $pagesize, filters: $filters) {\n    Results {\n      AuthorId\n      Badges {\n        DIY {\n          BadgeType\n          __typename\n        }\n        top250Contributor {\n          BadgeType\n          __typename\n        }\n        IncentivizedReview {\n          BadgeType\n          __typename\n        }\n        EarlyReviewerIncentive {\n          BadgeType\n          __typename\n        }\n        top1000Contributor {\n          BadgeType\n          __typename\n        }\n        VerifiedPurchaser {\n          BadgeType\n          __typename\n        }\n        __typename\n      }\n      BadgesOrder\n      CampaignId\n      ContextDataValues {\n        Age {\n          Value\n          __typename\n        }\n        VerifiedPurchaser {\n          Value\n          __typename\n        }\n        __typename\n      }\n      ContextDataValuesOrder\n      Id\n      IsRecommended\n      IsSyndicated\n      Photos {\n        Id\n        Sizes {\n          normal {\n            Url\n            __typename\n          }\n          thumbnail {\n            Url\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      ProductId\n      SubmissionTime\n      TagDimensions {\n        Pro {\n          Values\n          __typename\n        }\n        Con {\n          Values\n          __typename\n        }\n        __typename\n      }\n      Title\n      TotalNegativeFeedbackCount\n      TotalPositiveFeedbackCount\n      ClientResponses {\n        Response\n        Date\n        Department\n        __typename\n      }\n      Rating\n      RatingRange\n      ReviewText\n      SecondaryRatings {\n        Quality {\n          Label\n          Value\n          __typename\n        }\n        Value {\n          Label\n          Value\n          __typename\n        }\n        EnergyEfficiency {\n          Label\n          Value\n          __typename\n        }\n        Features {\n          Label\n          Value\n          __typename\n        }\n        Appearance {\n          Label\n          Value\n          __typename\n        }\n        EaseOfInstallation {\n          Label\n          Value\n          __typename\n        }\n        EaseOfUse {\n          Label\n          Value\n          __typename\n        }\n        __typename\n      }\n      SecondaryRatingsOrder\n      SyndicationSource {\n        LogoImageUrl\n        Name\n        __typename\n      }\n      UserNickname\n      UserLocation\n      Videos {\n        VideoId\n        VideoThumbnailUrl\n        VideoUrl\n        __typename\n      }\n      __typename\n    }\n    Includes {\n      Products {\n        store {\n          Id\n          FilteredReviewStatistics {\n            AverageOverallRating\n            TotalReviewCount\n            TotalRecommendedCount\n            RecommendedCount\n            NotRecommendedCount\n            SecondaryRatingsAveragesOrder\n            RatingDistribution {\n              RatingValue\n              Count\n              __typename\n            }\n            ContextDataDistribution {\n              Age {\n                Values {\n                  Value\n                  Count\n                  __typename\n                }\n                __typename\n              }\n              Gender {\n                Values {\n                  Value\n                  Count\n                  __typename\n                }\n                __typename\n              }\n              Expertise {\n                Values {\n                  Value\n                  __typename\n                }\n                __typename\n              }\n              HomeGoodsProfile {\n                Values {\n                  Value\n                  Count\n                  __typename\n                }\n                __typename\n              }\n              VerifiedPurchaser {\n                Values {\n                  Value\n                  Count\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n\n        __typename\n      }\n      __typename\n    }\n        pagination {\n      previousPage {\n        label\n        isNextPage\n        isPreviousPage\n        isSelectedPage\n        __typename\n      }\n      pages {\n        label\n        isNextPage\n        isPreviousPage\n        isSelectedPage\n        __typename\n      }\n      nextPage {\n        label\n        isNextPage\n        isPreviousPage\n        isSelectedPage\n        __typename\n      }\n      __typename\n    }\n    TotalResults\n    __typename\n  }\n}\n"
        }

        data = {
            'url': url,
            'product_id': product_id,
            'uuid': uuid,
            'headers': headers,
            'is_first_time': is_first_time,
            'payload': payload
        }

        return json.dumps(data)

    @staticmethod
    def build_amazon_header(product_id, uuid, is_first_time, page_num, **kwargs):
        # TODO: 实现Amazon的header构建逻辑
        url = f'https://www.amazon.com/product-reviews/{product_id}'

        if not is_first_time:
            sorted_by = kwargs.get("sortedBy", "recent")
            filtering = kwargs.get("filtering", "all_stars")
            url += f'/ref=cm_cr_arp_mb_viewopt_srt?sortBy={sorted_by}&filterByStar={filtering}&pageNumber={page_num}'

        data = {
            'url': url,
            'product_id': product_id,
            'uuid': uuid,
            'is_first_time': is_first_time,
        }
        return json.dumps(data)

    @staticmethod
    def build_lowes_header(product_id, uuid, is_first_time, start_idx):
        # TODO: 实现lowes的header构建逻辑
        url = f'https://www.lowes.com/rnr/r/get-by-product/{product_id}'

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8',
            'priority': 'u=1, i',
            'referer': '',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': get_fake_user_agent(),
        }

        offset = (start_idx - 1) * 10

        # payload = {
        #     'offset': str(offset),
        #     'sortBy': 'newestFirst',
        # }
        url += f'?offset={offset}&sortBy=newestFirst'

        data = {
            'url': url,
            'product_id': product_id,
            'uuid': uuid,
            'headers': headers,
            'is_first_time': is_first_time,
        }
        return json.dumps(data)

    @staticmethod
    def build_overstock_bedbathandbeyond_header(product_id, uuid, is_first_time, page_num, total_reviews):
        # TODO: 实现Overstock和BedBath&Beyond的header构建逻辑
        url = "https://api.overstock.com/reviews"
        headers = {
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://www.overstock.com',
            'pragma': 'no-cache',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': get_fake_user_agent()
        }
        if is_first_time:
            next_page_num = 0
        else:
            next_page_num = page_num
        params = {
            'productId': product_id,  # 商品id
            'page': next_page_num,  # 页码
            'sortBy': 'recentReview',  # 时间倒序排列
            'limit': total_reviews,  # 每页数量
        }
        url += f"?productId={params['productId']}&page={params['page']}&sortBy={params['sortBy']}&limit={params['limit']}"
        data = {
            'url': url,
            'product_id': product_id,
            'uuid': uuid,
            'headers': headers,
            'is_first_time': is_first_time,
        }

        return json.dumps(data)

    @staticmethod
    def build_walmart_header(product_id, uuid):
        # TODO: 实现walmart的header构建逻辑
        def md5_encrypt(self, string):
            '''
            'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
            'blake2b', 'blake2s',
            'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
            'shake_128', 'shake_256'
            '''
            md5 = hashlib.md5()
            md5.update(string.encode('utf-8'))
            return md5.hexdigest()

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            f"F{md5_encrypt(str(time.time()))[:5]}": f"{md5_encrypt(str(random.randint(1, 10000)))}",
            "Sec-Ch-Ua": f"\"Not A(Brand\";v=\"{random.randint(70, 99)}\", \"Brave\";v=\"{random.randint(70, 120)}\", \"Chromium\";v=\"{random.randint(70, 120)}\"",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(512, 538)}.{random.randint(9, 37)} (KHTML, like Gecko) Chrome/{random.randint(100, 121)}.0.0.0 Safari/{random.randint(512, 538)}.{random.randint(9, 37)}",
        }


        pass

def push_urls_to_redis_by_platform(platform_id):
    from comment_crawl.main import redis_conn
    """
    定时任务：从数据库读取URL并推入Redis
    """
    res, error = select_data_from_db_by_platform(platform_id)
    redis_key = platform_redis_key_map.get(platform_id)
    is_first_time = True

    for row in res:
        url, product_id, uuid = row
        data = HeaderFactory.build_header(platform_id, product_id, uuid, is_first_time, 1, 10)
        redis_conn.lpush(redis_key, data)
        print(f'[First Time] Pushed product: {product_id} to Redis')

def push_retry_url_to_redis(platform_id, product_id, uuid, start_idx, total_reviews, **kwargs):
    from comment_crawl.main import redis_conn
    """
    将需要重试的URL推入Redis
    """
    is_first_time = False
    redis_key = platform_redis_key_map.get(platform_id)
    data = HeaderFactory.build_header(platform_id, product_id, uuid, is_first_time, start_idx, total_reviews, **kwargs)
    redis_conn.lpush(redis_key, data)
    print(f'[Retry] Pushed product: {product_id} to Redis')



