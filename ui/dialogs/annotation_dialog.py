"""
标注管理对话框 - 管理单个参数的多个标注
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QListWidgetItem, QPushButton, QLineEdit, QComboBox, 
                               QColorDialog, QLabel, QMessageBox, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from typing import List, Dict


class AnnotationDialog(QDialog):
    """标注管理对话框"""
    
    # 信号：标注数据变更
    annotations_changed = Signal(str, list)  # param_id, annotations_list
    
    def __init__(self, param_id: str, param_name: str, annotations: List[Dict[str, str]], parent=None):
        super().__init__(parent)
        self.param_id = param_id
        self.param_name = param_name
        self.annotations = annotations.copy()  # 复制一份避免直接修改原数据
        
        self._setup_ui()
        self._load_annotations()
        self._connect_signals()
        
    def _setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle(f"标注管理 - {self.param_name}")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 顶部信息
        info_label = QLabel(f"参数: {self.param_name}")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # 标注列表
        list_group = QGroupBox("标注列表")
        list_layout = QVBoxLayout(list_group)
        
        self.annotation_list = QListWidget()
        list_layout.addWidget(self.annotation_list)
        
        # 列表操作按钮
        list_button_layout = QHBoxLayout()
        self.delete_button = QPushButton("删除选中")
        self.delete_button.setEnabled(False)
        self.move_up_button = QPushButton("上移")
        self.move_up_button.setEnabled(False)
        self.move_down_button = QPushButton("下移")
        self.move_down_button.setEnabled(False)
        
        list_button_layout.addWidget(self.delete_button)
        list_button_layout.addWidget(self.move_up_button)
        list_button_layout.addWidget(self.move_down_button)
        list_button_layout.addStretch()
        
        list_layout.addLayout(list_button_layout)
        layout.addWidget(list_group)
        
        # 添加新标注区域
        add_group = QGroupBox("添加新标注")
        add_layout = QVBoxLayout(add_group)
        
        # 文本输入
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("文本:"))
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("输入标注文本...")
        text_layout.addWidget(self.text_edit)
        add_layout.addLayout(text_layout)
        
        # 不再提供形状和颜色选择，使用默认值
        
        # 添加按钮
        self.add_button = QPushButton("添加标注")
        add_layout.addWidget(self.add_button)
        
        layout.addWidget(add_group)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def _connect_signals(self):
        """连接信号槽"""
        self.annotation_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.delete_button.clicked.connect(self._delete_selected)
        self.move_up_button.clicked.connect(self._move_up)
        self.move_down_button.clicked.connect(self._move_down)
        self.add_button.clicked.connect(self._add_annotation)
        self.ok_button.clicked.connect(self._save_and_close)
        self.cancel_button.clicked.connect(self.reject)
        
        # 回车键快速添加
        self.text_edit.returnPressed.connect(self._add_annotation)
        
    def _load_annotations(self):
        """加载标注到列表"""
        self.annotation_list.clear()
        
        for i, annotation in enumerate(self.annotations):
            item = QListWidgetItem()
            item.setText(annotation["text"])
            
            # 创建颜色图标
            icon = self._create_color_icon(annotation["color"], annotation["shape"])
            item.setIcon(icon)
            
            # 存储索引
            item.setData(Qt.UserRole, i)
            
            self.annotation_list.addItem(item)
            
    def _create_color_icon(self, color: str, shape: str) -> QIcon:
        """创建颜色和形状图标"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        qcolor = QColor(color)
        painter.setBrush(qcolor)
        painter.setPen(qcolor)
        
        if shape == "circle":
            painter.drawEllipse(2, 2, 12, 12)
        elif shape == "square":
            painter.drawRect(2, 2, 12, 12)
        elif shape == "triangle":
            from PySide6.QtGui import QPolygon
            from PySide6.QtCore import QPoint
            triangle = QPolygon([QPoint(8, 2), QPoint(2, 14), QPoint(14, 14)])
            painter.drawPolygon(triangle)
        
        painter.end()
        return QIcon(pixmap)
        
    def _on_selection_changed(self):
        """列表选择变化"""
        has_selection = self.annotation_list.currentItem() is not None
        current_row = self.annotation_list.currentRow()
        
        self.delete_button.setEnabled(has_selection)
        self.move_up_button.setEnabled(has_selection and current_row > 0)
        self.move_down_button.setEnabled(has_selection and current_row < self.annotation_list.count() - 1)
        
    def _delete_selected(self):
        """删除选中的标注"""
        current_item = self.annotation_list.currentItem()
        if not current_item:
            return
            
        row = self.annotation_list.row(current_item)
        
        # 直接删除，不需要确认对话框
        if 0 <= row < len(self.annotations):
            self.annotations.pop(row)
        
        # 重新加载列表
        self._load_annotations()
            
    def _move_up(self):
        """上移选中的标注"""
        current_row = self.annotation_list.currentRow()
        if current_row > 0:
            # 交换数据
            self.annotations[current_row], self.annotations[current_row - 1] = \
                self.annotations[current_row - 1], self.annotations[current_row]
            
            # 重新加载并保持选择
            self._load_annotations()
            self.annotation_list.setCurrentRow(current_row - 1)
            
    def _move_down(self):
        """下移选中的标注"""
        current_row = self.annotation_list.currentRow()
        if current_row < len(self.annotations) - 1:
            # 交换数据
            self.annotations[current_row], self.annotations[current_row + 1] = \
                self.annotations[current_row + 1], self.annotations[current_row]
            
            # 重新加载并保持选择
            self._load_annotations()
            self.annotation_list.setCurrentRow(current_row + 1)
            
    def _add_annotation(self):
        """添加新标注"""
        text = self.text_edit.text().strip()
        if not text:
            QMessageBox.warning(self, "警告", "请输入标注文本！")
            return
            
        # 检查是否重复
        for annotation in self.annotations:
            if annotation["text"] == text:
                QMessageBox.warning(self, "警告", f"标注 '{text}' 已存在！")
                return
                
        # 添加新标注（使用默认形状和颜色）
        new_annotation = {
            "text": text,
            "shape": "circle",  # 固定使用圆形
            "color": "#FF0000"  # 固定使用红色
        }
        
        self.annotations.append(new_annotation)
        
        # 重新加载列表
        self._load_annotations()
        
        # 清空输入
        self.text_edit.clear()
        
        # 选择新添加的项
        self.annotation_list.setCurrentRow(len(self.annotations) - 1)
        
    def _save_and_close(self):
        """保存并关闭"""
        # 发射信号通知数据变更
        self.annotations_changed.emit(self.param_id, self.annotations)
        self.accept()
        
    def get_annotations(self) -> List[Dict[str, str]]:
        """获取标注数据"""
        return self.annotations.copy()
