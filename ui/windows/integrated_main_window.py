"""
奇门遁甲工作台 - 集成主窗口
Task ID: UI-20250901-010

集成QueryWidget、ChartWidget和AttributePanelWidget的完整应用程序主窗口
"""

import sys
import os
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QStatusBar, QMessageBox, QSplitter,
    QApplication
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QAction

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.paipan_engine import PaiPanEngine
from core.models import ChartResult
from ui.config import DisplayConfig
from ui.widgets.query_widget import QueryWidget
from ui.widgets.chart_widget import ChartWidget
from ui.widgets.attribute_panel_widget import AttributePanelWidget


class IntegratedMainWindow(QMainWindow):
    """
    集成主窗口类
    
    负责管理应用程序的主界面，包括：
    - 中央图表显示区域（ChartWidget）
    - 左侧停靠查询面板（QueryWidget）  
    - 右侧停靠属性面板（AttributePanelWidget）
    - 菜单栏和状态栏
    """
    
    def __init__(self):
        """初始化集成主窗口"""
        super().__init__()
        
        # 初始化核心组件
        self.engine = PaiPanEngine()
        self.global_data = self._load_global_data()
        self.current_config = DisplayConfig()
        self.current_chart_data: Optional[ChartResult] = None
        
        # 初始化UI组件
        self.query_widget = None
        self.chart_widget = None
        self.attribute_panel_widget = None
        
        # 初始化界面
        self._init_ui()
        self._create_dock_widgets()
        self._create_menu_bar()
        self._create_status_bar()
        self._connect_signals()
        
        # 设置窗口属性
        self._setup_window_properties()
        
    def _load_global_data(self) -> dict:
        """加载全局数据文件"""
        try:
            import json
            data_file_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'data.json'
            )
            with open(data_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告：无法加载全局数据文件: {e}")
            return {}
    
    def _init_ui(self):
        """初始化主要UI组件"""
        # 创建中央图表组件
        self.chart_widget = ChartWidget(self.global_data, self.current_config)
        self.setCentralWidget(self.chart_widget)
        
    def _create_dock_widgets(self):
        """创建停靠面板"""
        # 创建左侧查询面板
        self.query_dock = QDockWidget("查询面板", self)
        self.query_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.query_widget = QueryWidget()
        self.query_dock.setWidget(self.query_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.query_dock)
        
        # 创建右侧属性面板
        self.attribute_dock = QDockWidget("属性面板", self)
        self.attribute_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.attribute_panel_widget = AttributePanelWidget(self.current_config)
        self.attribute_dock.setWidget(self.attribute_panel_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.attribute_dock)
        
        # 设置停靠面板的默认大小
        self.resizeDocks([self.query_dock, self.attribute_dock], [300, 250], Qt.Orientation.Horizontal)
        
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 新建排盘
        new_action = QAction("新建排盘(&N)", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_chart)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        # 停靠面板显示控制
        view_menu.addAction(self.query_dock.toggleViewAction())
        view_menu.addAction(self.attribute_dock.toggleViewAction())
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 关于
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
        
    def _connect_signals(self):
        """连接信号与槽"""
        # 查询组件信号连接
        if self.query_widget:
            self.query_widget.query_requested.connect(self._handle_paipan_request)
            
        # 属性面板信号连接
        if self.attribute_panel_widget:
            self.attribute_panel_widget.config_changed.connect(self._handle_config_change)
            
    def _setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle("奇门遁甲工作台")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)
        
        # 设置窗口图标（如果有的话）
        # self.setWindowIcon(QIcon("path/to/icon.png"))
        
    @Slot(dict)
    def _handle_paipan_request(self, query_data: dict):
        """
        处理排盘请求
        
        Args:
            query_data: 包含排盘参数的字典，格式：
                {
                    "query_time": datetime.datetime,
                    "nian_ming": str,
                    "notes": str
                }
        """
        try:
            self.status_bar.showMessage("正在计算排盘...")
            
            # 从query_time中提取时间参数
            query_time = query_data.get('query_time')
            if not query_time:
                raise ValueError("缺少查询时间")
            
            # 转换为引擎需要的14位时间字符串格式
            time_str = query_time.strftime('%Y%m%d%H%M%S')
            
            # 使用排盘引擎计算
            chart_result = self.engine.paipan(time_str)
            
            # 更新当前图表数据
            self.current_chart_data = chart_result
            
            # 更新图表显示
            self.chart_widget.update_chart(chart_result)
            
            self.status_bar.showMessage(f"排盘完成 - {chart_result.ju_shu_info.get('遁', '')}{chart_result.ju_shu_info.get('局', '')}局")
            
        except Exception as e:
            error_msg = f"排盘计算错误: {str(e)}"
            self.status_bar.showMessage(error_msg)
            QMessageBox.warning(self, "错误", error_msg)
            
    @Slot(object)
    def _handle_config_change(self, config: DisplayConfig):
        """
        处理配置变更
        
        Args:
            config: 新的显示配置
        """
        try:
            # 更新当前配置
            self.current_config = config
            
            # 更新图表组件配置
            self.chart_widget.update_config(config)
            
            self.status_bar.showMessage("显示配置已更新")
            
        except Exception as e:
            error_msg = f"配置更新错误: {str(e)}"
            self.status_bar.showMessage(error_msg)
            QMessageBox.warning(self, "错误", error_msg)
            
    def _new_chart(self):
        """新建排盘"""
        # 重置查询组件
        if self.query_widget:
            self.query_widget.reset_form()
            
        # 清空图表显示
        self.current_chart_data = None
        # 这里可以添加清空图表的逻辑
        
        self.status_bar.showMessage("已重置，请输入新的排盘参数")
        
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "<h3>奇门遁甲工作台</h3>"
            "<p>版本：1.0.0</p>"
            "<p>一个现代化的奇门遁甲排盘和分析工具</p>"
            "<p>©2024 Qimen Workbench Project</p>"
        )
        
    def get_current_chart_data(self) -> Optional[ChartResult]:
        """获取当前图表数据"""
        return self.current_chart_data
        
    def get_current_config(self) -> DisplayConfig:
        """获取当前显示配置"""
        return self.current_config


def main():
    """主函数，用于独立测试"""
    app = QApplication(sys.argv)
    
    window = IntegratedMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
