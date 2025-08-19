-- 创建百度热搜表
USE student_management;

CREATE TABLE IF NOT EXISTS baidu_hot_search (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rank_num INT NOT NULL COMMENT '排名',
    title VARCHAR(255) NOT NULL COMMENT '热搜标题',
    url VARCHAR(500) COMMENT '链接地址',
    hot_value VARCHAR(50) COMMENT '热度值',
    source VARCHAR(50) DEFAULT 'baidu' COMMENT '数据源',
    crawl_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '爬取时间',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_rank (rank_num),
    INDEX idx_crawl_time (crawl_time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='百度热搜数据表';