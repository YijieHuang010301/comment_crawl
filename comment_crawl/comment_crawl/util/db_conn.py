# -*- coding: UTF-8 -*-
# author: hyj
# date: 2024/09/13
import random
from urllib import parse
import socket
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from comment_crawl.common import errors
from comment_crawl.common.const import *
from comment_crawl.common.errors import *


def get_inner_ip() ->(str, errors):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip, None
    except:
        return "error", InnerIpError

def build_db_info_base() -> dict:
    INNER_IP, error = get_inner_ip()
    if error is not None:
        return {}

    db_info = {
        'mysql': {
            # 'tidb': {
            #     'host': 'tqindb-tidb02.timechee.inner' if INNER_IP.find('192.168.21') == -1 else '192.168.21.53',
            #     'port': 4000,
            #     'user': 'erp_all_root',
            #     'password': '#Zs@ckKCg!!mU@QT',
            #     'database': 'BIGDATA',
            #     'charset': 'utf8mb4'
            # },
            'tidb': {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': 'Abcd1234',
                'database': 'BIGDATATEST',
                'charset': 'utf8mb4'
            },
        },
        'redis': {
            'formal': {  # 数据库redisERP
                'host': "tqindb-redis-produce01.timechee.inner",
                'port': 6379,
                'password': "0MZQHwue",
                'db': 2,
                'decode_responses': True},
            'formal_erp_b': {  # 数据库redisERP-B
                # 'from_url': '',
                'host': "tqindb-b-redis-p01.timechee.inner",
                'port': 6379,
                'password': "Juk5Em6XhEnKqWfS",
                'db': 2,
                'decode_responses': True},

            'formal_91': {  # 数据库redis爬虫
                'host': "tqindb-redis-crawl01.timechee.inner",
                'port': 6379,
                'password': "123.com.!",
                'db': 2,
                'decode_responses': True},
            'formal_track': {  # 数据库redis 运单管理
                'host': "tqindb-redis-crawl01.timechee.inner",
                'port': 6379,
                'password': "123.com.!",
                'db': 3,
                'decode_responses': True},
            'formal_java': {  # 数据库redis 运单管理
                'host': "tqindb-redis-crawl01.timechee.inner",
                'port': 6379,
                'password': "123.com.!",
                'db': 4,
                'decode_responses': True},
        },
    }
    return db_info


def build_db_info() -> dict:
    db_info = build_db_info_base()
    for info_k, info_v in db_info.items():
        database_type = info_k
        info_2_ks = list(info_v.keys())
        for info_2_k in info_2_ks:
            # 组装 from_url
            if info_2_k.endswith('_from_url'):
                continue
            info_2_v = db_info[info_k][info_2_k]
            from_url_key = f"""{info_2_k}_from_url"""
            if not db_info.get(database_type).get(from_url_key):
                from_url = ''
                if database_type.lower() == 'mysql':
                    from_url = f"""mysql+pymysql://{info_2_v.get('user')}"""
                    from_url += f""":{parse.quote_plus(info_2_v.get('password'))}"""
                    from_url += f"""@{info_2_v.get('host')}"""
                    from_url += f""":{info_2_v.get('port')}"""
                    from_url += f"""/{info_2_v.get('database')}"""
                    from_url += f"""?charset={info_2_v.get('charset')}"""

                elif database_type.lower() == 'redis':
                    from_url = f"""redis://"""
                    from_url += f""":{info_2_v.get('password')}"""
                    from_url += f"""@{info_2_v.get('host')}"""
                    from_url += f""":{info_2_v.get('port')}"""
                    from_url += f"""/{info_2_v.get('db')}"""
                if from_url:
                    db_info[database_type][from_url_key] = from_url
    return db_info

def execute_sql(sql, sql_type, params=None):
    from comment_crawl.main import g_mysql
    connection = g_mysql.connect()
    try:
        # 使用数据库连接
        with connection.begin():
            result_proxy = connection.execute(sql, params)
            if sql_type == DB_SELECT:
                result = result_proxy.fetchall()
            elif sql_type == DB_UPDATE or sql_type == DB_DELETE or sql_type == DB_INSERT:
                result = result_proxy.rowcount
        return result, None   # 执行成功
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None, ExecQueryError()  # 执行失败

    finally:
        connection.close()  # 确保连接被关闭

def select_data_from_db_by_platform(platform_id):
    sql_select= text(f"""
        SELECT 
            ProductUrl, ProductId, id
        FROM 
            {ALL_PRODUCTS_TABLE} 
        WHERE 
            PlatformId = '{platform_id}' AND IsDelete = 0
    """)
    return execute_sql(sql_select, DB_SELECT)

def select_data_from_db_by_product(platform_id, product_id):
    sql_select= text(f"""
        SELECT 
            ProductUrl, ProductId
        FROM 
            {ALL_PRODUCTS_TABLE} 
        WHERE 
            PlatformId = '{platform_id}' AND ProductId = '{product_id}'
    """)
    return execute_sql(sql_select, DB_SELECT)

def set_isDelete_ALL_PRODUCTS_TABLE(uuid):
    update_sql = text(f"""
        UPDATE 
            {ALL_PRODUCTS_TABLE} 
        SET IsDelete = 1
        WHERE id = :uuid
    """)
    params = {"uuid": uuid}
    return execute_sql(update_sql, DB_UPDATE, params=params)

