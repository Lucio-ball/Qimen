"""
工作区案例浏览器组件 (V3版本)
Project: QMW-Persistence (Qi Men Workbench - Persistence Layer)
Task ID: FEAT-20250901-019-V3

工作区模式：显示当前工作区文件夹内的所有.qmw文件
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, QTimer, QFileInfo, QFileSystemWatcher
from PySide6.QtGui import QAction, QIcon, QFont
from typing import List, Dict, Optional
from datetime import datetime


class CaseBrowserWidget(QWidget):
    """工作区案例浏览器组件 - V3版本"""
    
    # 信号定义
    case_file_selected = Signal(str)  # 选择.qmw文件时发射，传递文件路径
    delete_case_requested = Signal(int)  # 请求删除案例时发射，传递案例ID (保留兼容性)
    open_workspace_requested = Signal()  # 请求打开工作区
    new_case_requested = Signal(str)  # 请求在工作区中新建案例，传递工作区路径
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_workspace_path: Optional[str] = None
        self.qmw_files: List[str] = []
        
        # 文件系统监视器（用于自动刷新）
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.directoryChanged.connect(self._on_directory_changed)
        
        self._init_ui()
        self._connect_signals()
        self._show_welcome_state()
        
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)  # 减少整体间距
        layout.setContentsMargins(10, 8, 10, 8)  # 减少边距
        
        # 工作区信息区域 - 紧凑的头部设计
        header_widget = QWidget()
        header_widget.setFixedHeight(50)  # 固定头部高度
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(2)
        
        # 工作区标题 - 更小的字体和间距
        self.workspace_title = QLabel("工作区")
        title_font = QFont()
        title_font.setPointSize(12)  # 从14减少到12
        title_font.setBold(True)
        self.workspace_title.setFont(title_font)
        header_layout.addWidget(self.workspace_title)
        
        # 工作区路径显示 - 更小的字体
        self.workspace_path_label = QLabel("未打开工作区")
        self.workspace_path_label.setStyleSheet("color: gray; font-size: 10px;")  # 从11px减少到10px
        self.workspace_path_label.setWordWrap(True)
        header_layout.addWidget(self.workspace_path_label)
        
        layout.addWidget(header_widget)
        
        # 欢迎区域（无工作区时显示）- 紧凑设计
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_widget)
        welcome_layout.setContentsMargins(15, 10, 15, 10)  # 减少margin
        welcome_layout.setSpacing(8)  # 减少间距
        
        welcome_label = QLabel("欢迎使用奇门遁甲工作台")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 15px; color: #666; margin: 5px 0;")  # 减少margin
        welcome_layout.addWidget(welcome_label)
        
        instruction_label = QLabel("请先打开一个工作区文件夹来开始使用")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet("color: #888; margin: 5px 0;")  # 减少margin
        welcome_layout.addWidget(instruction_label)
        
        self.open_workspace_button = QPushButton("打开工作区...")
        self.open_workspace_button.setFixedHeight(35)  # 固定按钮高度
        self.open_workspace_button.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                padding: 8px 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        welcome_layout.addWidget(self.open_workspace_button, 0, Qt.AlignCenter)
        
        layout.addWidget(self.welcome_widget)
        
        # 案例文件列表 - 给文件列表更多空间
        self.case_list = QListWidget()
        self.case_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.case_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                outline: none;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-left: 3px solid #2196f3;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        layout.addWidget(self.case_list)
        
        # 底部按钮区域 - 紧凑设计
        button_widget = QWidget()
        button_widget.setFixedHeight(35)  # 固定底部高度
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(5, 5, 5, 5)
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setFixedHeight(26)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 4px 12px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:disabled {
                color: #6c757d;
                background-color: #f8f9fa;
            }
        """)
        self.refresh_button.setEnabled(False)
        button_layout.addWidget(self.refresh_button)
        
        button_layout.addStretch()
        
        self.open_workspace_button_bottom = QPushButton("打开工作区...")
        self.open_workspace_button_bottom.setFixedHeight(26)
        self.open_workspace_button_bottom.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 4px 12px;
                border: 1px solid #4CAF50;
                border-radius: 3px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.open_workspace_button_bottom)
        
        layout.addWidget(button_widget)
        
        # 状态标签 - 更紧凑
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #6c757d; font-size: 10px; padding: 2px 5px;")
        self.status_label.setFixedHeight(20)
        layout.addWidget(self.status_label)
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 案例列表信号
        self.case_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.case_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.case_list.customContextMenuRequested.connect(self._show_context_menu)
        
        # 按钮信号
        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        self.open_workspace_button.clicked.connect(self._on_open_workspace_clicked)
        self.open_workspace_button_bottom.clicked.connect(self._on_open_workspace_clicked)
        
    def _show_welcome_state(self):
        """显示欢迎状态"""
        self.welcome_widget.show()
        self.case_list.hide()
        self.refresh_button.setEnabled(False)
        self.status_label.setText("请打开工作区")
        
    def _show_workspace_state(self):
        """显示工作区状态"""
        self.welcome_widget.hide()
        self.case_list.show()
        self.refresh_button.setEnabled(True)
        
    def load_workspace(self, workspace_path: str):
        """
        加载工作区 - V3核心方法
        
        Args:
            workspace_path: 工作区文件夹路径
        """
        if not os.path.exists(workspace_path) or not os.path.isdir(workspace_path):
            QMessageBox.warning(self, "警告", f"工作区路径无效: {workspace_path}")
            return
            
        self.current_workspace_path = workspace_path
        
        # 更新UI显示
        self._show_workspace_state()
        self.workspace_path_label.setText(f"路径: {workspace_path}")
        
        # 设置文件系统监视
        if self.file_watcher.directories():
            self.file_watcher.removePaths(self.file_watcher.directories())
        self.file_watcher.addPath(workspace_path)
        
        # 扫描.qmw文件
        self._scan_qmw_files()
        
    def _scan_qmw_files(self):
        """扫描当前工作区的.qmw文件"""
        if not self.current_workspace_path:
            return
            
        self.status_label.setText("扫描工作区文件...")
        
        try:
            self.qmw_files = []
            
            # 扫描工作区及子文件夹
            for root, dirs, files in os.walk(self.current_workspace_path):
                for file in files:
                    if file.lower().endswith('.qmw'):
                        file_path = os.path.join(root, file)
                        self.qmw_files.append(file_path)
                        
            # 按文件名排序
            self.qmw_files.sort(key=lambda x: os.path.basename(x).lower())
            
            # 更新列表显示
            self._update_file_list()
            
            # 更新状态
            count = len(self.qmw_files)
            self.status_label.setText(f"找到 {count} 个案例文件")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"扫描工作区失败: {str(e)}")
            self.status_label.setText("扫描失败")
            
    def _update_file_list(self):
        """更新文件列表显示"""
        self.case_list.clear()
        
        if not self.qmw_files:
            # 显示空状态
            item = QListWidgetItem("此工作区中没有案例文件")
            item.setForeground(Qt.gray)
            item.setFlags(Qt.NoItemFlags)  # 不可选择
            self.case_list.addItem(item)
            return
            
        for file_path in self.qmw_files:
            # 计算相对路径
            rel_path = os.path.relpath(file_path, self.current_workspace_path)
            
            # 获取文件信息
            file_info = QFileInfo(file_path)
            file_size = file_info.size()
            modified_time = file_info.lastModified().toString("yyyy-MM-dd hh:mm")
            
            # 创建列表项
            item = QListWidgetItem()
            
            # 设置主文本（文件名）
            file_name = os.path.basename(file_path)
            item.setText(file_name)
            
            # 设置详细信息作为工具提示
            tooltip = f"文件: {rel_path}\n路径: {file_path}\n大小: {self._format_file_size(file_size)}\n修改时间: {modified_time}"
            item.setToolTip(tooltip)
            
            # 存储完整路径
            item.setData(Qt.UserRole, file_path)
            
            self.case_list.addItem(item)
            
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
            
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """处理列表项双击事件 - V3版本"""
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            self.case_file_selected.emit(file_path)
        else:
            QMessageBox.warning(self, "警告", "文件不存在或已被移动")
            self._scan_qmw_files()  # 重新扫描
            
    def _on_selection_changed(self):
        """处理选择变化事件"""
        has_selection = bool(self.case_list.currentItem())
        # V3版本中暂时禁用删除功能，因为我们操作的是文件而不是数据库记录
        
    def _on_refresh_clicked(self):
        """处理刷新按钮点击事件"""
        if self.current_workspace_path:
            self._scan_qmw_files()
        else:
            self.status_label.setText("请先打开工作区")
            
    def _on_open_workspace_clicked(self):
        """处理打开工作区按钮点击事件"""
        self.open_workspace_requested.emit()
        
    def _on_directory_changed(self, path: str):
        """处理文件夹变化事件（自动刷新）"""
        if path == self.current_workspace_path:
            # 延迟刷新，避免频繁更新
            QTimer.singleShot(500, self._scan_qmw_files)
            
    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.case_list.itemAt(position)
        
        if item:
            # 文件项的右键菜单
            file_path = item.data(Qt.UserRole)
            if not file_path:
                return
                
            menu = QMenu(self)
            
            # 打开文件
            open_action = QAction("打开案例", self)
            open_action.triggered.connect(lambda: self.case_file_selected.emit(file_path))
            menu.addAction(open_action)
            
            menu.addSeparator()
            
            # 在文件管理器中显示
            show_action = QAction("在文件管理器中显示", self)
            show_action.triggered.connect(lambda: self._show_in_explorer(file_path))
            menu.addAction(show_action)
            
            # 复制文件路径
            copy_path_action = QAction("复制文件路径", self)
            copy_path_action.triggered.connect(lambda: self._copy_file_path(file_path))
            menu.addAction(copy_path_action)
            
            menu.addSeparator()
            
            # 重命名文件
            rename_action = QAction("重命名文件", self)
            rename_action.triggered.connect(lambda: self._rename_file(file_path))
            menu.addAction(rename_action)
            
            # 删除文件
            delete_action = QAction("删除文件", self)
            delete_action.triggered.connect(lambda: self._delete_file(file_path))
            menu.addAction(delete_action)
            
        else:
            # 空白区域的右键菜单
            menu = QMenu(self)
            
            # 新建案例
            new_case_action = QAction("新建案例", self)
            new_case_action.triggered.connect(self._on_new_case_in_workspace)
            menu.addAction(new_case_action)
            
            menu.addSeparator()
            
            # 刷新工作区
            refresh_action = QAction("刷新工作区", self)
            refresh_action.triggered.connect(self._scan_qmw_files)
            menu.addAction(refresh_action)
            
            # 在文件管理器中打开工作区
            if self.current_workspace_path:
                open_folder_action = QAction("在文件管理器中打开工作区", self)
                open_folder_action.triggered.connect(lambda: self._show_in_explorer(self.current_workspace_path))
                menu.addAction(open_folder_action)
            
            menu.addSeparator()
            
            # 打开其他工作区
            open_workspace_action = QAction("打开其他工作区...", self)
            open_workspace_action.triggered.connect(self._on_open_workspace_clicked)
            menu.addAction(open_workspace_action)
        
        menu.exec(self.case_list.mapToGlobal(position))
        
    def _show_in_explorer(self, file_path: str):
        """在文件管理器中显示文件或打开文件夹"""
        import subprocess
        import platform
        import os
        
        # 标准化路径格式
        file_path = os.path.normpath(file_path)
        
        try:
            if platform.system() == "Windows":
                if os.path.isfile(file_path):
                    # 如果是文件，使用/select参数选择文件
                    try:
                        subprocess.run(['explorer', '/select,', file_path], check=True)
                    except subprocess.CalledProcessError:
                        # 如果第一种方法失败，尝试使用cmd方式
                        subprocess.run(f'explorer /select,"{file_path}"', shell=True, check=True)
                elif os.path.isdir(file_path):
                    # 如果是文件夹，直接打开文件夹
                    subprocess.run(['explorer', file_path])
                else:
                    # 如果路径不存在，尝试打开父目录
                    parent_dir = os.path.dirname(file_path)
                    if os.path.exists(parent_dir):
                        subprocess.run(['explorer', parent_dir])
                    else:
                        raise FileNotFoundError(f"路径不存在: {file_path}")
            elif platform.system() == "Darwin":  # macOS
                if os.path.isfile(file_path):
                    subprocess.run(['open', '-R', file_path])
                else:
                    subprocess.run(['open', file_path])
            else:  # Linux
                if os.path.isfile(file_path):
                    subprocess.run(['xdg-open', os.path.dirname(file_path)])
                else:
                    subprocess.run(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.warning(self, "警告", f"无法打开文件管理器: {str(e)}")
            
    def _copy_file_path(self, file_path: str):
        """复制文件路径到剪贴板"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(file_path)
        self.status_label.setText("文件路径已复制到剪贴板")
        
    def _rename_file(self, file_path: str):
        """重命名文件"""
        from PySide6.QtWidgets import QInputDialog
        
        current_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(current_name)[0]
        
        new_name, ok = QInputDialog.getText(
            self, "重命名文件", "新文件名:", text=name_without_ext
        )
        
        if ok and new_name and new_name != name_without_ext:
            try:
                new_file_path = os.path.join(os.path.dirname(file_path), f"{new_name}.qmw")
                os.rename(file_path, new_file_path)
                self._scan_qmw_files()  # 刷新列表
                self.status_label.setText(f"文件已重命名为: {new_name}.qmw")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"重命名失败: {str(e)}")
                
    def _delete_file(self, file_path: str):
        """删除文件"""
        file_name = os.path.basename(file_path)
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除文件 '{file_name}' 吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(file_path)
                self._scan_qmw_files()  # 刷新列表
                self.status_label.setText(f"文件 {file_name} 已删除")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除文件失败: {str(e)}")
    
    def _on_new_case_in_workspace(self):
        """在当前工作区中新建案例"""
        if not self.current_workspace_path:
            QMessageBox.warning(self, "警告", "当前没有打开的工作区")
            return
            
        # 发射信号，让主窗口处理新建案例的逻辑
        self.new_case_requested.emit(self.current_workspace_path)
                
    # 保留兼容性方法（V1/V2版本）
    def refresh_list(self, cases_summary: List[Dict]):
        """
        刷新案例列表 (保留兼容性)
        
        Args:
            cases_summary: 案例摘要列表
        """
        # V3版本中此方法不再使用，但保留以确保兼容性
        pass
        
    def remove_case_from_list(self, case_id: int):
        """
        从列表中移除案例 (保留兼容性)
        
        Args:
            case_id: 案例ID
        """
        # V3版本中此方法不再使用，但保留以确保兼容性
        pass
        
    def get_workspace_path(self) -> Optional[str]:
        """获取当前工作区路径"""
        return self.current_workspace_path
        
    def has_workspace(self) -> bool:
        """检查是否有当前工作区"""
        return self.current_workspace_path is not None
        
    def get_qmw_files(self) -> List[str]:
        """获取当前工作区的.qmw文件列表"""
        return self.qmw_files.copy()
        if reply == QMessageBox.Yes:
            self.delete_case_requested.emit(case_id)
            
    def _on_refresh_clicked(self):
        """处理刷新按钮点击事件"""
        # 发射一个特殊的信号，主窗口可以监听这个信号来刷新列表
        # 这里我们使用一个定时器来模拟刷新过程
        self.status_label.setText("刷新中...")
        QTimer.singleShot(100, lambda: self.status_label.setText("就绪"))
        
        # 在实际应用中，主窗口应该监听这个按钮的点击并重新加载案例列表
        
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
