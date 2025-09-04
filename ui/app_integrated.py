"""
奇门遁甲工作台 - 集成版本启动器
Task ID: UI-20250901-010

使用完整集成的MainWindow启动应用程序
"""

import sys
from PySide6.QtWidgets import QApplication
from .windows.integrated_main_window import IntegratedMainWindow


def run_integrated():
    """
    启动集成版本的应用程序
    
    Returns:
        int: 程序退出码
    """
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("奇门遁甲工作台")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Qimen Workbench Project")
    
    # 实例化集成主窗口
    main_window = IntegratedMainWindow()
    
    # 显示窗口
    main_window.show()
    
    # 启动事件循环并返回退出码
    return app.exec()


# 保持原有的run函数作为备用
def run():
    """
    应用程序启动函数（原版本）
    
    Returns:
        int: 程序退出码
    """
    from .windows.main_window import MainWindow
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 实例化主窗口
    main_window = MainWindow()
    
    # 显示窗口
    main_window.show()
    
    # 启动事件循环并返回退出码
    return app.exec()
