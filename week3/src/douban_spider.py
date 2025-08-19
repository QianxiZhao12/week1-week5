#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import time
import gzip
import ssl
from datetime import datetime
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from mysql_helper import MySqlHelper

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', '')
}

class DoubanMovieSpider:
    """豆瓣电影Top250爬虫"""
    
    def __init__(self):
        self.base_url = 'https://movie.douban.com/top250'
        self.db = MySqlHelper(**DB_CONFIG)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        # 创建SSL上下文，忽略证书验证
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
    def fetch_page(self, start=0):
        """获取页面内容"""
        url = f'{self.base_url}?start={start}&filter='
        print(f"正在获取: {url}")
        
        try:
            request = urllib.request.Request(url, headers=self.headers)
            # 使用自定义SSL上下文
            response = urllib.request.urlopen(request, timeout=10, context=self.ssl_context)
            
            # 处理gzip压缩
            if response.info().get('Content-Encoding') == 'gzip':
                content = gzip.decompress(response.read())
            else:
                content = response.read()
                
            return content.decode('utf-8')
            
        except Exception as e:
            print(f"获取页面失败: {e}")
            return None
    
    def parse_movies(self, html):
        """解析电影信息"""
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'lxml')
        movies = []
        
        # 查找所有电影条目
        movie_items = soup.find_all('div', class_='item')
        
        for item in movie_items:
            try:
                movie = self._extract_movie_info(item)
                if movie:
                    movies.append(movie)
            except Exception as e:
                print(f"解析电影信息失败: {e}")
                continue
                
        return movies
    
    def _extract_movie_info(self, item):
        """提取单个电影信息"""
        movie = {
            'rank_num': 0, 'title': '', 'title_en': '', 'director': '',
            'actors': '', 'year': '', 'country': '', 'genre': '',
            'rating': 0.0, 'rating_count': 0, 'duration': '',
            'poster_url': '', 'summary': '', 'douban_id': '',
            'douban_url': '', 'crawl_time': '', 'created_time': '',
            'updated_time': ''
        }
        
        # 排名 - 使用find方法
        rank_elem = item.find('em')
        if rank_elem:
            movie['rank_num'] = int(rank_elem.get_text().strip())
        
        # 链接和豆瓣ID - 使用find方法查找a标签
        link_elem = item.find('a')
        if link_elem and link_elem.get('href'):
            href = link_elem.get('href')
            movie['douban_url'] = href
            # 提取豆瓣ID
            if '/subject/' in href:
                movie['douban_id'] = href.split('/subject/')[1].rstrip('/')
        
        # 海报 - 使用find方法查找img标签
        img_elem = item.find('img')
        if img_elem:
            movie['poster_url'] = img_elem.get('src', '')
        
        # 标题 - 使用find_all方法查找所有title类的span
        title_elems = item.find_all('span', class_='title')
        if title_elems:
            # 第一个span是中文标题
            movie['title'] = title_elems[0].get_text().strip()
            # 第二个span是英文标题（如果存在）
            if len(title_elems) > 1:
                en_title = title_elems[1].get_text().strip()
                # 移除开头的斜杠和空格
                movie['title_en'] = en_title.lstrip('/ ').strip()
        
        # 电影详细信息 - 查找bd div下的第一个p标签
        bd_div = item.find('div', class_='bd')
        if bd_div:
            info_p = bd_div.find('p')
            if info_p:
                # 获取p标签的所有文本内容
                info_text = info_p.get_text().strip()
                self._parse_movie_details_with_soup(movie, info_p)
        
        # 评分 - 使用find方法查找rating_num类的span
        rating_elem = item.find('span', class_='rating_num')
        if rating_elem:
            try:
                movie['rating'] = float(rating_elem.get_text().strip())
            except ValueError:
                movie['rating'] = 0.0
        
        # 评分人数 - 查找包含"人评价"的span
        rating_spans = item.find_all('span')
        for span in rating_spans:
            text = span.get_text().strip()
            if '人评价' in text:
                # 提取数字部分
                number_text = text.replace('人评价', '').strip()
                try:
                    movie['rating_count'] = int(number_text)
                except ValueError:
                    movie['rating_count'] = 0
                break
        
        # 简介 - 使用find方法查找inq类的span
        quote_elem = item.find('span', class_='inq')
        if quote_elem:
            movie['summary'] = quote_elem.get_text().strip()
        
        # 设置时间戳
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        movie['crawl_time'] = current_time
        movie['created_time'] = current_time
        movie['updated_time'] = current_time
        
        return movie
    
    def _parse_movie_details_with_soup(self, movie, info_p):
        """使用BeautifulSoup API解析电影详细信息"""
        # 获取p标签内的所有文本内容
        full_text = info_p.get_text().strip()
        
        # 按行分割处理
        text_lines = full_text.split('\n')
        
        # 合并所有文本用于更好的解析
        combined_text = ' '.join([line.strip() for line in text_lines if line.strip()])
        
        # 解析导演信息
        if '导演:' in combined_text:
            director_start = combined_text.find('导演:') + 3
            director_end = combined_text.find('主演:', director_start)
            if director_end == -1:
                # 如果没有主演，找到下一个可能的分隔符
                for delimiter in ['年', '分钟', '类型']:
                    temp_end = combined_text.find(delimiter, director_start)
                    if temp_end != -1:
                        director_end = temp_end
                        break
                if director_end == -1:
                    director_end = len(combined_text)
            
            director_text = combined_text[director_start:director_end].strip()
            if director_text:
                # 清理导演信息
                directors = [d.strip() for d in director_text.split('/') if d.strip()]
                movie['director'] = '/'.join(directors)
        
        # 解析主演信息
        if '主演:' in combined_text:
            actor_start = combined_text.find('主演:') + 3
            actor_end = len(combined_text)
            
            # 找到主演信息的结束位置
            for delimiter in ['年', '分钟', '类型', '剧情', '喜剧', '动作']:
                temp_end = combined_text.find(delimiter, actor_start)
                if temp_end != -1 and temp_end < actor_end:
                    actor_end = temp_end
            
            # 查找年份作为结束标志
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', combined_text[actor_start:])
            if year_match:
                year_pos = actor_start + year_match.start()
                if year_pos < actor_end:
                    actor_end = year_pos
            
            actor_text = combined_text[actor_start:actor_end].strip()
            if actor_text:
                # 清理主演信息
                actor_text = actor_text.rstrip('...')
                actors = [a.strip() for a in actor_text.split('/') if a.strip()]
                if actors:
                    movie['actors'] = '/'.join(actors)
        
        # 解析年份、国家、类型等信息
        for line in text_lines:
            line = line.strip()
            if not line or '导演:' in line or '主演:' in line:
                continue
                
            if any(char.isdigit() for char in line):
                # 这行包含数字，可能是年份、时长等信息
                parts = [p.strip() for p in line.split('/') if p.strip()]
                
                for part in parts:
                    # 年份（4位数字）
                    if len(part) == 4 and part.isdigit():
                        if 1900 <= int(part) <= 2030:
                            movie['year'] = part
                    
                    # 时长（包含"分钟"）
                    elif '分钟' in part:
                        movie['duration'] = part
                    
                    # 国家（常见国家名）
                    elif any(country in part for country in [
                        '中国大陆', '美国', '英国', '法国', '德国', '日本', '韩国',
                        '意大利', '西班牙', '加拿大', '澳大利亚', '中国香港', '中国台湾',
                        '俄罗斯', '印度', '瑞典', '丹麦', '挪威', '芬兰', '荷兰', '比利时'
                    ]):
                        if movie['country']:
                            movie['country'] += '/' + part
                        else:
                            movie['country'] = part
                    
                    # 类型（常见电影类型）
                    elif any(genre in part for genre in [
                        '剧情', '喜剧', '动作', '爱情', '科幻', '悬疑', '惊悚', '恐怖',
                        '犯罪', '战争', '动画', '纪录片', '传记', '历史', '音乐', '家庭',
                        '冒险', '奇幻', '西部', '运动', '短片'
                    ]):
                        if movie['genre']:
                            movie['genre'] += ' ' + part
                        else:
                            movie['genre'] = part
    
    def save_movies(self, movies):
        """保存电影数据到数据库"""
        if not movies:
            print("没有电影数据需要保存")
            return
        
        try:
            # 获取当前日期
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 清除今天的数据
            delete_sql = "DELETE FROM douban_movies WHERE DATE(created_time) = %s"
            self.db.execute(delete_sql, (today,))
            print(f"已清除今天的历史数据")
            
            # 批量插入
            current_time = datetime.now()
            success_count = 0
            
            for movie in movies:
                try:
                    self.db.insert('douban_movies', {
                        'rank_num': movie['rank_num'],
                        'title': movie['title'],
                        'title_en': movie['title_en'],
                        'director': movie['director'],
                        'actors': movie['actors'],
                        'year': movie['year'],
                        'country': movie['country'],
                        'genre': movie['genre'],
                        'rating': movie['rating'],
                        'rating_count': movie['rating_count'],
                        'duration': movie['duration'],
                        'poster_url': movie['poster_url'],
                        'summary': movie['summary'],
                        'douban_id': movie['douban_id'],
                        'douban_url': movie['douban_url'],
                        'crawl_time': current_time,
                        'created_time': current_time,
                        'updated_time': current_time
                    })
                    success_count += 1
                    
                except Exception as e:
                    print(f"保存电影 {movie.get('title', '未知')} 失败: {e}")
                    continue
            
            print(f"成功保存 {success_count}/{len(movies)} 部电影数据")
            
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def run(self):
        """运行爬虫"""
        print("开始爬取豆瓣电影Top100...")
        
        all_movies = []
        
        # 只爬取前100部电影，共4页，每页25部电影
        for page in range(4):
            start = page * 25
            print(f"\n正在爬取第 {page + 1}/4 页...")
            
            # 获取页面内容
            html = self.fetch_page(start)
            if not html:
                print(f"第 {page + 1} 页获取失败，跳过")
                continue
            
            # 解析电影信息
            movies = self.parse_movies(html)
            if movies:
                all_movies.extend(movies)
                print(f"第 {page + 1} 页解析到 {len(movies)} 部电影")
                
                # 打印前几部电影的信息用于调试
                if page == 0:
                    for i, movie in enumerate(movies[:3]):
                        print(f"电影{i+1}: {movie['title']} - 导演: {movie['director']} - 主演: {movie['actors']} - 评分: {movie['rating']}")
            else:
                print(f"第 {page + 1} 页没有解析到电影数据")
            
            # 延时避免请求过快
            time.sleep(2)
        
        # 保存所有电影数据
        if all_movies:
            print(f"\n总共爬取到 {len(all_movies)} 部电影，开始保存到数据库...")
            self.save_movies(all_movies)
        else:
            print("\n没有爬取到任何电影数据")
        
        print("\n爬取完成！")
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'db'):
            self.db.close()

if __name__ == '__main__':
    spider = DoubanMovieSpider()
    try:
        spider.run()
    except KeyboardInterrupt:
        print("\n用户中断爬取")
    except Exception as e:
        print(f"\n程序异常: {e}")
    finally:
        spider.close()