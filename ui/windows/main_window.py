"""
奇门遁甲工作台 - 主窗口控制器
Project: QMW-CoreUI (Qi Men Workbench - Core UI)
Task ID: UI-20250901-001
"""

import os
from pathlib import Path
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice


class MainWindow(QMainWindow):
    """
    主窗口类
    
    负责加载main_window.ui文件并管理主窗口的逻辑
    """
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """
        初始化用户界面
        
        加载main_window.ui文件并设置为主窗口布局
        """
        try:
            # 获取UI文件路径
            ui_file_path = self._get_ui_file_path()
            
            # 创建UI加载器
            loader = QUiLoader()
            
            # 打开UI文件
            ui_file = QFile(ui_file_path)
            if not ui_file.open(QIODevice.ReadOnly):
                raise FileNotFoundError(f"无法打开UI文件: {ui_file_path}")
            
            # 加载UI
            widget = loader.load(ui_file, self)
            ui_file.close()
            
            if widget is None:
                raise RuntimeError("UI文件加载失败")
            
            # 设置中央部件
            self.setCentralWidget(widget)
            
        except (FileNotFoundError, RuntimeError) as e:
            # 创建基础窗口作为备选方案
            self._create_fallback_ui()
    
    def _get_ui_file_path(self):
        """
        获取UI文件的完整路径
        
        Returns:
            str: main_window.ui文件的绝对路径
        """
        # 获取当前文件的目录
        current_dir = Path(__file__).parent
        # 构建UI文件路径 (../../views/main_window.ui)
        ui_file_path = current_dir.parent / "views" / "main_window.ui"
        return str(ui_file_path.absolute())
    
    def _create_fallback_ui(self):
        """
        创建备选UI
        
        当UI文件加载失败时，创建一个基本的窗口界面
        """
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        label = QLabel("奇门遁甲工作台\n(UI文件加载失败，使用备选界面)")
        label.setStyleSheet("font-size: 16px; text-align: center; padding: 50px;")
        layout.addWidget(label)
        
        self.setCentralWidget(central_widget)
        self.setWindowTitle("奇门遁甲工作台")
        self.resize(800, 600)
    
    def _connect_signals(self):
        """
        连接信号与槽
        
        预留方法，用于未来的事件绑定
        """
        # 预留用于未来的信号连接
        pass
