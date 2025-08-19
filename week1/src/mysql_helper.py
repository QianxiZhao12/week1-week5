#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional, Tuple


class MySqlHelper:
    """MySQL数据库操作工具类"""
    
    def __init__(self, host='localhost', port=3306, user='root', password='', database=''):
        """初始化数据库连接"""
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'autocommit': True
        }
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            raise
    
    def execute(self, sql: str, params: Optional[Tuple] = None) -> int:
        """执行SQL语句，返回影响行数"""
        try:
            self.cursor.execute(sql, params or ())
            self.connection.commit()
            return self.cursor.rowcount
        except Error as e:
            self.connection.rollback()
            raise
    
    def fetch_one(self, sql: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """查询单条记录"""
        try:
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchone()
        except Error as e:
            raise
    
    def fetch_all(self, sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """查询多条记录"""
        try:
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchall()
        except Error as e:
            raise
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """插入单条记录，返回插入ID"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute(sql, tuple(data.values()))
        return self.cursor.lastrowid
    
    def update(self, table: str, data: Dict[str, Any], where: str, where_params: Optional[Tuple] = None) -> int:
        """更新记录，返回影响行数"""
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = list(data.values())
        if where_params:
            params.extend(where_params)
        return self.execute(sql, tuple(params))
    
    def delete(self, table: str, where: str, where_params: Optional[Tuple] = None) -> int:
        """删除记录，返回影响行数"""
        sql = f"DELETE FROM {table} WHERE {where}"
        return self.execute(sql, where_params)
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()