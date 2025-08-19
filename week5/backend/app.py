from flask import Flask, request, jsonify
from flask_cors import CORS
from mysql_helper import MySqlHelper
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root1234'),
    'database': os.getenv('DB_NAME', 'student_management')
}

@app.route('/api/movies/rating-distribution', methods=['GET'])
def get_rating_distribution():
    """获取电影评分分布数据"""
    try:
        db = MySqlHelper(**DB_CONFIG)
        sql = """
        SELECT 
            CASE 
                WHEN rating >= 9.0 THEN '9.0-10.0'
                WHEN rating >= 8.0 THEN '8.0-8.9'
                WHEN rating >= 7.0 THEN '7.0-7.9'
                WHEN rating >= 6.0 THEN '6.0-6.9'
                ELSE '6.0以下'
            END as rating_range,
            COUNT(*) as count
        FROM douban_movies 
        WHERE rating IS NOT NULL
        GROUP BY rating_range
        ORDER BY rating_range DESC
        """
        result = db.fetch_all(sql)
        db.close()
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/movies/year-distribution', methods=['GET'])
def get_year_distribution():
    """获取电影年份分布数据"""
    try:
        db = MySqlHelper(**DB_CONFIG)
        sql = """
        SELECT 
            CASE 
                WHEN year >= '2020' THEN '2020年代'
                WHEN year >= '2010' THEN '2010年代'
                WHEN year >= '2000' THEN '2000年代'
                WHEN year >= '1990' THEN '1990年代'
                WHEN year >= '1980' THEN '1980年代'
                ELSE '1980年前'
            END as decade,
            COUNT(*) as count
        FROM douban_movies 
        WHERE year IS NOT NULL AND year != ''
        GROUP BY decade
        ORDER BY decade DESC
        """
        result = db.fetch_all(sql)
        db.close()
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/movies/country-distribution', methods=['GET'])
def get_country_distribution():
    """获取电影国家分布数据"""
    try:
        db = MySqlHelper(**DB_CONFIG)
        sql = """
        SELECT 
            CASE 
                WHEN country LIKE '%美国%' THEN '美国'
                WHEN country LIKE '%中国%' OR country LIKE '%香港%' OR country LIKE '%台湾%' THEN '中国'
                WHEN country LIKE '%日本%' THEN '日本'
                WHEN country LIKE '%英国%' THEN '英国'
                WHEN country LIKE '%法国%' THEN '法国'
                WHEN country LIKE '%意大利%' THEN '意大利'
                WHEN country LIKE '%德国%' THEN '德国'
                ELSE '其他'
            END as country_group,
            COUNT(*) as count
        FROM douban_movies 
        WHERE country IS NOT NULL AND country != ''
        GROUP BY country_group
        ORDER BY count DESC
        LIMIT 8
        """
        result = db.fetch_all(sql)
        db.close()
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=6000, host='0.0.0.0')