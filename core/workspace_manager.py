"""
工作区配置管理器
Project: QMW-Persistence (Qi Men Workbench - Persistence Layer)
Task ID: FEAT-20250901-019-V3

负责管理工作区路径的持久化存储和配置
"""

import os
import json
from typing import Optional
from PySide6.QtCore import QSettings

class WorkspaceManager:
    """工作区管理器 - 负责工作区路径的存储和管理"""
    
    def __init__(self):
        """初始化工作区管理器"""
        self.settings = QSettings("QiMenWorkbench", "WorkspaceManager")
        self.current_workspace_path: Optional[str] = None
        
        # 加载上次的工作区路径
        self._load_last_workspace()
        
    def _load_last_workspace(self):
        """加载上次的工作区路径"""
        last_workspace = self.settings.value("last_workspace_path", "")
        if last_workspace and os.path.exists(last_workspace) and os.path.isdir(last_workspace):
            self.current_workspace_path = last_workspace
            
    def set_workspace_path(self, workspace_path: str) -> bool:
        """
        设置当前工作区路径
        
        Args:
            workspace_path: 工作区文件夹路径
            
        Returns:
            bool: 设置是否成功
        """
        if not os.path.exists(workspace_path) or not os.path.isdir(workspace_path):
            return False
            
        self.current_workspace_path = workspace_path
        self.settings.setValue("last_workspace_path", workspace_path)
        return True
        
    def get_workspace_path(self) -> Optional[str]:
        """获取当前工作区路径"""
        return self.current_workspace_path
        
    def has_workspace(self) -> bool:
        """检查是否有当前工作区"""
        return self.current_workspace_path is not None
        
    def scan_qmw_files(self, workspace_path: Optional[str] = None) -> list:
        """
        扫描工作区中的.qmw文件
        
        Args:
            workspace_path: 可选的工作区路径，如果不提供则使用当前工作区
            
        Returns:
            list: .qmw文件的完整路径列表
        """
        scan_path = workspace_path or self.current_workspace_path
        if not scan_path or not os.path.exists(scan_path):
            return []
            
        qmw_files = []
        
        # 扫描工作区文件夹及子文件夹
        for root, dirs, files in os.walk(scan_path):
            for file in files:
                if file.lower().endswith('.qmw'):
                    file_path = os.path.join(root, file)
                    qmw_files.append(file_path)
                    
        # 按文件名排序
        qmw_files.sort(key=lambda x: os.path.basename(x).lower())
        return qmw_files
        
    def get_relative_path(self, file_path: str) -> str:
        """
        获取文件相对于工作区的相对路径
        
        Args:
            file_path: 文件的完整路径
            
        Returns:
            str: 相对路径，如果不在工作区内则返回文件名
        """
        if not self.current_workspace_path:
            return os.path.basename(file_path)
            
        try:
            rel_path = os.path.relpath(file_path, self.current_workspace_path)
            return rel_path if not rel_path.startswith('..') else os.path.basename(file_path)
        except ValueError:
            # 不同驱动器的情况
            return os.path.basename(file_path)
            
    def create_workspace_structure(self, base_path: str) -> str:
        """
        在指定路径创建工作区结构
        
        Args:
            base_path: 基础路径
            
        Returns:
            str: 创建的工作区路径
        """
        workspace_path = os.path.join(base_path, "QiMen_Workspace")
        
        # 创建主工作区文件夹
        os.makedirs(workspace_path, exist_ok=True)
        
        # 创建子文件夹结构
        subdirs = ["案例", "模板", "备份"]
        for subdir in subdirs:
            os.makedirs(os.path.join(workspace_path, subdir), exist_ok=True)
            
        # 创建README文件
        readme_path = os.path.join(workspace_path, "README.txt")
        if not os.path.exists(readme_path):
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("奇门遁甲工作区\n")
                f.write("="*20 + "\n\n")
                f.write("案例/ - 存放奇门遁甲案例文件(.qmw)\n")
                f.write("模板/ - 存放案例模板文件\n")
                f.write("备份/ - 存放自动备份文件\n\n")
                f.write("说明：\n")
                f.write("- .qmw文件是奇门遁甲案例文件，包含完整的排盘结果和标注信息\n")
                f.write("- 可以在子文件夹中组织您的案例文件\n")
                f.write("- 程序会自动扫描整个工作区文件夹中的所有.qmw文件\n")
                
        return workspace_path
        
    def validate_workspace(self, workspace_path: str) -> tuple[bool, str]:
        """
        验证工作区路径的有效性
        
        Args:
            workspace_path: 工作区路径
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not workspace_path:
            return False, "工作区路径不能为空"
            
        if not os.path.exists(workspace_path):
            return False, "工作区路径不存在"
            
        if not os.path.isdir(workspace_path):
            return False, "工作区路径必须是一个文件夹"
            
        # 检查是否有读写权限
        try:
            test_file = os.path.join(workspace_path, ".qmw_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except (OSError, IOError):
            return False, "工作区路径没有读写权限"
            
        return True, ""

def test_workspace_manager():
    """测试工作区管理器"""
    import tempfile
    import shutil

    # 创建临时测试目录
    test_dir = tempfile.mkdtemp()
        
    try:
        # 测试工作区管理器
        wm = WorkspaceManager()
        
        # 测试设置工作区
        success = wm.set_workspace_path(test_dir)
                
        # 创建测试.qmw文件
        test_files = ["案例1.qmw", "案例2.qmw", "subfolder/案例3.qmw"]
        for file_path in test_files:
            full_path = os.path.join(test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write("test content")
        
        # 测试文件扫描
        qmw_files = wm.scan_qmw_files()
        for file_path in qmw_files:
            rel_path = wm.get_relative_path(file_path)
                        
        # 测试工作区验证
        is_valid, error_msg = wm.validate_workspace(test_dir)

    finally:
        # 清理测试目录
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    test_workspace_manager()
