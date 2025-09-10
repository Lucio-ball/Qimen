#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模板管理器对话框 - TemplateManagerDialog
用于管理自动标注模板的创建、编辑和删除
"""

import json
import os
import sys
from typing import Dict, List, Optional

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发环境和PyInstaller打包环境"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的应用程序
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QLineEdit, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QMessageBox,
    QComboBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class TemplateManagerDialog(QDialog):
    """模板管理器对话框"""
    
    # 信号：当模板发生变化时发出，通知外部刷新
    templates_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("模板管理器")
        self.setMinimumSize(800, 600)
        
        # 数据文件路径
        self.templates_file = get_resource_path("data/templates.json")
        
        # 当前编辑的模板数据
        self.current_template_data: List[Dict] = []
        self.current_template_name: str = ""
        
        # 参数类型映射
        self.param_type_mapping = {
            "special": "特殊参数",
            "baShen": "八神",
            "tianGan": "天干", 
            "jiuXing": "九星",
            "baMen": "八门",
            "zhiFu": "值符",
            "zhiShi": "值使",
            "riGan": "日干",
            "shiGan": "时干"
        }
        
        self.reverse_param_type_mapping = {v: k for k, v in self.param_type_mapping.items()}
        
        # 各参数类型对应的选项数据
        self.param_options = {
            "special": ["太岁", "月干", "日干", "时干", "年命"],
            "baShen": ["直符", "螣蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"],
            "tianGan": ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"],
            "jiuXing": ["天蓬", "天任", "天冲", "天辅", "天英", "天芮", "天心", "天柱", "天禽"],
            "baMen": ["休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"],
            "zhiFu": ["值符星"],  # 值符是动态的，通常就是值符星
            "zhiShi": ["值使门"],  # 值使是动态的，通常就是值使门
            "riGan": ["日干"],     # 日干是动态的
            "shiGan": ["时干"]     # 时干是动态的
        }
        
        self._setup_ui()
        self._load_templates()
        
    def _setup_ui(self):
        """设置UI界面"""
        main_layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：模板列表
        self._create_left_panel(splitter)
        
        # 右侧：编辑区域
        self._create_right_panel(splitter)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
        # 底部按钮区域
        self._create_bottom_buttons(main_layout)
        
    def _create_left_panel(self, parent):
        """创建左侧模板列表面板"""
        left_widget = QVBoxLayout()
        
        # 标题
        title_label = QLabel("模板列表")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        left_widget.addWidget(title_label)
        
        # 模板列表
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self._on_template_selected)
        left_widget.addWidget(self.template_list)
        
        # 新建按钮
        new_button = QPushButton("新建模板")
        new_button.clicked.connect(self._create_new_template)
        left_widget.addWidget(new_button)
        
        # 包装到widget
        left_panel = QVBoxLayout()
        left_panel.addLayout(left_widget)
        
        from PySide6.QtWidgets import QWidget
        left_container = QWidget()
        left_container.setLayout(left_panel)
        parent.addWidget(left_container)
        
    def _create_right_panel(self, parent):
        """创建右侧编辑面板"""
        right_layout = QVBoxLayout()
        
        # 模板名称编辑
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("模板名称："))
        self.template_name_edit = QLineEdit()
        self.template_name_edit.textChanged.connect(self._on_template_name_changed)
        name_layout.addWidget(self.template_name_edit)
        right_layout.addLayout(name_layout)
        
        # 标注内容表格
        content_label = QLabel("标注内容")
        content_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        right_layout.addWidget(content_label)
        
        self.content_table = QTableWidget()
        self.content_table.setColumnCount(3)
        self.content_table.setHorizontalHeaderLabels(["参数类型", "参数名称", "标注文本"])
        
        # 设置表格属性
        header = self.content_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 标注文本列可伸缩
        
        # 设置垂直表头（行）属性，支持自动调整行高
        vertical_header = self.content_table.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.content_table.setAlternatingRowColors(True)
        self.content_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # 设置文本换行
        self.content_table.setWordWrap(True)
        
        right_layout.addWidget(self.content_table)
        
        # 表格操作按钮
        table_buttons_layout = QHBoxLayout()
        add_row_button = QPushButton("添加标注")
        add_row_button.clicked.connect(self._add_table_row)
        delete_row_button = QPushButton("删除选中")
        delete_row_button.clicked.connect(self._delete_table_row)
        
        table_buttons_layout.addWidget(add_row_button)
        table_buttons_layout.addWidget(delete_row_button)
        table_buttons_layout.addStretch()
        
        right_layout.addLayout(table_buttons_layout)
        
        # 包装到widget
        from PySide6.QtWidgets import QWidget
        right_container = QWidget()
        right_container.setLayout(right_layout)
        parent.addWidget(right_container)
        
    def _create_bottom_buttons(self, parent_layout):
        """创建底部按钮"""
        buttons_layout = QHBoxLayout()
        
        # 保存按钮
        save_button = QPushButton("保存模板")
        save_button.clicked.connect(self._save_current_template)
        
        # 删除按钮
        delete_button = QPushButton("删除模板")
        delete_button.clicked.connect(self._delete_current_template)
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_button)
        
        parent_layout.addLayout(buttons_layout)
        
    def _load_templates(self):
        """加载模板数据"""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    templates_data = json.load(f)
                    
                # 填充模板列表（排除_default_模板）
                self.template_list.clear()
                for template_name in templates_data.keys():
                    if template_name != "_default_":
                        item = QListWidgetItem(template_name)
                        self.template_list.addItem(item)
                        
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载模板文件失败：{str(e)}")
            
    def _on_template_selected(self, item: QListWidgetItem):
        """模板被选中时的处理"""
        template_name = item.text()
        self._load_template_content(template_name)
        
    def _load_template_content(self, template_name: str):
        """加载指定模板的内容到编辑区"""
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
                
            if template_name in templates_data:
                self.current_template_name = template_name
                self.current_template_data = templates_data[template_name].copy()
                
                # 更新UI
                self.template_name_edit.setText(template_name)
                self._populate_content_table()
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载模板内容失败：{str(e)}")
            
    def _populate_content_table(self):
        """填充内容表格"""
        self.content_table.setRowCount(len(self.current_template_data))
        
        for row, item_data in enumerate(self.current_template_data):
            # 参数类型下拉框
            type_combo = QComboBox()
            type_combo.addItems(list(self.param_type_mapping.values()))
            type_combo.currentTextChanged.connect(lambda text, r=row: self._on_param_type_changed(r, text))
            
            # 设置当前值
            param_type = item_data.get("param_type", "")
            if param_type in self.param_type_mapping:
                type_combo.setCurrentText(self.param_type_mapping[param_type])
            
            self.content_table.setCellWidget(row, 0, type_combo)
            
            # 参数名称下拉框
            name_combo = QComboBox()
            name_combo.setEditable(True)  # 允许编辑
            self.content_table.setCellWidget(row, 1, name_combo)
            
            # 设置参数名称选项
            if param_type in self.param_options:
                name_combo.addItems(self.param_options[param_type])
            
            # 设置当前参数名称值
            param_name = item_data.get("param_name", item_data.get("param_value", ""))
            if param_name:
                # 如果当前值在选项中，选中它；否则直接设置文本
                if param_name in [name_combo.itemText(i) for i in range(name_combo.count())]:
                    name_combo.setCurrentText(str(param_name))
                else:
                    name_combo.setEditText(str(param_name))
            
            # 标注文本
            label = item_data.get("label", "")
            label_item = QTableWidgetItem(label)
            # 设置文本换行标志
            label_item.setFlags(label_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.content_table.setItem(row, 2, label_item)
            
    def _add_table_row(self):
        """添加新的表格行"""
        row_count = self.content_table.rowCount()
        self.content_table.insertRow(row_count)
        
        # 添加参数类型下拉框
        type_combo = QComboBox()
        type_combo.addItems(list(self.param_type_mapping.values()))
        type_combo.currentTextChanged.connect(lambda text, row=row_count: self._on_param_type_changed(row, text))
        self.content_table.setCellWidget(row_count, 0, type_combo)
        
        # 添加参数名称下拉框
        name_combo = QComboBox()
        name_combo.setEditable(True)  # 允许编辑，以防有特殊需求
        self.content_table.setCellWidget(row_count, 1, name_combo)
        
        # 添加标注文本
        text_item = QTableWidgetItem("")
        text_item.setFlags(text_item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.content_table.setItem(row_count, 2, text_item)
        
        # 初始化参数名称选项（默认选择第一个参数类型）
        if list(self.param_type_mapping.values()):
            first_type = list(self.param_type_mapping.values())[0]
            self._on_param_type_changed(row_count, first_type)
            
    def _on_param_type_changed(self, row: int, param_type_display: str):
        """参数类型改变时更新参数名称下拉菜单"""
        # 获取对应的参数类型key
        param_type = self.reverse_param_type_mapping.get(param_type_display, "")
        
        # 获取参数名称下拉框
        name_combo = self.content_table.cellWidget(row, 1)
        if not isinstance(name_combo, QComboBox):
            return
            
        # 清空现有选项
        name_combo.clear()
        
        # 根据参数类型添加对应选项
        if param_type in self.param_options:
            options = self.param_options[param_type]
            name_combo.addItems(options)
            
            # 如果只有一个选项，自动选择
            if len(options) == 1:
                name_combo.setCurrentIndex(0)
        
    def _delete_table_row(self):
        """删除选中的表格行"""
        current_row = self.content_table.currentRow()
        if current_row >= 0:
            self.content_table.removeRow(current_row)
            
    def _create_new_template(self):
        """创建新模板"""
        self.current_template_name = ""
        self.current_template_data = []
        
        # 清空编辑区
        self.template_name_edit.setText("")
        self.content_table.setRowCount(0)
        
        # 清除列表选择
        self.template_list.clearSelection()
        
    def _on_template_name_changed(self):
        """模板名称改变时的处理"""
        # 更新当前模板名称
        new_name = self.template_name_edit.text().strip()
        if new_name:
            self.current_template_name = new_name
            
    def _save_current_template(self):
        """保存当前模板"""
        # 验证输入
        template_name = self.template_name_edit.text().strip()
        if not template_name:
            QMessageBox.warning(self, "错误", "请输入模板名称")
            return
            
        if template_name == "_default_":
            QMessageBox.warning(self, "错误", "不能使用保留名称 '_default_'")
            return
            
        # 收集表格数据
        template_data = []
        for row in range(self.content_table.rowCount()):
            type_combo = self.content_table.cellWidget(row, 0)
            name_combo = self.content_table.cellWidget(row, 1)
            label_item = self.content_table.item(row, 2)
            
            if type_combo and name_combo and label_item:
                param_type_display = type_combo.currentText()
                param_type = self.reverse_param_type_mapping.get(param_type_display, "")
                param_name = name_combo.currentText().strip()
                label = label_item.text().strip()
                
                if param_type and label:  # 至少需要类型和标注文本
                    item_data = {
                        "param_type": param_type,
                        "label": label
                    }
                    
                    # 根据参数类型决定使用param_name还是param_value
                    if param_type == "special":
                        item_data["param_name"] = param_name
                    else:
                        item_data["param_value"] = param_name if param_name else None
                        
                    template_data.append(item_data)
                    
        if not template_data:
            QMessageBox.warning(self, "错误", "请至少添加一个有效的标注项")
            return
            
        # 保存到文件
        try:
            # 读取现有数据
            templates_data = {}
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    templates_data = json.load(f)
                    
            # 更新数据
            templates_data[template_name] = template_data
            
            # 写入文件
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, ensure_ascii=False, indent=2)
                
            # 更新UI
            self._reload_template_list()
            self._select_template_in_list(template_name)
            
            # 发出变化信号
            self.templates_changed.emit()
            
            QMessageBox.information(self, "成功", f"模板 '{template_name}' 已保存")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存模板失败：{str(e)}")
            
    def _delete_current_template(self):
        """删除当前模板"""
        if not self.current_template_name:
            QMessageBox.warning(self, "错误", "请先选择要删除的模板")
            return
            
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除模板 '{self.current_template_name}' 吗？\n此操作无法撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 读取现有数据
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    templates_data = json.load(f)
                    
                # 删除模板
                if self.current_template_name in templates_data:
                    del templates_data[self.current_template_name]
                    
                    # 写入文件
                    with open(self.templates_file, 'w', encoding='utf-8') as f:
                        json.dump(templates_data, f, ensure_ascii=False, indent=2)
                        
                    # 更新UI
                    self._reload_template_list()
                    self._create_new_template()  # 清空编辑区
                    
                    # 发出变化信号
                    self.templates_changed.emit()
                    
                    QMessageBox.information(self, "成功", f"模板 '{self.current_template_name}' 已删除")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除模板失败：{str(e)}")
                
    def _reload_template_list(self):
        """重新加载模板列表"""
        self._load_templates()
        
    def _select_template_in_list(self, template_name: str):
        """在列表中选中指定模板"""
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            if item.text() == template_name:
                self.template_list.setCurrentItem(item)
                break
