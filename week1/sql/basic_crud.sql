-- 使用学生管理数据库
USE student_management;

-- ================================
-- 插入数据 (CREATE)
-- ================================

-- 插入单条记录
INSERT INTO students (student_id, name, height) 
VALUES ('2024001', '张三', 175.5);

-- 插入多条记录
INSERT INTO students (student_id, name, height) VALUES 
('2024002', '李四', 168.0),
('2024003', '王五', 172.3),
('2024004', '赵六', 180.2),
('2024005', '钱七', 165.8);

-- 查看插入结果
SELECT * FROM students;

-- ================================
-- 查询数据 (READ)
-- ================================

-- 查询所有记录
SELECT * FROM students;

-- 查询指定字段
SELECT student_id, name FROM students;

-- 条件查询
SELECT * FROM students WHERE height > 170;

-- 模糊查询
SELECT * FROM students WHERE name LIKE '%三%';

-- 排序查询
SELECT * FROM students ORDER BY height DESC;

-- 限制查询结果数量
SELECT * FROM students ORDER BY height DESC LIMIT 3;

-- 统计查询
SELECT COUNT(*) as total_students FROM students;
SELECT AVG(height) as avg_height FROM students;
SELECT MAX(height) as max_height, MIN(height) as min_height FROM students;

-- ================================
-- 更新数据 (UPDATE)
-- ================================

-- 更新单个字段
UPDATE students SET height = 176.0 WHERE student_id = '2024001';

-- 更新多个字段
UPDATE students SET name = '张三丰', height = 177.5 WHERE student_id = '2024001';

-- 批量更新
UPDATE students SET height = height + 1 WHERE height < 170;

-- 查看更新结果
SELECT * FROM students WHERE student_id = '2024001';
SELECT * FROM students WHERE height < 171;

-- ================================
-- 删除数据 (DELETE)
-- ================================

-- 删除指定记录
DELETE FROM students WHERE student_id = '2024005';

-- 条件删除
DELETE FROM students WHERE height > 180;

-- 查看删除结果
SELECT * FROM students;
