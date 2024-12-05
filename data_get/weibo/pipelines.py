# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import copy
import csv
import sqlite3
import copy
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings


settings = get_project_settings()

class SQLitePipeline(object):
    def open_spider(self, spider):
        """打开数据库连接，创建数据库和表"""
        try:
            # 数据库文件路径（可以自定义路径）
            self.db_file = 'weibo_data.db'  # 数据库文件名
            self.conn = sqlite3.connect(self.db_file)  # 连接数据库
            self.cursor = self.conn.cursor()

            # 创建数据库表
            self.create_table()

        except sqlite3.Error as e:
            spider.sqlite_error = True
            spider.logger.error(f"SQLite Error: {e}")

    def create_table(self):
        """创建SQLite表"""
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS weibo (
                id TEXT PRIMARY KEY,
                bid TEXT NOT NULL,
                user_id TEXT,
                screen_name TEXT,
                text TEXT,
                article_url TEXT,
                location TEXT,
                at_users TEXT,
                topics TEXT,
                reposts_count INTEGER,
                comments_count INTEGER,
                attitudes_count INTEGER,
                created_at TEXT,
                source TEXT,
                pics TEXT,
                video_url TEXT,
                retweet_id TEXT,
                ip TEXT,
                user_authentication TEXT
            );
        """
        self.cursor.execute(create_table_sql)
        self.conn.commit()

    def process_item(self, item, spider):
        """处理每个爬取的微博数据并保存到SQLite数据库"""
        try:
            new_item = copy.deepcopy(item)
            data = new_item['weibo']

            # 插入或更新数据（SQLite不支持ON DUPLICATE KEY，使用INSERT OR REPLACE）
            insert_sql = """
                INSERT OR REPLACE INTO weibo (
                    id, bid, user_id, screen_name, text, article_url, location,
                    at_users, topics, reposts_count, comments_count, attitudes_count,
                    created_at, source, pics, video_url, retweet_id, ip, user_authentication
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            values = (
                data.get('id', ''),
                data.get('bid', ''),
                data.get('user_id', ''),
                data.get('screen_name', ''),
                data.get('text', ''),
                data.get('article_url', ''),
                data.get('location', ''),
                data.get('at_users', ''),
                data.get('topics', ''),
                data.get('reposts_count', 0),
                data.get('comments_count', 0),
                data.get('attitudes_count', 0),
                data.get('created_at', ''),
                data.get('source', ''),
                ','.join(data.get('pics', [])),  # 将列表转为逗号分隔的字符串
                data.get('video_url', ''),
                data.get('retweet_id', ''),
                data.get('ip', ''),
                data.get('user_authentication', '')
            )
            self.cursor.execute(insert_sql, values)
            self.conn.commit()

        except sqlite3.Error as e:
            spider.logger.error(f"SQLite Error: {e}")
            raise DropItem(f"Error inserting item: {item}")
        return item

    def close_spider(self, spider):
        """关闭数据库连接"""
        try:
            self.conn.close()
        except sqlite3.Error as e:
            spider.logger.error(f"SQLite Error: {e}")

class DuplicatesPipeline:
    def __init__(self):
        self.seen_ids = set()  # 用于存储已处理过的微博id

    def process_item(self, item, spider):
        # 获取微博的唯一标识符，比如 'id' 或者 'bid'
        weibo_id = item.get('weibo', {}).get('id', None)

        if weibo_id:
            # 检查该微博是否已经处理过
            if weibo_id in self.seen_ids:
                raise DropItem(f"Duplicate item found: {weibo_id}")  # 如果已经处理过，丢弃该项
            else:
                self.seen_ids.add(weibo_id)  # 否则，添加到已处理集合中

        return item

import csv
from scrapy.exceptions import DropItem


class CsvPipeline:
    def open_spider(self, spider):
        """打开CSV文件并初始化写入器"""
        self.file = open('weibo_data_11_05.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        # 写入CSV头部（表头）
        self.writer.writerow([
            'id', 'user_id', 'screen_name', 'text', 'created_at',
            'article_url', 'at_users', 'attitudes_count', 'comments_count',
            'ip', 'location', 'reposts_count', 'retweet_id', 'source',
            'topics', 'user_authentication'
        ])

    def process_item(self, item, spider):
        """处理每个item并写入CSV"""
        weibo_data = item.get('weibo', {})
        row = [
            weibo_data.get('id', ''),
            weibo_data.get('user_id', ''),
            weibo_data.get('screen_name', ''),
            weibo_data.get('text', ''),
            weibo_data.get('created_at', ''),
            weibo_data.get('article_url', ''),  # 新字段
            weibo_data.get('at_users', ''),     # 新字段
            weibo_data.get('attitudes_count', ''),  # 新字段
            weibo_data.get('comments_count', ''),   # 新字段
            weibo_data.get('ip', ''),
            weibo_data.get('location', ''),
            weibo_data.get('reposts_count', ''),
            weibo_data.get('retweet_id', ''),
            weibo_data.get('source', ''),
            weibo_data.get('topics', ''),
            weibo_data.get('user_authentication', '')
        ]
        # 写入CSV
        self.writer.writerow(row)
        return item

    def close_spider(self, spider):
        """关闭CSV文件"""
        self.file.close()
