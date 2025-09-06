"""
奇门遁甲工作台 - 集成主窗口 (多案例工作台版本)
Project: QMW-CoreUI (Qi Men Workbench - Core UI)
Task ID: ARCH-20250901-012

从单盘面工具升级为多案例工作台，支持：
- 欢迎页面
- 多标签页案例管理
- 模态对话框起局流程
"""

import sys
import os
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QStatusBar, QMessageBox, QSplitter, QTabWidget, QTabBar, QMenu,
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
from ui.widgets.welcome_widget import WelcomeWidget
from ui.widgets.central_widget import CentralWidget
from ui.dialogs.query_dialog import QueryDialog


class IntegratedMainWindow(QMainWindow):
    """
    集成主窗口类 - 多案例工作台版本
    
    负责管理应用程序的主界面，支持：
    - 欢迎页面（无案例时显示）
    - 多标签页案例管理（QTabWidget）
    - 模态对话框起局流程（QueryDialog）
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
        
        # 页面管理和案例计数
        self.central_widget = None
        self.case_counter = 0  # 案例计数器，用于生成标签页标题
        
        # 初始化UI组件
        self.attribute_panel_widget = None
        
        # 初始化界面
        self._init_ui()
        self._create_dock_widgets()
        self._setup_menu()
        self._setup_dock_actions()
        self._create_status_bar()
        self._connect_signals()
        
        # 设置窗口属性
        self._setup_window_properties()
        
        # 确保停靠面板初始状态正确（放在最后确保生效）
        self._setup_initial_dock_state()
        self._setup_initial_dock_state()
        
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
        # 创建中央切换控件作为唯一的中央部件
        self.central_widget = CentralWidget(self)
        self.setCentralWidget(self.central_widget)
        
    def _create_dock_widgets(self):
        """创建停靠面板"""
        # 创建右侧属性面板
        self.attribute_dock = QDockWidget("属性面板", self)
        self.attribute_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable  # 添加可关闭特性
        )
        
        # 设置允许停靠的区域
        self.attribute_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        
        self.attribute_panel_widget = AttributePanelWidget(self.current_config)
        self.attribute_dock.setWidget(self.attribute_panel_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.attribute_dock)
        
        # 设置停靠面板的默认大小
        self.resizeDocks([self.attribute_dock], [300], Qt.Orientation.Horizontal)
    
    def _setup_initial_dock_state(self):
        """设置停靠面板的初始状态"""
        # 确保属性面板可见（在窗口完全初始化后设置）
        if hasattr(self, 'attribute_dock'):
            # 明确设置停靠面板可见
            self.attribute_dock.setVisible(True)
            self.attribute_dock.show()
            self.attribute_dock.raise_()  # 确保面板在前台
            
            # 确保停靠面板的widget也是启用的
            if self.attribute_panel_widget:
                self.attribute_panel_widget.setEnabled(True)
                self.attribute_panel_widget.show()
    
    def _setup_dock_actions(self):
        """设置停靠面板的菜单操作"""
        # 必须在_setup_menu()之后调用，以确保view_menu已经创建
        if hasattr(self, 'view_menu') and hasattr(self, 'attribute_dock'):
            # 获取属性面板的toggleViewAction
            toggle_action = self.attribute_dock.toggleViewAction()
            
            # 确保action是启用的
            toggle_action.setEnabled(True)
            
            # 添加到视图菜单
            self.view_menu.addAction(toggle_action)
        
    def _setup_menu(self):
        """创建和设置主窗口的菜单栏"""
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 创建文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 新建案例菜单项
        self.new_case_action = QAction("新建案例(&N)", self)
        self.new_case_action.setShortcut("Ctrl+N")
        file_menu.addAction(self.new_case_action)
        
        file_menu.addSeparator()
        
        # 关闭当前案例
        close_case_action = QAction("关闭当前案例(&C)", self)
        close_case_action.setShortcut("Ctrl+W")
        close_case_action.triggered.connect(self._close_current_tab)
        file_menu.addAction(close_case_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 创建视图菜单 - 用于控制停靠面板显示
        self.view_menu = menubar.addMenu("视图(&V)")
        self.view_menu.setObjectName("view_menu")  # 设置对象名便于查找
        
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
        # 菜单操作信号连接
        if hasattr(self, 'new_case_action'):
            self.new_case_action.triggered.connect(self._handle_new_case_action)
        
        # 中央切换控件信号连接
        if self.central_widget:
            self.central_widget.new_case_requested.connect(self._handle_new_case_action)
            self.central_widget.tab_close_requested.connect(self._handle_tab_close_request)
        
        # 属性面板信号连接
        if self.attribute_panel_widget:
            self.attribute_panel_widget.config_changed.connect(self._handle_config_change)
            
    def _setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle("奇门遁甲工作台 - 多案例管理 (最终架构)")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)
        
        # 设置窗口图标（如果有的话）
        # self.setWindowIcon(QIcon("path/to/icon.png"))
    
    def _handle_new_case_action(self):
        """处理新建案例操作"""
        try:
            # 创建并显示起局对话框
            dialog = QueryDialog(self)
            
            # 执行对话框
            if dialog.exec() == dialog.DialogCode.Accepted:
                # 获取起局数据
                query_data = dialog.get_data()
                
                # 进行排盘计算
                self._create_new_case(query_data)
                
        except Exception as e:
            error_msg = f"新建案例错误: {str(e)}"
            self.status_bar.showMessage(error_msg)
            QMessageBox.warning(self, "错误", error_msg)
    
    def _create_new_case(self, query_data: dict):
        """
        创建新案例
        
        Args:
            query_data: 从QueryDialog获取的起局数据
        """
        try:
            self.status_bar.showMessage("正在计算排盘...")
            
            # 构建时间字符串（这里需要根据实际的query_data格式调整）
            if 'query_time' in query_data:
                # 如果query_data包含datetime对象
                query_time = query_data['query_time']
                time_str = query_time.strftime('%Y%m%d%H%M%S')
            else:
                # 如果query_data包含分别的年月日时分字段
                year = query_data.get('year', 2024)
                month = query_data.get('month', 1)
                day = query_data.get('day', 1)
                hour = query_data.get('hour', 12)
                minute = query_data.get('minute', 0)
                time_str = f"{year:04d}{month:02d}{day:02d}{hour:02d}{minute:02d}00"
            
            # 使用排盘引擎计算
            chart_result = self.engine.paipan(time_str)
            
            # 创建新的图表组件
            chart_widget = ChartWidget(self.global_data, self.current_config)
            chart_widget.update_chart(chart_result)
            
            # 生成案例标题
            self.case_counter += 1
            case_title = f"案例{self.case_counter}"
            
            # 可以根据起局信息生成更具描述性的标题
            if 'question' in query_data and query_data['question']:
                case_title = f"案例{self.case_counter}: {query_data['question'][:10]}..."
            
            # 添加到标签页
            tab_index = self.central_widget.add_tab(chart_widget, case_title)
            
            # 关键步骤：切换到多案例页面
            self.central_widget.show_page(1)
            
            # 存储图表数据到标签页（用于后续操作）
            chart_widget.chart_data = chart_result
            
            self.status_bar.showMessage(f"案例创建完成 - {chart_result.ju_shu_info.get('遁', '')}{chart_result.ju_shu_info.get('局', '')}局")
            
        except Exception as e:
            error_msg = f"案例创建错误: {str(e)}"
            self.status_bar.showMessage(error_msg)
            QMessageBox.warning(self, "错误", error_msg)
    
    def _handle_tab_close_request(self, index: int):
        """
        处理标签页关闭请求（来自CentralWidget）
        
        Args:
            index: 要关闭的标签页索引
        """
        if index >= 0 and index < self.central_widget.get_tab_count():
            # 移除标签页
            self.central_widget.remove_tab(index)
            
            # 检查是否需要切换回欢迎页面
            if self.central_widget.get_tab_count() == 0:
                self.central_widget.show_page(0)  # 切换回欢迎页面
                self.status_bar.showMessage("所有案例已关闭，返回欢迎页面")
            else:
                self.status_bar.showMessage("案例已关闭")
    
    def _close_current_tab(self):
        """关闭当前标签页"""
        if (self.central_widget.is_multi_case_page_active() and 
            self.central_widget.get_tab_count() > 0):
            current_index = self.central_widget.tab_widget.currentIndex()
            if current_index >= 0:
                self._handle_tab_close_request(current_index)
        
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
            
            # 更新所有标签页中的图表组件配置
            for i in range(self.tab_widget.count()):
                widget = self.tab_widget.widget(i)
                if hasattr(widget, 'update_config') and widget != self.welcome_widget:
                    widget.update_config(config)
            
            self.status_bar.showMessage("显示配置已更新")
            
        except Exception as e:
            error_msg = f"配置更新错误: {str(e)}"
            self.status_bar.showMessage(error_msg)
            QMessageBox.warning(self, "错误", error_msg)
            
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "<h3>奇门遁甲工作台 - 最终架构版本</h3>"
            "<p>版本：3.0.0 (ARCH-20250901-013)</p>"
            "<p>一个现代化的奇门遁甲排盘和分析工具</p>"
            "<p>支持多案例同时管理的专业工作台</p>"
            "<p>采用QStackedLayout架构解决停靠面板兼容性</p>"
            "<p>©2024 Qimen Workbench Project</p>"
        )
        
    def get_current_chart_data(self) -> Optional[ChartResult]:
        """获取当前标签页的图表数据"""
        if self.central_widget.is_multi_case_page_active():
            current_widget = self.central_widget.get_current_tab_widget()
            if current_widget and hasattr(current_widget, 'chart_data'):
                return current_widget.chart_data
        return None
        
    def get_current_config(self) -> DisplayConfig:
        """获取当前显示配置"""
        return self.current_config
    
    def get_tab_count(self) -> int:
        """获取标签页数量"""
        return self.central_widget.get_tab_count() if self.central_widget else 0


def main():
    """主函数，用于独立测试"""
    app = QApplication(sys.argv)
    
    window = IntegratedMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
