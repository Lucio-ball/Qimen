"""
奇门遁甲工作台 - 应用程序启动器
Project: QMW-CoreUI (Qi Men Workbench - Core UI)
Task ID: UI-20250901-001
"""

import sys
from PySide6.QtWidgets import QApplication
from .windows.main_window import MainWindow


def run():
    """
    应用程序启动函数
    
    Returns:
        int: 程序退出码
    """
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 实例化主窗口
    main_window = MainWindow()
    
    # 显示窗口
    main_window.show()
    
    # 启动事件循环并返回退出码
    return app.exec()
