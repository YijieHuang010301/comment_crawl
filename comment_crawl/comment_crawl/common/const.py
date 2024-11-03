AMAZON_PLATFORM_ID = 1
WAYFAIR_PLATFORM_ID = 2
WALMART_PLATFORM_ID = 3
HOMEDEPOT_PLATFORM_ID = 4
# 属于同平台
OVERSTOCK_PLATFORM_ID = 5
BEDBATHANDBEYOND_PLATFORM_ID = 5

LOWES_PLATFORM_ID = 6


platforms = {
    'amazon.com': {'id': AMAZON_PLATFORM_ID, 'name': 'amazon'},
    'wayfair.com': {'id': WAYFAIR_PLATFORM_ID, 'name': 'wayfair'},
    'wayfair.ca' : {'id': WAYFAIR_PLATFORM_ID, 'name': 'wayfair'},
    'walmart.com': {'id': WALMART_PLATFORM_ID, 'name': 'walmart'},
    'homedepot.com': {'id': HOMEDEPOT_PLATFORM_ID, 'name': 'homedepot'},
    'overstock.com': {'id': OVERSTOCK_PLATFORM_ID, 'name': 'overstock'},
    'bedbathandbeyond.com': {'id': BEDBATHANDBEYOND_PLATFORM_ID, 'name': 'bedbathandbeyond'},
    'lowes.com': {'id': LOWES_PLATFORM_ID, 'name': 'lowes'}
}

platform_redis_key_map = {
    AMAZON_PLATFORM_ID: "amazon_spider:urls",
    WAYFAIR_PLATFORM_ID: "wayfair_spider:urls",
    WALMART_PLATFORM_ID: "walmart_spider:urls",
    HOMEDEPOT_PLATFORM_ID: "homedepot_spider:urls",
    OVERSTOCK_PLATFORM_ID: "overstock_spider:urls",
    BEDBATHANDBEYOND_PLATFORM_ID: "overstock_spider:urls",  # 同一平台共享Redis键
    LOWES_PLATFORM_ID: "lowes_spider:urls"
}


ALL_PRODUCTS_TABLE = 'all_products'
PRODUCT_REVIEWS_TABLE = 'product_reviews'
MAX_REVIEWS = 100

DB_SELECT = "select"
DB_INSERT = "insert"
DB_UPDATE = "update"
DB_DELETE = "delete"

WAYFAIR_APP_VERSION = "5.273.2"

