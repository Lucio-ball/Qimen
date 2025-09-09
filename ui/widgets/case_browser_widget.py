"""
案例浏览器组件
Project: QMW-Persistence (Qi Men Workbench - Persistence Layer)
Task ID: FEAT-20250901-019

提供案例列表显示、选择和管理功能
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction
from typing import List, Dict, Optional
from datetime import datetime


class CaseBrowserWidget(QWidget):
    """案例浏览器组件"""
    
    # 信号定义
    case_double_clicked = Signal(int)  # 双击案例时发射，传递案例ID
    delete_case_requested = Signal(int)  # 请求删除案例时发射，传递案例ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题标签
        title_label = QLabel("案例浏览器")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title_label)
        
        # 案例列表
        self.case_list = QListWidget()
        self.case_list.setContextMenuPolicy(Qt.CustomContextMenu)
        layout.addWidget(self.case_list)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("删除选中")
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("刷新")
        button_layout.addWidget(self.refresh_button)
        
        button_layout.addStretch()  # 添加弹性空间
        
        layout.addLayout(button_layout)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: gray; font-size: 12px; padding: 2px;")
        layout.addWidget(self.status_label)
        
    def _connect_signals(self):
        """连接信号和槽"""
        self.case_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.case_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.case_list.customContextMenuRequested.connect(self._show_context_menu)
        self.delete_button.clicked.connect(self._on_delete_clicked)
        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        
    def refresh_list(self, cases_summary: List[Dict]):
        """
        刷新案例列表
        
        Args:
            cases_summary: 案例摘要列表，格式为 [{'id': int, 'name': str, 'query_time': str, 'creation_time': str}, ...]
        """
        self.case_list.clear()
        
        if not cases_summary:
            self.status_label.setText("暂无保存的案例")
            return
            
        for case_info in cases_summary:
            self._add_case_item(case_info)
            
        self.status_label.setText(f"共 {len(cases_summary)} 个案例")
        
    def _add_case_item(self, case_info: Dict):
        """
        添加案例项到列表
        
        Args:
            case_info: 案例信息字典
        """
        case_id = case_info['id']
        case_name = case_info['name']
        query_time = case_info['query_time']
        creation_time = case_info['creation_time']
        
        # 格式化时间显示
        try:
            # 尝试解析ISO格式时间
            if 'T' in query_time:
                query_dt = datetime.fromisoformat(query_time.replace('Z', '+00:00'))
                query_time_str = query_dt.strftime("%Y-%m-%d %H:%M")
            else:
                query_time_str = query_time
        except:
            query_time_str = query_time
            
        try:
            if 'T' in creation_time:
                creation_dt = datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
                creation_time_str = creation_dt.strftime("%Y-%m-%d %H:%M")
            else:
                creation_time_str = creation_time
        except:
            creation_time_str = creation_time
        
        # 创建列表项文本
        item_text = f"{case_name}\n起局: {query_time_str}\n保存: {creation_time_str}"
        
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, case_id)  # 存储案例ID
        
        # 设置项的工具提示
        tooltip = f"案例名称: {case_name}\n起局时间: {query_time_str}\n保存时间: {creation_time_str}\n\n双击打开案例"
        item.setToolTip(tooltip)
        
        self.case_list.addItem(item)
        
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """处理列表项双击事件"""
        case_id = item.data(Qt.UserRole)
        if case_id is not None:
            self.case_double_clicked.emit(case_id)
            
    def _on_selection_changed(self):
        """处理选择变化事件"""
        has_selection = bool(self.case_list.currentItem())
        self.delete_button.setEnabled(has_selection)
        
    def _on_delete_clicked(self):
        """处理删除按钮点击事件"""
        current_item = self.case_list.currentItem()
        if not current_item:
            return
            
        case_id = current_item.data(Qt.UserRole)
        case_name = current_item.text().split('\n')[0]  # 获取案例名称（第一行）
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除案例 '{case_name}' 吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_case_requested.emit(case_id)
            
    def _on_refresh_clicked(self):
        """处理刷新按钮点击事件"""
        # 发射一个特殊的信号，主窗口可以监听这个信号来刷新列表
        # 这里我们使用一个定时器来模拟刷新过程
        self.status_label.setText("刷新中...")
        QTimer.singleShot(100, lambda: self.status_label.setText("就绪"))
        
        # 在实际应用中，主窗口应该监听这个按钮的点击并重新加载案例列表
        
    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.case_list.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        
        # 打开案例
        open_action = QAction("打开案例", self)
        open_action.triggered.connect(lambda: self._on_item_double_clicked(item))
        menu.addAction(open_action)
        
        menu.addSeparator()
        
        # 删除案例
        delete_action = QAction("删除案例", self)
        delete_action.triggered.connect(self._on_delete_clicked)
        menu.addAction(delete_action)
        
        # 显示菜单
        menu.exec_(self.case_list.mapToGlobal(position))
        
    def get_selected_case_id(self) -> Optional[int]:
        """
        获取当前选中的案例ID
        
        Returns:
            Optional[int]: 选中的案例ID，如果没有选中则返回None
        """
        current_item = self.case_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
        
    def select_case_by_id(self, case_id: int) -> bool:
        """
        根据案例ID选中对应的列表项
        
        Args:
            case_id: 要选中的案例ID
            
        Returns:
            bool: 成功选中返回True，否则返回False
        """
        for i in range(self.case_list.count()):
            item = self.case_list.item(i)
            if item.data(Qt.UserRole) == case_id:
                self.case_list.setCurrentItem(item)
                return True
        return False
        
    def remove_case_from_list(self, case_id: int):
        """
        从列表中移除指定的案例项
        
        Args:
            case_id: 要移除的案例ID
        """
        for i in range(self.case_list.count()):
            item = self.case_list.item(i)
            if item.data(Qt.UserRole) == case_id:
                self.case_list.takeItem(i)
                break
                
        # 更新状态
        count = self.case_list.count()
        if count == 0:
            self.status_label.setText("暂无保存的案例")
        else:
            self.status_label.setText(f"共 {count} 个案例")
            
    def set_status(self, message: str):
        """
        设置状态消息
        
        Args:
            message: 状态消息
        """
        self.status_label.setText(message)
