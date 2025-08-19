-- 豆瓣电影Top100数据表
USE student_management;

DROP TABLE IF EXISTS douban_movies;

CREATE TABLE douban_movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rank_num INT NOT NULL COMMENT '排名',
    title VARCHAR(500) NOT NULL COMMENT '电影标题',
    title_en VARCHAR(500) COMMENT '英文标题',
    director VARCHAR(1000) COMMENT '导演',
    actors TEXT COMMENT '主演列表',
    year VARCHAR(10) COMMENT '上映年份',
    country VARCHAR(500) COMMENT '制片国家/地区',
    genre VARCHAR(500) COMMENT '类型',
    rating DECIMAL(3,1) COMMENT '豆瓣评分',
    rating_count INT COMMENT '评分人数',
    duration VARCHAR(50) COMMENT '片长',
    poster_url VARCHAR(1000) COMMENT '海报链接',
    summary TEXT COMMENT '剧情简介',
    douban_id VARCHAR(50) COMMENT '豆瓣ID',
    douban_url VARCHAR(500) COMMENT '豆瓣链接',
    crawl_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '爬取时间',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    UNIQUE KEY uk_douban_id (douban_id),
    INDEX idx_rank (rank_num),
    INDEX idx_year (year),
    INDEX idx_rating (rating),
    INDEX idx_genre (genre),
    INDEX idx_country (country)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='豆瓣电影Top100数据表';