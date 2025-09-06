"""
中央切换控件 - CentralWidget
Project: QMW-CoreUI (Qi Men Workbench - Core UI)
Task ID: ARCH-20250901-013

核心页面管理器，使用QStackedLayout管理欢迎页面和多案例标签页的切换
解决QDockWidget在QTabWidget作为中央部件时的停靠问题
"""

from PySide6.QtWidgets import QWidget, QStackedLayout, QTabWidget
from PySide6.QtCore import Qt, Signal

from .welcome_widget import WelcomeWidget


class CentralWidget(QWidget):
    """
    中央切换控件
    
    使用QStackedLayout管理两个主要页面：
    - 页面0：欢迎页面（WelcomeWidget）
    - 页面1：多案例标签页（QTabWidget）
    
    提供页面切换的统一接口，确保停靠面板在任何页面下都能正常工作
    """
    
    # 信号：当需要新建案例时发出
    new_case_requested = Signal()
    
    # 信号：当标签页关闭且需要检查是否切换回欢迎页面时发出
    tab_close_requested = Signal(int)  # 传递要关闭的标签页索引
    
    def __init__(self, parent=None):
        """
        初始化中央切换控件
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        
        # 初始化内部组件
        self.welcome_widget = None
        self.tab_widget = None
        self.stacked_layout = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 创建堆叠布局作为主布局
        self.stacked_layout = QStackedLayout(self)
        self.stacked_layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        
        # 页面0：创建欢迎页面
        self.welcome_widget = WelcomeWidget(self)
        self.stacked_layout.addWidget(self.welcome_widget)  # 索引0
        
        # 页面1：创建多案例标签页
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)  # 允许关闭标签页
        self.tab_widget.setMovable(True)       # 允许拖拽标签页
        self.tab_widget.setDocumentMode(True)  # 文档模式，更好的外观
        self.tab_widget.setUsesScrollButtons(True)  # 支持滚动按钮
        self.stacked_layout.addWidget(self.tab_widget)  # 索引1
        
        # 默认显示欢迎页面
        self.stacked_layout.setCurrentIndex(0)
    
    def _connect_signals(self):
        """连接信号槽"""
        # 连接欢迎页面的新建案例信号
        if self.welcome_widget:
            self.welcome_widget.new_case_requested.connect(self.new_case_requested.emit)
        
        # 连接标签页的关闭信号
        if self.tab_widget:
            self.tab_widget.tabCloseRequested.connect(self._handle_tab_close_request)
    
    def _handle_tab_close_request(self, index):
        """
        处理标签页关闭请求
        
        Args:
            index: 要关闭的标签页索引
        """
        # 发出信号让MainWindow处理
        self.tab_close_requested.emit(index)
    
    def show_page(self, index):
        """
        切换到指定页面
        
        Args:
            index: 页面索引
                   0 - 欢迎页面
                   1 - 多案例标签页
        """
        if 0 <= index < self.stacked_layout.count():
            self.stacked_layout.setCurrentIndex(index)
            
            # 更新页面状态
            if index == 0:
                # 切换到欢迎页面
                self._update_welcome_page_state()
            elif index == 1:
                # 切换到多案例页面
                self._update_multi_case_page_state()
    
    def _update_welcome_page_state(self):
        """更新欢迎页面状态"""
        # 如果有需要，可以在这里更新欢迎页面的显示状态
        pass
    
    def _update_multi_case_page_state(self):
        """更新多案例页面状态"""
        # 如果有需要，可以在这里更新标签页的显示状态
        pass
    
    def get_current_page_index(self):
        """
        获取当前显示的页面索引
        
        Returns:
            int: 当前页面索引
        """
        return self.stacked_layout.currentIndex()
    
    def is_welcome_page_active(self):
        """
        检查当前是否显示欢迎页面
        
        Returns:
            bool: True if 欢迎页面活跃
        """
        return self.get_current_page_index() == 0
    
    def is_multi_case_page_active(self):
        """
        检查当前是否显示多案例页面
        
        Returns:
            bool: True if 多案例页面活跃
        """
        return self.get_current_page_index() == 1
    
    def get_tab_count(self):
        """
        获取标签页数量
        
        Returns:
            int: 标签页数量
        """
        return self.tab_widget.count() if self.tab_widget else 0
    
    def add_tab(self, widget, title):
        """
        添加新标签页
        
        Args:
            widget: 标签页内容组件
            title: 标签页标题
            
        Returns:
            int: 新标签页的索引
        """
        if self.tab_widget:
            index = self.tab_widget.addTab(widget, title)
            self.tab_widget.setCurrentIndex(index)
            return index
        return -1
    
    def remove_tab(self, index):
        """
        移除指定索引的标签页
        
        Args:
            index: 要移除的标签页索引
        """
        if self.tab_widget and 0 <= index < self.tab_widget.count():
            self.tab_widget.removeTab(index)
    
    def set_current_tab(self, index):
        """
        设置当前活跃的标签页
        
        Args:
            index: 标签页索引
        """
        if self.tab_widget and 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
    
    def get_current_tab_widget(self):
        """
        获取当前标签页的组件
        
        Returns:
            QWidget: 当前标签页的组件，如果没有则返回None
        """
        if self.tab_widget and self.tab_widget.count() > 0:
            return self.tab_widget.currentWidget()
        return None