WAYFAIR_COOKIES = {
    "CSNUtId": "23e9f4e3-5eff-f7d1-8662-0fc49b3d0302",
    "ExCSNUtId": "23e9f4e3-5eff-f7d1-8662-0fc49b3d0302",
    "_RCRTX03-samesite": "a5b70349620f11ee8fc8f95f7c84a197a71b0da1a83347fea8932b1026428a4a",
    "SFSID": "e76ade11b3f1cb9738a523e36b67ad17",
    "canary": "0",
    "serverUAInfo": "%7B%22browser%22%3A%22Google%20Chrome%22%2C%22browserVersion%22%3A128%2C%22OS%22%3A%22Mac%20OS%20X%22%2C%22OSVersion%22%3A%22%22%2C%22isMobile%22%3Afalse%2C%22isTablet%22%3Afalse%2C%22isTouch%22%3Afalse%7D",
    "pxcts": "60e617a8-6fcb-11ef-9b1e-4f5e37500995",
    "_pxvid": "60e604b1-6fcb-11ef-9b1e-3335ee86bf33",
    "_wf_fs_sample_user": "false",
    "postalCode": "61820",
    "__ssid": "ef3fc61cff14bcd1847d3f7fde1d666",
    "sm_uuid": "1726010980032",
    "cjConsent": "MHxOfDB8Tnww",
    "cjUser": "66caae41-f6eb-426c-aab0-bb9346263910",
    "_gcl_aw": "GCL.1726010478.CjwKCAjw3P-2BhAEEiwA3yPhwJFDq2i-WmfWVg8aUIntEuIFKNqXr85jeSofFxqHc_-fH2m2IuAyJBoCGGYQAvD_BwE",
    "_gcl_au": "1.1.1130477814.1726010478",
    "__attentive_id": "cf7a0a7859b7404681b44e7414a4a041",
    "_attn_": "eyJ1Ijoie1wiY29cIjoxNzI2MDEwNDc3OTM2LFwidW9cIjoxNzI2MDEwNDc3OTM2LFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcImNmN2EwYTc4NTliNzQwNDY4MWI0NGU3NDE0YTRhMDQxXCJ9In0=",
    "__attentive_cco": "1726010477939",
    "_gcl_gs": "2.1.k1$i1726010475",
    "_tt_enable_cookie": "1",
    "_ttp": "O3GslBGZPcosySyyMp16DZRNjPE",
    "__podscribe_wayfair_referrer": "https://www.google.com/",
    "__podscribe_wayfair_landing_url": "https://www.wayfair.com/gateway.php?refid=GX281264597885.Wayfair%7Eb&position=&network=g&pcrid=281264597885&device=c&targetid=kwd-3598608535&channel=GoogleBrand&gad_source=1&gclid=CjwKCAjw3P-2BhAEEiwA3yPhwJFDq2i-WmfWVg8aUIntEuIFKNqXr85jeSofFxqHc_-fH2m2IuAyJBoCGGYQAvD_BwE",
    "__podscribe_did": "pscrb_f5c2899d-64f9-46d2-db24-e110d2b95dbe",
    "rskxRunCookie": "0",
    "rCookie": "ro2nwrjilgq425tunl2cm0x22oer",
    "IR_gbd": "wayfair.com",
    "_gac_UA-2081664-4": "1.1726010478.CjwKCAjw3P-2BhAEEiwA3yPhwJFDq2i-WmfWVg8aUIntEuIFKNqXr85jeSofFxqHc_-fH2m2IuAyJBoCGGYQAvD_BwE",
    "i18nPrefs": "lang%3Den-US",
    "salsify_session_id": "5447cdf1-f4f6-4a5e-b117-48c807021b2d",
    "ndp_session_id": "f6bed165-0da1-44b8-bb6f-6a6c5593338b",
    "AppInterstitial": "visit_date_1%3D2024-09-24",
    "CSNBrief": "is_new_user=1&refid=GX281264597885.Wayfair~b",
    "TopNavCSSCachedByBrowser": "true",
    "featureDetect": "{\"isTouch\":false,\"hasMQ\":true,\"deviceWidth\":1440,\"deviceHeight\":778,\"devicePixelRatio\":2}",
    "_ga_1FPVXH256H": "GS1.2.1727227307.1.1.1727227310.0.0.0",
    "cjLiveRampLastCall": "2024-10-01T00:02:12.721Z",
    "otx": "I+F9Omb7Visc9oxDOHjvAg==",
    "WFDC": "DSM",
    "vid": "23e17d3a-670d-b39f-07b5-23c4cf147302",
    "CSN_CSRF": "cad1ef5adc38e814d0c5eed2338e0ffe829ae94e956e9ba75976aaa0297d7611",
    "pdp-views-count": "1",
    "_dpm_ses.15e8": "*",
    "__attentive_ss_referrer": "ORGANIC",
    "__attentive_dv": "1",
    "_gid": "GA1.2.357840650.1728951204",
    "__wid": "217565407",
    "hideGoogleYolo": "true",
    "_px3": "6f64902a5ded6b53ddc496a4b3409923c7782267e797a485c1b2455f60f259f3:v3Gt7+X/8aHa9NPKl9/EQsAEN4JCZYYuKs/DhFIZPMf+5yjLh7E7xqMA/bpHK+IqjIzHrnpYR1crEkYWi9OWTQ==:1000:fiK5fEsbZLrjStOPhOJ4wk4zmZTWKghkUC1HGt/aA93AjIqdCH1CHCB2DjHfSRgO7jMHF+pc+46mvN0XYz+XdOKSCmy2nkPLnImmJDw8yA7VNbBwdD2/oSdGvXIlQEU9FqfVBRz9VZNRe/2atDtcdrtwBkI9wGlaP5wnfg3WjtoM+gmH9XdRJoCk4ZC/P7MnOYppJe3ZyYX+x+MdcdOAQFTgVRmJMnJ7fOm9GD4TW2I=",
    "_dpm_id.15e8": "f144759b-2dcf-4c26-909e-1d98bb75c61d.1726010478.14.1728951285.1728504277.ca81381f-cf97-45a1-8d6a-6e245d2f6325",
    "CSN": "g_countryCode%3DUS%26g_zip%3D61820",
    "_ga_0GV7WXFNMT": "GS1.1.1728951203.22.1.1728951285.58.0.0",
    "_uetsid": "4a7612c08a8a11efb9ecaf7812596956",
    "_uetvid": "61ea67606fcb11efa800f36a3c836fa7",
    "lastRskxRun": "1728951285912",
    "IR_12051": "1728951285908%7C0%7C1728951285908%7C%7C",
    "_gat_gtag_UA_2081664_4": "1",
    "_ga_Q0HJWP456J": "GS1.1.1728951204.21.1.1728951285.58.0.0",
    "_ga": "GA1.1.1544528229.1726010478",
    "__attentive_pv": "2",
    "forterToken": "1f7438230b9f45aeb6f6345ebb82859e_1728951285193__UDF43-m4_20ck_zUvjJCoyTAQ%3D-6999-v2",
    "_rdt_uuid": "1726010478089.cfdabc1a-c4ad-496b-8e3b-a49bca134c9f",
    "CSNPersist": "latestRefid%3DGX281264597885.Wayfair~b%26page_of_visit%3D110",
    "__cf_bm": "oJFBWsvvqHGJZFM6_zX61GEX8IJqNJAgZ2G4cZ6EQdI-1728951313-1.0.1.1-WHr5I_ZogvB5cQTq0TL.v6kymoIQYm2N6vCQQY.PRpSFzoC2wh_busTAT2LRv2p.mGrHGI..xT.Zi95T9xWaNQ"
}
