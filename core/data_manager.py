"""
数据访问层 - 案例持久化管理
Project: QMW-Persistence (Qi Men Workbench - Persistence Layer)
Task ID: FEAT-20250901-019

提供SQLite数据库的案例增删改查功能
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional
import os
from datetime import datetime
from typing import List, Dict, Optional
from .models import Case, ChartResult


class DataManager:
    """数据访问层 - 管理案例的持久化存储"""
    
    def __init__(self, db_path: str):
        """
        初始化数据管理器
        
        Args:
            db_path: 数据库文件路径（.qmw文件）
        """
        self.db_path = db_path
        self.create_tables()
        self._upgrade_database_schema()  # 确保数据库架构是最新的
    
    def create_tables(self):
        """创建数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建cases表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        querent TEXT DEFAULT '',
                        details TEXT DEFAULT '',
                        creation_time TEXT NOT NULL,
                        query_time TEXT NOT NULL,
                        chart_result_json TEXT NOT NULL,
                        annotation_layers_json TEXT NOT NULL,
                        duan_yu_markdown TEXT,
                        feedback_text TEXT
                    )
                ''')
                
                conn.commit()
                
        except sqlite3.Error as e:
            print(f"创建数据库表失败: {e}")
            raise
    
    def _upgrade_database_schema(self):
        """升级数据库架构到V2版本"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查是否存在V2字段，如果不存在则添加
                cursor.execute("PRAGMA table_info(cases)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'querent' not in columns:
                    print("升级数据库架构：添加querent列")
                    cursor.execute("ALTER TABLE cases ADD COLUMN querent TEXT DEFAULT ''")
                
                if 'details' not in columns:
                    print("升级数据库架构：添加details列")
                    cursor.execute("ALTER TABLE cases ADD COLUMN details TEXT DEFAULT ''")
                    
                conn.commit()
                
        except sqlite3.Error as e:
            print(f"数据库架构升级失败: {e}")
            # 不抛出异常，允许继续运行
    
    def save_case(self, case: Case) -> int:
        """
        保存案例到数据库
        
        Args:
            case: 要保存的案例对象
            
        Returns:
            int: 保存后的案例ID
            
        Raises:
            Exception: 保存失败时抛出异常
        """
        try:
            current_time = datetime.now().isoformat()
            
            # 序列化ChartResult
            chart_result_json = json.dumps(case.chart_result.to_dict(), ensure_ascii=False, indent=2)
            
            # 序列化标注图层
            annotation_layers_json = json.dumps(case.annotation_layers, ensure_ascii=False, indent=2)
            
            # 从ChartResult中提取起局时间
            query_time = case.chart_result.qi_ju_time or current_time
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if case.id is None:
                    # 新案例 - 插入
                    cursor.execute('''
                        INSERT INTO cases (name, querent, details, creation_time, query_time, chart_result_json, annotation_layers_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (case.title, case.querent, case.details, current_time, query_time, chart_result_json, annotation_layers_json))
                    
                    case_id = cursor.lastrowid
                    case.id = case_id
                else:
                    # 现有案例 - 更新
                    cursor.execute('''
                        UPDATE cases 
                        SET name = ?, querent = ?, details = ?, query_time = ?, chart_result_json = ?, annotation_layers_json = ?
                        WHERE id = ?
                    ''', (case.title, case.querent, case.details, query_time, chart_result_json, annotation_layers_json, case.id))
                    
                    case_id = case.id
                
                conn.commit()
                return case_id
                
        except sqlite3.Error as e:
            print(f"保存案例失败: {e}")
            raise Exception(f"保存案例失败: {e}")
        except json.JSONEncodeError as e:
            print(f"序列化案例数据失败: {e}")
            raise Exception(f"序列化案例数据失败: {e}")
    
    def load_case(self, case_id: int) -> Optional[Case]:
        """
        从数据库加载案例
        
        Args:
            case_id: 案例ID
            
        Returns:
            Case: 加载的案例对象，如果不存在则返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, name, querent, details, creation_time, query_time, chart_result_json, annotation_layers_json
                    FROM cases WHERE id = ?
                ''', (case_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # 解析数据
                case_id, name, querent, details, creation_time, query_time, chart_result_json, annotation_layers_json = row
                
                # 反序列化ChartResult
                chart_result_data = json.loads(chart_result_json)
                chart_result = ChartResult.from_dict(chart_result_data)
                
                # 创建Case对象
                case = Case(name, chart_result)
                case.id = case_id
                case.querent = querent
                case.details = details
                case.filepath = self.db_path  # 设置案例关联的文件路径
                
                # 反序列化标注图层
                case.annotation_layers = json.loads(annotation_layers_json)
                
                # 确保有激活图层
                if case.annotation_layers and case.active_layer_index == -1:
                    case.active_layer_index = 0
                
                return case
                
        except sqlite3.Error as e:
            print(f"加载案例失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"反序列化案例数据失败: {e}")
            return None
    
    def load_all_cases(self) -> List[Case]:
        """
        加载数据库中的所有案例
        
        Returns:
            List[Case]: 所有案例的列表
        """
        try:
            cases = []
            cases_summary = self.get_all_cases_summary()
            
            for case_info in cases_summary:
                case = self.load_case(case_info['id'])
                if case:
                    cases.append(case)
                    
            return cases
            
        except Exception as e:
            print(f"加载所有案例失败: {e}")
            return []
    
    def get_all_cases_summary(self) -> List[Dict]:
        """
        获取所有案例的摘要信息
        
        Returns:
            List[Dict]: 案例摘要列表，格式为 [{'id': int, 'name': str, 'query_time': str, 'creation_time': str}, ...]
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, name, querent, details, query_time, creation_time
                    FROM cases
                    ORDER BY creation_time DESC
                ''')
                
                rows = cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'name': row[1],
                        'querent': row[2],
                        'details': row[3],
                        'query_time': row[4],
                        'creation_time': row[5]
                    }
                    for row in rows
                ]
                
        except sqlite3.Error as e:
            print(f"获取案例摘要失败: {e}")
            return []
    
    def delete_case(self, case_id: int) -> bool:
        """
        删除指定的案例
        
        Args:
            case_id: 要删除的案例ID
            
        Returns:
            bool: 删除成功返回True，失败返回False
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM cases WHERE id = ?', (case_id,))
                
                # 检查是否真的删除了记录
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    return False
                    
        except sqlite3.Error as e:
            print(f"删除案例失败: {e}")
            return False
    
    def get_database_info(self) -> Dict:
        """
        获取数据库信息
        
        Returns:
            Dict: 包含数据库文件信息的字典
        """
        try:
            file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM cases')
                case_count = cursor.fetchone()[0]
            
            return {
                'db_path': self.db_path,
                'file_size': file_size,
                'case_count': case_count,
                'exists': os.path.exists(self.db_path)
            }
            
        except Exception as e:
            return {
                'db_path': self.db_path,
                'file_size': 0,
                'case_count': 0,
                'exists': False,
                'error': str(e)
            }
