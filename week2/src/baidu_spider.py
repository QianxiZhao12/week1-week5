#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import os
import ssl
from datetime import datetime
from dotenv import load_dotenv
from mysql_helper import MySqlHelper

# 加载.env文件
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'student_management')
}

class BaiduSpider:
    """百度热搜爬虫"""

    def __init__(self):
        self.db = MySqlHelper(**DB_CONFIG)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        # 创建SSL上下文，忽略证书验证
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def fetch_hot_search(self):
        """获取热搜数据"""
        try:
            url = 'https://top.baidu.com/api/board?platform=wise&tab=realtime'
            req = urllib.request.Request(url, headers=self.headers)

            # 使用自定义SSL上下文
            with urllib.request.urlopen(req, timeout=10, context=self.ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))

            hot_list = []
            if 'data' in data and 'cards' in data['data']:
                for card in data['data']['cards']:
                    if 'content' in card:
                        for item in card['content'][:10]:
                            hot_list.append({
                                'title': item.get('word', ''),
                                'url': item.get('url', ''),
                                'hot_value': str(item.get('hotScore', 0))
                            })
            return hot_list

        except Exception as e:
            print(f"爬取失败: {e}")
            return []

    def save_data(self, hot_list):
        """保存数据"""
        if not hot_list:
            return

        try:
            # 清除今日数据
            today = datetime.now().strftime('%Y-%m-%d')
            self.db.execute(
                "DELETE FROM baidu_hot_search WHERE DATE(created_time) = %s",
                (today,)
            )

            # 批量插入
            current_time = datetime.now()
            for i, item in enumerate(hot_list, 1):
                self.db.insert('baidu_hot_search', {
                    'rank_num': i,
                    'title': item['title'],
                    'url': item['url'],
                    'hot_value': item['hot_value'],
                    'source': 'baidu',
                    'crawl_time': current_time,
                    'created_time': current_time
                })

            print(f"保存成功: {len(hot_list)} 条数据")

        except Exception as e:
            print(f"保存失败: {e}")

    def run(self):
        """执行爬取"""
        print("开始爬取百度热搜...")
        hot_list = self.fetch_hot_search()

        if hot_list:
            self.save_data(hot_list)
            print("爬取完成")
        else:
            print("未获取到数据")

    def close(self):
        """关闭连接"""
        if self.db:
            self.db.close()

if __name__ == '__main__':
    spider = BaiduSpider()
    try:
        spider.run()
    finally:
        spider.close()