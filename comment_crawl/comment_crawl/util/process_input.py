import datetime
import os
import pandas as pd
from sqlalchemy import text

from comment_crawl.common.const import *
from comment_crawl.common.errors import *
from comment_crawl.util.url_parser import *

from comment_crawl.util.db_conn import execute_sql
from comment_crawl.util.hash_util import get_hash


EC_SKU_HEADER_STR = "ec_sku_headers"
STORE_SKU_HEADER_STR = "store_sku_headers"
LINK_HEADER_STR = "link_headers"

# Define keywords for each type of SKU and link
required_headers = {
    EC_SKU_HEADER_STR: ['易仓sku', '仓库sku'],
    STORE_SKU_HEADER_STR: ['supplier part', 'seller sku', '店铺sku', '平台sku'],
    LINK_HEADER_STR: ['链接', 'link']
}


platform_key_func = {'amazon.com': amazon_url_parser, 'wayfair.com': wayfair_url_parser, 'wayfair.ca': wayfair_url_parser,
                     'walmart.com': walmart_url_parser, 'homedepot.com': homedepot_url_parser,
                     'overstock.com': overstock_url_parser,'bedbathandbeyond.com': overstock_url_parser,
                     'lowes.com': lowes_url_parser}

insert_all_product_sql = (
    text(
        f'''
        INSERT INTO {ALL_PRODUCTS_TABLE} (id, PlatformId, PlatformName, ProductId, ProductUrl, StoreProductSku, ECProductSku, IsDelete, ImportTime, UpdateTime)
        VALUES (:id, :PlatformId, :PlatformName, :ProductId, :ProductUrl, :StoreProductSku, :ECProductSku, :IsDelete, :ImportTime, :UpdateTime)
        ON DUPLICATE KEY UPDATE
            PlatformId = VALUES(PlatformId),
            PlatformName = VALUES(PlatformName),
            ProductUrl = VALUES(ProductUrl),
            StoreProductSku = VALUES(StoreProductSku),
            ECProductSku = VALUES(ECProductSku),
            UpdateTime = VALUES(UpdateTime)
        '''
        ))

class InputProcessor:
    def __init__(self, file_path):
        self.sheet_headers = {}
        self.file_path = file_path
        self.header_fail_infos = {}
        self.items_to_save = []
        self.excel_reader = None

    # 判断header合规性
    def parse_header(self):
        for sheet_name, df_data in self.excel_reader.items():
            df_data.columns = df_data.columns.str.lower()
            if df_data.shape[0] > 0:
                # 删除全为空值的行
                df_data.dropna(how='all', inplace=True)

                header_names = [str(col).strip() for col in df_data.columns.values]

                missing_columns = []
                found_sheet_headers = {}

                for column_display_name, keywords in required_headers.items():
                    matched_column = self._match_column_keywords(header_names, keywords)
                    if matched_column:
                        found_sheet_headers[column_display_name] = matched_column
                    else:
                        missing_columns.append(f" 没有{column_display_name};")

                if missing_columns:
                    fail_msg = '文件表头不符合规范:' + ''.join(missing_columns)
                    self.header_fail_infos[sheet_name] = fail_msg
                else:
                    self.sheet_headers[sheet_name] = found_sheet_headers

        if self.header_fail_infos:
            return UploadFileCheckError(self.header_fail_infos)

        return None

    # 返回header字符
    def _match_column_keywords(self, header_names, keywords):
        """
        在表头中查找包含指定关键词的列名，返回第一个匹配的列名
        """
        for header in header_names:
            for keyword in keywords:
                if keyword in header:
                    return header  # 返回匹配的列名
        return None

    # 保存数据
    def save_data(self):
        for sheet_name, df_data in self.excel_reader.items():
            curr_ec_sku_header = self.sheet_headers[sheet_name][EC_SKU_HEADER_STR]
            curr_store_sku_header = self.sheet_headers[sheet_name][STORE_SKU_HEADER_STR]
            curr_link_header = self.sheet_headers[sheet_name][LINK_HEADER_STR]

            # 空数据使用上一行数据填充
            df_data.ffill(inplace=True)

            # TODO: 防止第一行为空 填充 第二行数据
            df_data.bfill(inplace=True)


            for idx, row in df_data.iterrows():
                curr_ec_sku = str(row[curr_ec_sku_header]).strip()
                curr_store_sku = str(row[curr_store_sku_header]).strip()
                curr_link = str(row[curr_link_header]).strip()
                save_error = self.save_row(curr_ec_sku, curr_store_sku, curr_link)
                if save_error:
                    print(save_error)
        self.save_to_db()

    # 解析每一行
    def save_row(self, ec_sku, store_sku, link):
        platform_id, platform_name, product_id = self.parse_product_url(link)
        if platform_id is None:
            return SaveRowFailedError()
        item = dict()
        item["id"] = get_hash('_'.join([str(platform_id), str(product_id)]))
        item["PlatformId"] = platform_id
        item["PlatformName"] = platform_name
        item["ProductId"] = product_id
        item["ProductUrl"] = link
        item["StoreProductSku"] = store_sku
        item["ECProductSku"] = ec_sku
        item["IsDelete"] = 0
        item["ImportTime"] = item["UpdateTime"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.items_to_save.append(item)
        return None

    # 保存数据到database
    def save_to_db(self):
        print("start saving to db")
        if not self.items_to_save:
            return

        # 参数
        values = [
            {
                "id": item["id"],
                "PlatformId": item["PlatformId"],
                "PlatformName": item["PlatformName"],
                "ProductId": item["ProductId"],
                "ProductUrl": item["ProductUrl"],
                "StoreProductSku": item["StoreProductSku"],
                "ECProductSku": item["ECProductSku"],
                "IsDelete": item["IsDelete"],
                "ImportTime": item["ImportTime"],
                "UpdateTime": item["UpdateTime"]
            }
            for item in self.items_to_save
        ]

        # 执行 SQL 语句
        rows, error = execute_sql(insert_all_product_sql,DB_INSERT, params=values)
        if error is not None:
            print(error)
            return
        print(f"successfully parsed {rows} rows")

    # 解析不同url的数据
    def parse_product_url(self, link):
        for key in platform_key_func.keys():
            if key in link:
                platform_id = platforms[key].get("id")
                platform_name = platforms[key].get("name")
                return platform_id, platform_name, platform_key_func[key](link)
        return None, None, None


    def run(self):
        self.excel_reader = pd.read_excel(self.file_path, sheet_name=None)
        parse_error = self.parse_header()
        if parse_error is not None:
            return parse_error
        self.save_data()
        os.remove(self.file_path)


