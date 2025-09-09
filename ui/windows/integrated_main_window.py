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
from core.models import ChartResult, Case
from core.data_manager import DataManager
from ui.config import DisplayConfig
from ui.widgets.query_widget import QueryWidget
from ..widgets.central_widget import CentralWidget
from ..widgets.attribute_panel_widget import AttributePanelWidget
from ..widgets.annotation_panel_widget import AnnotationPanelWidget
from ..widgets.case_browser_widget import CaseBrowserWidget
from ui.widgets.chart_widget import ChartWidget
from ui.widgets.welcome_widget import WelcomeWidget
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
        
        # 初始化数据管理器
        self.data_manager = DataManager()
        
        # 页面管理和案例计数
        self.central_widget = None
        self.case_counter = 0  # 案例计数器，用于生成标签页标题
        
        # 初始化UI组件
        self.attribute_panel_widget = None
        self.case_browser_widget = None
        
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
        
        # 初始化案例列表
        self._refresh_case_list()
        
    def _load_global_data(self) -> dict:
        """加载全局数据文件"""
        try:
            import json
            data_file_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'data', 'core_parameters.json'
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
        
        # 创建右侧标注面板
        self.annotation_dock = QDockWidget("标注面板", self)
        self.annotation_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        
        # 设置允许停靠的区域
        self.annotation_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        
        self.annotation_panel_widget = AnnotationPanelWidget(self)
        self.annotation_dock.setWidget(self.annotation_panel_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.annotation_dock)
        
        # 创建左侧案例浏览器面板
        self.case_browser_dock = QDockWidget("案例浏览器", self)
        self.case_browser_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        
        # 设置允许停靠的区域
        self.case_browser_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        
        self.case_browser_widget = CaseBrowserWidget(self)
        self.case_browser_dock.setWidget(self.case_browser_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.case_browser_dock)
        
        # 设置停靠面板的默认大小
        self.resizeDocks([self.case_browser_dock, self.attribute_dock, self.annotation_dock], [250, 300, 250], Qt.Orientation.Horizontal)
        
        # 将标注面板停靠在属性面板下方
        self.tabifyDockWidget(self.attribute_dock, self.annotation_dock)
    
    def _setup_initial_dock_state(self):
        """设置停靠面板的初始状态"""
        # 属性面板默认隐藏，用户可通过视图菜单控制显示
        if hasattr(self, 'attribute_dock'):
            # 设置属性面板默认不可见
            self.attribute_dock.setVisible(False)
            self.attribute_dock.hide()
            
            # 确保停靠面板的widget是启用的（虽然隐藏）
            if self.attribute_panel_widget:
                self.attribute_panel_widget.setEnabled(True)
                
        # 标注面板默认隐藏，用户可通过视图菜单控制显示  
        if hasattr(self, 'annotation_dock'):
            self.annotation_dock.setVisible(False)
            self.annotation_dock.hide()
            
            if self.annotation_panel_widget:
                self.annotation_panel_widget.setEnabled(True)
    
    def _setup_dock_actions(self):
        """设置停靠面板的菜单操作"""
        # 必须在_setup_menu()之后调用，以确保view_menu已经创建
        if hasattr(self, 'view_menu'):
            # 添加案例浏览器的菜单操作
            if hasattr(self, 'case_browser_dock'):
                case_browser_toggle_action = self.case_browser_dock.toggleViewAction()
                case_browser_toggle_action.setEnabled(True)
                self.view_menu.addAction(case_browser_toggle_action)
            
            # 添加属性面板的菜单操作
            if hasattr(self, 'attribute_dock'):
                attribute_toggle_action = self.attribute_dock.toggleViewAction()
                attribute_toggle_action.setEnabled(True)
                self.view_menu.addAction(attribute_toggle_action)
                
            # 添加标注面板的菜单操作
            if hasattr(self, 'annotation_dock'):
                annotation_toggle_action = self.annotation_dock.toggleViewAction()
                annotation_toggle_action.setEnabled(True)
                self.view_menu.addAction(annotation_toggle_action)
        
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
        
        # 保存当前案例
        self.save_case_action = QAction("保存当前案例(&S)", self)
        self.save_case_action.setShortcut("Ctrl+S")
        self.save_case_action.triggered.connect(self._save_current_case)
        file_menu.addAction(self.save_case_action)
        
        # 另存为
        self.save_as_action = QAction("另存为(&A)...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self._save_case_as)
        file_menu.addAction(self.save_as_action)
        
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
            
            # 连接标签页切换信号
            if self.central_widget.tab_widget:
                self.central_widget.tab_widget.currentChanged.connect(self._handle_tab_changed)
                
        # 案例浏览器信号连接
        if self.case_browser_widget:
            self.case_browser_widget.case_double_clicked.connect(self._load_case)
            self.case_browser_widget.delete_case_requested.connect(self._delete_case)
            self.case_browser_widget.refresh_button.clicked.connect(self._refresh_case_list)
        
        # 属性面板信号连接
        if self.attribute_panel_widget:
            self.attribute_panel_widget.config_changed.connect(self._handle_config_change)
            
        # 标注面板信号连接
        if self.annotation_panel_widget:
            self.annotation_panel_widget.annotation_selected.connect(self._handle_annotation_selected)
            self.annotation_panel_widget.annotation_edited.connect(self._handle_annotation_edited)
            self.annotation_panel_widget.annotation_deleted.connect(self._handle_annotation_deleted)
            self.annotation_panel_widget.annotations_changed.connect(self._refresh_current_chart_annotations)
            # v2.0 新增信号
            self.annotation_panel_widget.template_applied.connect(self._handle_template_applied)
            self.annotation_panel_widget.layer_changed.connect(self._handle_layer_changed)
            
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
            
            # 设置年命信息
            if 'nian_ming' in query_data and query_data['nian_ming']:
                chart_result.nian_ming = query_data['nian_ming']
                # 重新计算特殊参数，因为年命会影响特殊参数的计算
                chart_result.special_params = self.engine._analyze_special_params(chart_result)
            
            # 生成案例标题
            self.case_counter += 1
            case_title = f"案例{self.case_counter}"
            
            # 可以根据起局信息生成更具描述性的标题
            if 'question' in query_data and query_data['question']:
                case_title = f"案例{self.case_counter}: {query_data['question'][:10]}..."
            
            # 创建Case数据模型
            case = Case(case_title, chart_result)
            
            # 创建新的图表组件
            chart_widget = ChartWidget(self.global_data, self.current_config)
            chart_widget.update_chart(chart_result)
            
            # 将case对象关联到chart_widget以便后续使用
            chart_widget.case = case
            
            # 添加到标签页
            tab_index = self.central_widget.add_tab(chart_widget, case_title)
            
            # 关键步骤：切换到多案例页面
            self.central_widget.show_page(1)
            
            # 存储图表数据到标签页（用于后续操作）
            chart_widget.chart_data = chart_result
            
            # 同步标注面板显示当前案例
            if self.annotation_panel_widget:
                self.annotation_panel_widget.set_case(case)
                
                # 自动应用默认模板
                self._apply_template("_default_")
            
            # 自动打开标注面板
            if hasattr(self, 'annotation_dock') and self.annotation_dock:
                self.annotation_dock.setVisible(True)
                self.annotation_dock.raise_()  # 将面板置于前台
            
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

                # 兼容新版CentralWidget架构
                tab_widget = getattr(self.central_widget, 'tab_widget', None)
                if tab_widget:
                    for i in range(tab_widget.count()):
                        widget = tab_widget.widget(i)
                        if hasattr(widget, 'update_config') and widget != getattr(self, 'welcome_widget', None):
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
        
    def _connect_parameter_widget_signals(self, chart_widget):
        """连接ChartWidget中的ParameterWidget信号"""
        # 这里需要根据ChartWidget的实际结构来实现
        # 假设ChartWidget有一个方法可以获取所有ParameterWidget
        if hasattr(chart_widget, 'get_parameter_widgets'):
            for param_widget in chart_widget.get_parameter_widgets():
                # 连接标注相关信号
                param_widget.annotation_requested.connect(self._handle_annotation_request)
                param_widget.annotation_remove_requested.connect(self._handle_annotation_remove_request)
                
    def _handle_annotation_request(self, param_id):
        """处理添加标注请求"""
        if self.annotation_panel_widget:
            # 使用对话框让用户输入标注内容，而不是默认添加"新标注"
            self.annotation_panel_widget.show_annotation_dialog_for_param(param_id)
            
    def _handle_annotation_remove_request(self, param_id):
        """处理删除标注请求"""
        current_widget = self.central_widget.get_current_tab_widget() if self.central_widget else None
        if current_widget and hasattr(current_widget, 'case'):
            current_widget.case.remove_annotation(param_id)
            # 刷新标注面板
            if self.annotation_panel_widget:
                self.annotation_panel_widget.set_case(current_widget.case)
            # 刷新图表显示
            self._refresh_chart_annotations(current_widget)
            
    def _handle_annotation_selected(self, param_id):
        """处理标注选择"""
        # 可以高亮显示对应的参数在图表中
        pass
        
    def _handle_annotation_edited(self, param_id, annotation):
        """处理标注编辑"""
        # 刷新图表中对应参数的显示
        current_widget = self.central_widget.get_current_tab_widget() if self.central_widget else None
        if current_widget:
            self._refresh_chart_annotations(current_widget)
            
    def _handle_annotation_deleted(self, param_id):
        """处理标注删除"""
        # 刷新图表中对应参数的显示
        current_widget = self.central_widget.get_current_tab_widget() if self.central_widget else None
        if current_widget:
            self._refresh_chart_annotations(current_widget)
            
    def _refresh_current_chart_annotations(self):
        """刷新当前图表的标注显示"""
        current_widget = self.central_widget.get_current_tab_widget() if self.central_widget else None
        if current_widget:
            self._refresh_chart_annotations(current_widget)
            
    def _refresh_chart_annotations(self, chart_widget):
        """刷新图表中的标注显示"""
        # 这里需要根据ChartWidget的实际结构来实现
        # 更新所有ParameterWidget的标注显示
        if hasattr(chart_widget, 'refresh_annotations'):
            chart_widget.refresh_annotations()
        elif hasattr(chart_widget, 'case'):
            # fallback: 重新设置图表数据
            chart_widget.update_chart(chart_widget.case.chart_result)
            
    # v2.0 新增处理方法
    def _handle_template_applied(self, template_name):
        """处理模板应用"""
        print(f"模板已应用: {template_name}")
        # 更新状态栏
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(f"已应用模板: {template_name}", 3000)
        # 刷新当前图表
        self._refresh_current_chart_annotations()
        
    def _handle_layer_changed(self):
        """处理图层变化"""
        print("图层状态已变化")
        # 刷新当前图表以反映图层可见性变化
        self._refresh_current_chart_annotations()
        # 如果状态栏存在，显示提示
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("图层状态已更新", 2000)
            
    def _apply_template(self, template_name: str):
        """
        应用模板到当前激活的案例
        
        Args:
            template_name: 模板名称，包括特殊的"_default_"
        """
        try:
            # 获取当前激活的案例
            current_widget = self.central_widget.get_current_tab_widget()
            if not current_widget or not hasattr(current_widget, 'case'):
                print(f"没有激活的案例，无法应用模板 '{template_name}'")
                return
                
            case = current_widget.case
            if not case:
                print(f"案例对象为空，无法应用模板 '{template_name}'")
                return
                
            # 加载模板数据
            import json
            import os
            template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "templates.json")
            
            if not os.path.exists(template_path):
                print(f"模板文件不存在: {template_path}")
                return
                
            with open(template_path, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
                
            if template_name not in templates_data:
                print(f"模板 '{template_name}' 不存在")
                return
                
            template_rules = templates_data[template_name]
            chart_result = case.chart_result
            
            # 获取当前激活图层
            active_layer = case.get_active_layer()
            if not active_layer:
                print("没有激活的图层")
                return
                
            applied_count = 0
            
            # 遍历模板规则
            for rule in template_rules:
                param_type = rule.get("param_type", "")
                label = rule.get("label", "标注")
                
                matching_param_ids = []
                
                if param_type == "special":
                    # 处理特殊参数
                    param_name = rule.get("param_name", "")
                    matching_param_ids = self._find_special_param_ids(chart_result, param_name)
                else:
                    # 处理常规参数
                    param_value = rule.get("param_value")
                    matching_param_ids = self._find_regular_param_ids(chart_result, param_type, param_value)
                
                # 为每个匹配的参数ID添加标注
                for param_id in matching_param_ids:
                    annotations = active_layer["annotations"]
                    if param_id not in annotations:
                        annotations[param_id] = []
                        
                    # 检查是否已存在相同文本的标注
                    existing_texts = [ann.get("text", "") for ann in annotations[param_id]]
                    if label not in existing_texts:
                        annotations[param_id].append({
                            "text": label,
                            "shape": "circle",
                            "color": "#FF0000"
                        })
                        applied_count += 1
                        
            # 刷新显示
            if applied_count > 0:
                self._refresh_current_chart_annotations()
                if self.annotation_panel_widget:
                    self.annotation_panel_widget._refresh_annotation_list()
                    self.annotation_panel_widget._refresh_layer_list()
                    
                print(f"成功应用模板 '{template_name}'，添加了 {applied_count} 个标注")
            else:
                print(f"模板 '{template_name}' 没有找到匹配的参数")
                
        except Exception as e:
            print(f"应用模板失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def _find_special_param_ids(self, chart_result, param_name: str) -> list:
        """查找特殊参数的ID"""
        if not hasattr(chart_result, 'special_params') or not chart_result.special_params:
            print(f"ChartResult没有special_params或为空")
            return []
            
        special_params = chart_result.special_params
        if param_name not in special_params:
            print(f"特殊参数 '{param_name}' 不存在于special_params中")
            print(f"可用的特殊参数: {list(special_params.keys())}")
            return []
            
        param_ids = []
        param_locations = special_params[param_name]
        
        print(f"查找特殊参数 '{param_name}', 位置数量: {len(param_locations)}")
        
        for location_info in param_locations:
            # 直接使用location_info中的id字段
            param_id = location_info.get("id", "")
            if param_id:
                param_ids.append(param_id)
                print(f"  找到位置: {param_id}")
                
        return param_ids
        
    def _find_regular_param_ids(self, chart_result, param_type: str, param_value) -> list:
        """查找常规参数的ID"""
        matching_ids = []
        
        # 根据不同的参数类型查找匹配项
        if param_type == "tianGan":
            # 天干 - 在天盘干中查找
            for palace_idx in range(1, 10):
                palace = chart_result.palaces[palace_idx]
                for stem_idx, stem in enumerate(palace.tian_pan_stems):
                    if stem == param_value:
                        matching_ids.append(f"palace_{palace_idx}_tian_pan_stem_{stem_idx}")
                        
        elif param_type == "jiuXing":
            # 九星 - 在天盘星中查找
            for palace_idx in range(1, 10):
                palace = chart_result.palaces[palace_idx]
                for star_idx, star in enumerate(palace.tian_pan_stars):
                    if star == param_value:
                        matching_ids.append(f"palace_{palace_idx}_tian_pan_star_{star_idx}")
                        
        elif param_type == "baMen":
            # 八门 - 在天盘门中查找
            for palace_idx in range(1, 10):
                palace = chart_result.palaces[palace_idx]
                for gate_idx, gate in enumerate(palace.tian_pan_gates):
                    if gate == param_value:
                        matching_ids.append(f"palace_{palace_idx}_tian_pan_gate_{gate_idx}")
                        
        elif param_type == "baShen":
            # 八神 - 在八神中查找
            for palace_idx in range(1, 10):
                palace = chart_result.palaces[palace_idx]
                if palace.zhi_fu == param_value:
                    matching_ids.append(f"palace_{palace_idx}_zhi_fu")
                    
        # 可以继续添加其他参数类型的处理...
                    
        return matching_ids

    # ============ 案例持久化相关方法 ============
    
    def _save_current_case(self):
        """保存当前案例"""
        current_widget = self.central_widget.get_current_tab_widget() if self.central_widget else None
        if not current_widget or not hasattr(current_widget, 'case'):
            QMessageBox.warning(self, "警告", "没有可保存的案例")
            return
            
        try:
            case = current_widget.case
            case_id = self.data_manager.save_case(case)
            
            # 更新标签页标题（如果是新保存的案例）
            if case.id == case_id:
                current_index = self.central_widget.tab_widget.currentIndex()
                self.central_widget.tab_widget.setTabText(current_index, case.title)
            
            # 刷新案例列表
            self._refresh_case_list()
            
            # 状态栏提示
            self.status_bar.showMessage(f"案例 '{case.title}' 已保存", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存案例失败：{str(e)}")
            
    def _save_case_as(self):
        """另存为案例"""
        current_widget = self.central_widget.get_current_tab_widget() if self.central_widget else None
        if not current_widget or not hasattr(current_widget, 'case'):
            QMessageBox.warning(self, "警告", "没有可保存的案例")
            return
            
        # 这里可以弹出对话框让用户输入新的案例名称
        # 为简化实现，这里直接在原案例名称后加上时间戳
        import datetime
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            case = current_widget.case
            original_id = case.id
            original_title = case.title
            
            # 创建新的案例（清空ID和修改标题）
            case.id = None
            case.title = f"{original_title}_副本_{current_time}"
            
            case_id = self.data_manager.save_case(case)
            
            # 更新当前标签页标题
            current_index = self.central_widget.tab_widget.currentIndex()
            self.central_widget.tab_widget.setTabText(current_index, case.title)
            
            # 刷新案例列表
            self._refresh_case_list()
            
            # 状态栏提示
            self.status_bar.showMessage(f"案例已另存为 '{case.title}'", 3000)
            
        except Exception as e:
            # 恢复原始状态
            case.id = original_id
            case.title = original_title
            QMessageBox.critical(self, "错误", f"另存为失败：{str(e)}")
            
    def _load_case(self, case_id: int):
        """加载案例到新标签页"""
        try:
            case = self.data_manager.load_case(case_id)
            if not case:
                QMessageBox.warning(self, "警告", "案例不存在或已被删除")
                self._refresh_case_list()  # 刷新列表以移除无效项
                return
                
            # 在新标签页中打开案例
            self._create_case_tab(case)
            
            # 状态栏提示
            self.status_bar.showMessage(f"案例 '{case.title}' 已加载", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载案例失败：{str(e)}")
            
    def _delete_case(self, case_id: int):
        """删除案例"""
        try:
            success = self.data_manager.delete_case(case_id)
            if success:
                # 从案例浏览器列表中移除
                self.case_browser_widget.remove_case_from_list(case_id)
                
                # 检查是否有已打开的标签页对应这个案例，如果有则关闭
                self._close_case_tab_by_id(case_id)
                
                # 状态栏提示
                self.status_bar.showMessage("案例已删除", 3000)
            else:
                QMessageBox.warning(self, "警告", "删除案例失败，案例可能不存在")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除案例失败：{str(e)}")
            
    def _refresh_case_list(self):
        """刷新案例列表"""
        try:
            cases_summary = self.data_manager.get_all_cases_summary()
            self.case_browser_widget.refresh_list(cases_summary)
        except Exception as e:
            print(f"刷新案例列表失败：{e}")
            self.case_browser_widget.set_status("刷新失败")
            
    def _create_case_tab(self, case: Case):
        """创建案例标签页"""
        # 创建ChartWidget并设置案例
        chart_widget = ChartWidget(self.current_config, case.chart_result, case, self.global_data)
        
        # 连接参数组件信号
        self._connect_parameter_widget_signals(chart_widget)
        
        # 添加到标签页
        tab_index = self.central_widget.add_tab(chart_widget, case.title)
        
        # 切换到新标签页
        self.central_widget.tab_widget.setCurrentIndex(tab_index)
        
        # 更新标注面板
        if self.annotation_panel_widget:
            self.annotation_panel_widget.set_case(case)
            
    def _close_case_tab_by_id(self, case_id: int):
        """根据案例ID关闭对应的标签页"""
        if not self.central_widget or not self.central_widget.tab_widget:
            return
            
        tab_widget = self.central_widget.tab_widget
        for i in range(tab_widget.count()):
            widget = tab_widget.widget(i)
            if hasattr(widget, 'case') and widget.case and widget.case.id == case_id:
                tab_widget.removeTab(i)
                break
                
    def _handle_tab_changed(self, index: int):
        """处理标签页切换事件"""
        if index >= 0 and self.central_widget and self.central_widget.tab_widget:
            current_widget = self.central_widget.tab_widget.widget(index)
            
            # 更新保存菜单的可用性
            has_case = hasattr(current_widget, 'case') and current_widget.case is not None
            if hasattr(self, 'save_case_action'):
                self.save_case_action.setEnabled(has_case)
            if hasattr(self, 'save_as_action'):
                self.save_as_action.setEnabled(has_case)
                
            # 更新标注面板
            if self.annotation_panel_widget:
                case = getattr(current_widget, 'case', None) if current_widget else None
                self.annotation_panel_widget.set_case(case)


def main():
    """主函数，用于独立测试"""
    app = QApplication(sys.argv)
    
    window = IntegratedMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
