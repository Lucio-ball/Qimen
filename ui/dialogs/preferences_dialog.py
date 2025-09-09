"""
首选项对话框 - 全面的用户配置界面
Project: QMW-CoreApp (Qi Men Workbench - Core Application)
Task ID: FEAT-20250901-020-Comprehensive (全面首选项系统)
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget,
    QWidget, QPushButton, QDialogButtonBox, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.config import DisplayConfig
from core.config_manager import ConfigManager
from .preferences_pages import (
    GeneralPage, ChartDisplayPage, TemplateManagementPage, 
    DataCachePage, AboutPage
)


"""
首选项对话框 - 全面的用户配置界面
Project: QMW-CoreApp (Qi Men Workbench - Core Application)
Task ID: FEAT-20250901-020-Comprehensive (全面首选项系统)
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget,
    QWidget, QPushButton, QDialogButtonBox, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.config import DisplayConfig
from core.config_manager import ConfigManager
from .preferences_pages import (
    GeneralPage, ChartDisplayPage, TemplateManagementPage, 
    DataCachePage, AboutPage
)


class PreferencesDialog(QDialog):
    """
    全面的首选项设置对话框
    
    功能：
    1. 左侧导航列表（通用、盘面显示、模板管理、数据与缓存、关于）
    2. 右侧设置页面（QStackedWidget）
    3. 实时预览和应用按钮
    4. 取消和确定按钮
    5. 分页管理设置内容
    """
    
    # 信号：配置发生变化时发出（用于实时预览）
    config_applied = Signal(DisplayConfig, dict, dict)  # display_config, general_config, data_config
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        
        # 原始配置备份（用于取消操作）
        self.original_display_config = self.config_manager.load_display_config()
        self.original_general_config = self.config_manager.load_general_config()
        self.original_data_config = self.config_manager.load_data_config()
        
        # 当前编辑的配置副本
        self.current_display_config = self.config_manager.load_display_config()
        self.current_general_config = self.config_manager.load_general_config()
        self.current_data_config = self.config_manager.load_data_config()
        
        self.setWindowTitle("首选项")
        self.setMinimumSize(900, 700)
        self.setModal(True)
        
        self._init_ui()
        self._load_configs_to_pages()
        self._connect_signals()
        
    def _init_ui(self):
        """初始化用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧导航列表
        self.nav_list = QListWidget()
        self.nav_list.setMaximumWidth(200)
        self.nav_list.setFrameStyle(QFrame.NoFrame)
        
        # 添加导航项
        nav_items = ["通用", "盘面显示", "模板管理", "数据与缓存", "关于"]
        for item in nav_items:
            self.nav_list.addItem(item)
        
        # 设置当前选中项
        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        
        splitter.addWidget(self.nav_list)
        
        # 右侧内容区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # 页面容器
        self.stacked_widget = QStackedWidget()
        right_layout.addWidget(self.stacked_widget)
        
        # 创建设置页面
        self._create_pages()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 重置按钮
        self.reset_button = QPushButton("重置为默认值")
        self.reset_button.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        # 应用按钮
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self._apply_configs)
        button_layout.addWidget(self.apply_button)
        
        # 标准对话框按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self._cancel)
        button_layout.addWidget(button_box)
        
        right_layout.addLayout(button_layout)
        
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([200, 700])
        
    def _create_pages(self):
        """创建各个设置页面"""
        # 通用页面
        self.general_page = GeneralPage(self)
        self.stacked_widget.addWidget(self.general_page)
        
        # 盘面显示页面
        self.chart_display_page = ChartDisplayPage(self)
        self.stacked_widget.addWidget(self.chart_display_page)
        
        # 模板管理页面
        self.template_page = TemplateManagementPage(self)
        self.stacked_widget.addWidget(self.template_page)
        
        # 数据与缓存页面
        self.data_cache_page = DataCachePage(self)
        self.stacked_widget.addWidget(self.data_cache_page)
        
        # 关于页面
        self.about_page = AboutPage(self)
        self.stacked_widget.addWidget(self.about_page)
        
    def _connect_signals(self):
        """连接信号与槽"""
        # 各页面的配置变化信号
        self.general_page.config_changed.connect(self._on_general_config_changed)
        self.chart_display_page.config_changed.connect(self._on_display_config_changed)
        self.data_cache_page.config_changed.connect(self._on_data_config_changed)
        
        # 模板变化信号
        self.template_page.templates_changed.connect(self._on_templates_changed)
        
    def _load_configs_to_pages(self):
        """将配置加载到各个页面"""
        # 设置配置文件路径显示
        config_path = self.config_manager.get_config_file_path()
        self.data_cache_page.set_config_path(config_path)
        
        # 加载配置到各页面
        self.general_page.load_config(self.current_general_config)
        self.chart_display_page.load_config(self.current_display_config)
        self.data_cache_page.load_config(self.current_data_config)
        
    def _on_nav_changed(self, current_row):
        """导航项切换事件"""
        self.stacked_widget.setCurrentIndex(current_row)
        
    def _on_general_config_changed(self, config):
        """通用配置变化事件"""
        self.current_general_config = config.copy()
        # 实时预览可以在这里实现，例如主题切换
        
    def _on_display_config_changed(self, config):
        """显示配置变化事件"""
        self.current_display_config = config
        # 发出信号进行实时预览
        self.config_applied.emit(
            self.current_display_config, 
            self.current_general_config, 
            self.current_data_config
        )
        
    def _on_data_config_changed(self, config):
        """数据配置变化事件"""
        self.current_data_config = config.copy()
        
    def _on_templates_changed(self):
        """模板变化事件"""
        # 模板变化不需要实时预览，只在保存时生效
        pass
        
    def _apply_configs(self):
        """应用配置（保存到磁盘）"""
        try:
            # 从各页面收集最新配置
            self.current_general_config = self.general_page.get_config()
            self.current_display_config = self.chart_display_page.get_config()
            self.current_data_config = self.data_cache_page.get_config()
            
            # 保存到磁盘
            success1 = self.config_manager.save_general_config(self.current_general_config)
            success2 = self.config_manager.save_display_config(self.current_display_config)
            success3 = self.config_manager.save_data_config(self.current_data_config)
            
            if success1 and success2 and success3:
                # 更新原始配置备份
                self.original_general_config = self.current_general_config.copy()
                self.original_display_config = self.current_display_config
                self.original_data_config = self.current_data_config.copy()
                
                # 发出应用信号
                self.config_applied.emit(
                    self.current_display_config, 
                    self.current_general_config, 
                    self.current_data_config
                )
                
                print("所有配置已成功应用")
            else:
                print("配置应用失败")
                
        except Exception as e:
            print(f"应用配置时出错: {e}")
            
    def _reset_to_defaults(self):
        """重置为默认值"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要将所有设置重置为默认值吗？这将清除您的所有自定义设置。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 重置显示配置
            default_display_config = DisplayConfig()
            self.current_display_config = default_display_config
            self.chart_display_page.load_config(default_display_config)
            
            # 重置通用配置
            default_general_config = {
                "theme": "light",
                "language": "zh_CN", 
                "auto_load_last_workspace": True,
                "last_workspace_path": ""
            }
            self.current_general_config = default_general_config
            self.general_page.load_config(default_general_config)
            
            # 重置数据配置
            default_data_config = {
                "default_workspace_path": "",
                "auto_save_interval": 300,
                "max_recent_files": 10,
                "cache_enabled": True
            }
            self.current_data_config = default_data_config
            self.data_cache_page.load_config(default_data_config)
            
            # 发出实时预览信号
            self.config_applied.emit(
                self.current_display_config, 
                self.current_general_config, 
                self.current_data_config
            )
        
    def _accept(self):
        """确定按钮 - 应用配置并关闭对话框"""
        self._apply_configs()
        self.accept()
        
    def _cancel(self):
        """取消按钮 - 恢复原始配置并关闭对话框"""
        # 恢复原始配置
        self.current_general_config = self.original_general_config.copy()
        self.current_display_config = self.original_display_config
        self.current_data_config = self.original_data_config.copy()
        
        # 发出恢复信号
        self.config_applied.emit(
            self.current_display_config, 
            self.current_general_config, 
            self.current_data_config
        )
        
        self.reject()
