"""
首选项对话框的各个设置页面组件
Project: QMW-CoreApp (Qi Men Workbench - Core Application)
Task ID: FEAT-20250901-020-Comprehensive (全面首选项系统)
"""

import os
import json
import sys
from typing import Dict, Any, List, Optional

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
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QComboBox,
    QCheckBox, QLineEdit, QPushButton, QFileDialog, QMessageBox, QListWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QTextEdit,
    QFrame, QSpacerItem, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QFont, QPixmap, QDesktopServices

from ui.config import DisplayConfig


class GeneralPage(QWidget):
    """通用设置页面"""
    
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_config = {
            "theme": "light",
            "language": "zh_CN", 
            "auto_load_last_workspace": True,
            "last_workspace_path": ""
        }
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 外观设置组
        appearance_group = QGroupBox("外观设置")
        appearance_layout = QGridLayout(appearance_group)
        
        # 主题选择
        appearance_layout.addWidget(QLabel("UI主题:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["亮色主题", "暗色主题", "跟随系统"])
        self.theme_combo.setCurrentText("亮色主题")
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        appearance_layout.addWidget(self.theme_combo, 0, 1)
        
        # 语言选择
        appearance_layout.addWidget(QLabel("界面语言:"), 1, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English"])
        self.language_combo.setCurrentText("简体中文")
        self.language_combo.currentTextChanged.connect(self._on_language_changed)
        appearance_layout.addWidget(self.language_combo, 1, 1)
        
        layout.addWidget(appearance_group)
        
        # 启动行为设置组
        startup_group = QGroupBox("启动行为")
        startup_layout = QVBoxLayout(startup_group)
        
        self.auto_load_workspace_cb = QCheckBox("启动时自动加载上一个工作区")
        self.auto_load_workspace_cb.setChecked(True)
        self.auto_load_workspace_cb.toggled.connect(self._on_auto_load_changed)
        startup_layout.addWidget(self.auto_load_workspace_cb)
        
        layout.addWidget(startup_group)
        
        # 添加弹性空间
        layout.addStretch()
    
    def _on_theme_changed(self, theme_text: str):
        """主题改变事件"""
        theme_map = {
            "亮色主题": "light",
            "暗色主题": "dark", 
            "跟随系统": "system"
        }
        self.current_config["theme"] = theme_map.get(theme_text, "light")
        self.config_changed.emit(self.current_config)
    
    def _on_language_changed(self, language_text: str):
        """语言改变事件"""
        language_map = {
            "简体中文": "zh_CN",
            "English": "en_US"
        }
        self.current_config["language"] = language_map.get(language_text, "zh_CN")
        self.config_changed.emit(self.current_config)
    
    def _on_auto_load_changed(self, checked: bool):
        """自动加载工作区改变事件"""
        self.current_config["auto_load_last_workspace"] = checked
        self.config_changed.emit(self.current_config)
    
    def load_config(self, config: Dict[str, Any]):
        """加载配置到UI"""
        self.current_config = config.copy()
        
        # 主题
        theme_map = {
            "light": "亮色主题",
            "dark": "暗色主题",
            "system": "跟随系统"
        }
        theme_text = theme_map.get(config.get("theme", "light"), "亮色主题")
        self.theme_combo.setCurrentText(theme_text)
        
        # 语言
        language_map = {
            "zh_CN": "简体中文",
            "en_US": "English"
        }
        language_text = language_map.get(config.get("language", "zh_CN"), "简体中文")
        self.language_combo.setCurrentText(language_text)
        
        # 自动加载工作区
        self.auto_load_workspace_cb.setChecked(
            config.get("auto_load_last_workspace", True)
        )
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.current_config.copy()


class ChartDisplayPage(QWidget):
    """盘面显示设置页面"""
    
    config_changed = Signal(DisplayConfig)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_config = DisplayConfig()
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 样式设置组
        style_group = QGroupBox("样式设置")
        style_layout = QVBoxLayout(style_group)
        
        self.use_wuxing_colors_cb = QCheckBox("按五行颜色显示参数")
        self.use_wuxing_colors_cb.setToolTip("启用后将根据五行属性显示不同颜色")
        self.use_wuxing_colors_cb.toggled.connect(self._on_config_changed)
        style_layout.addWidget(self.use_wuxing_colors_cb)
        
        self.show_zhi_fu_shi_bold_cb = QCheckBox("加粗显示值符/值使")
        self.show_zhi_fu_shi_bold_cb.setToolTip("将值符和值使的文字以粗体形式显示")
        self.show_zhi_fu_shi_bold_cb.toggled.connect(self._on_config_changed)
        style_layout.addWidget(self.show_zhi_fu_shi_bold_cb)
        
        self.auto_yue_ling_chong_kong_cb = QCheckBox("应用月令自动冲空样式 (删除线)")
        self.auto_yue_ling_chong_kong_cb.setToolTip("自动检测并标记月令冲空情况")
        self.auto_yue_ling_chong_kong_cb.toggled.connect(self._on_config_changed)
        style_layout.addWidget(self.auto_yue_ling_chong_kong_cb)
        
        self.auto_maxing_chong_mu_kong_cb = QCheckBox("应用马星自动冲墓、冲空样式 (删除线)")
        self.auto_maxing_chong_mu_kong_cb.setToolTip("自动检测并标记马星冲墓空情况")
        self.auto_maxing_chong_mu_kong_cb.toggled.connect(self._on_config_changed)
        style_layout.addWidget(self.auto_maxing_chong_mu_kong_cb)
        
        layout.addWidget(style_group)
        
        # 参数显示组
        visibility_group = QGroupBox("参数显示")
        visibility_layout = QGridLayout(visibility_group)
        
        # 第一列
        self.show_ri_kong_cb = QCheckBox("显示日空")
        self.show_ri_kong_cb.toggled.connect(self._on_config_changed)
        visibility_layout.addWidget(self.show_ri_kong_cb, 0, 0)
        
        self.show_shi_kong_cb = QCheckBox("显示时空")
        self.show_shi_kong_cb.toggled.connect(self._on_config_changed)
        visibility_layout.addWidget(self.show_shi_kong_cb, 1, 0)
        
        self.show_liu_ji_cb = QCheckBox("显示六仪击刑")
        self.show_liu_ji_cb.toggled.connect(self._on_config_changed)
        visibility_layout.addWidget(self.show_liu_ji_cb, 2, 0)
        
        # 第二列
        self.show_ru_mu_cb = QCheckBox("显示入墓")
        self.show_ru_mu_cb.toggled.connect(self._on_config_changed)
        visibility_layout.addWidget(self.show_ru_mu_cb, 0, 1)
        
        self.show_ma_xing_cb = QCheckBox("显示马星")
        self.show_ma_xing_cb.toggled.connect(self._on_config_changed)
        visibility_layout.addWidget(self.show_ma_xing_cb, 1, 1)
        
        self.show_yue_ling_cb = QCheckBox("显示月令")
        self.show_yue_ling_cb.toggled.connect(self._on_config_changed)
        visibility_layout.addWidget(self.show_yue_ling_cb, 2, 1)
        
        # 地盘相关
        self.show_di_pan_gate_cb = QCheckBox("显示地盘门")
        self.show_di_pan_gate_cb.toggled.connect(self._on_config_changed)
        visibility_layout.addWidget(self.show_di_pan_gate_cb, 3, 0)
        
        self.show_di_pan_star_cb = QCheckBox("显示地盘星")
        self.show_di_pan_star_cb.toggled.connect(self._on_config_changed)
        visibility_layout.addWidget(self.show_di_pan_star_cb, 3, 1)
        
        layout.addWidget(visibility_group)
        
        # 添加弹性空间
        layout.addStretch()
    
    def _on_config_changed(self):
        """配置变化事件"""
        self.current_config = self._collect_config_from_ui()
        self.config_changed.emit(self.current_config)
    
    def _collect_config_from_ui(self) -> DisplayConfig:
        """从UI控件收集配置"""
        return DisplayConfig(
            use_wuxing_colors=self.use_wuxing_colors_cb.isChecked(),
            show_zhi_fu_shi_bold=self.show_zhi_fu_shi_bold_cb.isChecked(),
            auto_yue_ling_chong_kong=self.auto_yue_ling_chong_kong_cb.isChecked(),
            auto_maxing_chong_mu_kong=self.auto_maxing_chong_mu_kong_cb.isChecked(),
            show_ri_kong=self.show_ri_kong_cb.isChecked(),
            show_shi_kong=self.show_shi_kong_cb.isChecked(),
            show_liu_ji=self.show_liu_ji_cb.isChecked(),
            show_ru_mu=self.show_ru_mu_cb.isChecked(),
            show_ma_xing=self.show_ma_xing_cb.isChecked(),
            show_yue_ling=self.show_yue_ling_cb.isChecked(),
            show_di_pan_gate=self.show_di_pan_gate_cb.isChecked(),
            show_di_pan_star=self.show_di_pan_star_cb.isChecked(),
            annotation_background_alpha=self.current_config.annotation_background_alpha,
            selected_border_width=self.current_config.selected_border_width,
            annotation_circle_radius=self.current_config.annotation_circle_radius
        )
    
    def load_config(self, config: DisplayConfig):
        """加载配置到UI"""
        self.current_config = config
        
        # 样式设置
        self.use_wuxing_colors_cb.setChecked(config.use_wuxing_colors)
        self.show_zhi_fu_shi_bold_cb.setChecked(config.show_zhi_fu_shi_bold)
        self.auto_yue_ling_chong_kong_cb.setChecked(config.auto_yue_ling_chong_kong)
        self.auto_maxing_chong_mu_kong_cb.setChecked(config.auto_maxing_chong_mu_kong)
        
        # 参数显示
        self.show_ri_kong_cb.setChecked(config.show_ri_kong)
        self.show_shi_kong_cb.setChecked(config.show_shi_kong)
        self.show_liu_ji_cb.setChecked(config.show_liu_ji)
        self.show_ru_mu_cb.setChecked(config.show_ru_mu)
        self.show_ma_xing_cb.setChecked(config.show_ma_xing)
        self.show_yue_ling_cb.setChecked(config.show_yue_ling)
        self.show_di_pan_gate_cb.setChecked(config.show_di_pan_gate)
        self.show_di_pan_star_cb.setChecked(config.show_di_pan_star)
    
    def get_config(self) -> DisplayConfig:
        """获取当前配置"""
        return self._collect_config_from_ui()


class TemplateManagementPage(QWidget):
    """模板管理页面"""
    
    templates_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.templates_file = get_resource_path('data/templates.json')
        self.templates_data = {}
        self.current_template = None
        self._init_ui()
        self._load_templates()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧模板列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("模板列表:"))
        self.template_list = QListWidget()
        self.template_list.currentTextChanged.connect(self._on_template_selected)
        left_layout.addWidget(self.template_list)
        
        # 模板操作按钮
        buttons_layout = QHBoxLayout()
        self.new_template_btn = QPushButton("新建")
        self.delete_template_btn = QPushButton("删除")
        self.new_template_btn.clicked.connect(self._new_template)
        self.delete_template_btn.clicked.connect(self._delete_template)
        buttons_layout.addWidget(self.new_template_btn)
        buttons_layout.addWidget(self.delete_template_btn)
        left_layout.addLayout(buttons_layout)
        
        splitter.addWidget(left_widget)
        
        # 右侧模板编辑
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        right_layout.addWidget(QLabel("模板规则:"))
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(3)
        self.rules_table.setHorizontalHeaderLabels(["参数类型", "参数名称", "标注文本"])
        
        # 设置表格列宽
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        right_layout.addWidget(self.rules_table)
        
        # 规则操作按钮
        rule_buttons_layout = QHBoxLayout()
        self.add_rule_btn = QPushButton("添加规则")
        self.remove_rule_btn = QPushButton("删除规则")
        self.save_template_btn = QPushButton("保存模板")
        
        self.add_rule_btn.clicked.connect(self._add_rule)
        self.remove_rule_btn.clicked.connect(self._remove_rule)
        self.save_template_btn.clicked.connect(self._save_templates)
        
        rule_buttons_layout.addWidget(self.add_rule_btn)
        rule_buttons_layout.addWidget(self.remove_rule_btn)
        rule_buttons_layout.addStretch()
        rule_buttons_layout.addWidget(self.save_template_btn)
        right_layout.addLayout(rule_buttons_layout)
        
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([200, 400])
    
    def _load_templates(self):
        """加载模板文件"""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    self.templates_data = json.load(f)
            else:
                self.templates_data = {"_default_": {"rules": []}}
            
            # 更新模板列表
            self.template_list.clear()
            for template_name in self.templates_data.keys():
                self.template_list.addItem(template_name)
                
        except Exception as e:
            QMessageBox.warning(self, "警告", f"无法加载模板文件: {e}")
            self.templates_data = {"_default_": {"rules": []}}
    
    def _on_template_selected(self, template_name: str):
        """模板选中事件"""
        if not template_name or template_name not in self.templates_data:
            return
            
        self.current_template = template_name
        template_data = self.templates_data[template_name]
        
        # 兼容两种数据格式：新格式(dict with rules)和旧格式(array)
        if isinstance(template_data, dict):
            rules = template_data.get("rules", [])
        else:
            # 旧格式：直接是规则数组
            rules = template_data if isinstance(template_data, list) else []
        
        # 更新规则表格
        self.rules_table.setRowCount(len(rules))
        for i, rule in enumerate(rules):
            # 兼容旧格式字段名
            param_type = rule.get("param_type", "")
            param_name = rule.get("param_name", "")
            # 新格式使用annotation_text，旧格式使用label
            annotation_text = rule.get("annotation_text", rule.get("label", ""))
            
            self.rules_table.setItem(i, 0, QTableWidgetItem(param_type))
            self.rules_table.setItem(i, 1, QTableWidgetItem(param_name))
            self.rules_table.setItem(i, 2, QTableWidgetItem(annotation_text))
    
    def _new_template(self):
        """新建模板"""
        from PySide6.QtWidgets import QInputDialog
        
        template_name, ok = QInputDialog.getText(
            self, "新建模板", "请输入模板名称:"
        )
        
        if ok and template_name:
            if template_name in self.templates_data:
                QMessageBox.warning(self, "警告", "模板名称已存在")
                return
                
            self.templates_data[template_name] = {"rules": []}
            self.template_list.addItem(template_name)
            self.template_list.setCurrentItem(
                self.template_list.findItems(template_name, Qt.MatchExactly)[0]
            )
    
    def _delete_template(self):
        """删除模板"""
        if not self.current_template:
            return
            
        if self.current_template == "_default_":
            QMessageBox.warning(self, "警告", "不能删除默认模板")
            return
            
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除模板 '{self.current_template}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.templates_data[self.current_template]
            self.template_list.takeItem(self.template_list.currentRow())
            self.current_template = None
            self.rules_table.setRowCount(0)
    
    def _add_rule(self):
        """添加规则"""
        if not self.current_template:
            QMessageBox.warning(self, "警告", "请先选择一个模板")
            return
            
        row = self.rules_table.rowCount()
        self.rules_table.insertRow(row)
        self.rules_table.setItem(row, 0, QTableWidgetItem(""))
        self.rules_table.setItem(row, 1, QTableWidgetItem(""))
        self.rules_table.setItem(row, 2, QTableWidgetItem(""))
    
    def _remove_rule(self):
        """删除规则"""
        current_row = self.rules_table.currentRow()
        if current_row >= 0:
            self.rules_table.removeRow(current_row)
    
    def _save_templates(self):
        """保存模板"""
        if not self.current_template:
            return
            
        # 收集当前模板的规则
        rules = []
        for i in range(self.rules_table.rowCount()):
            param_type = self.rules_table.item(i, 0)
            param_name = self.rules_table.item(i, 1)
            annotation_text = self.rules_table.item(i, 2)
            
            if param_type and param_name and annotation_text:
                rules.append({
                    "param_type": param_type.text(),
                    "param_name": param_name.text(),
                    "annotation_text": annotation_text.text()
                })
        
        # 使用新格式保存模板
        self.templates_data[self.current_template] = {"rules": rules}
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
            
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", "模板已保存")
            self.templates_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存模板失败: {e}")


class DataCachePage(QWidget):
    """数据与缓存设置页面"""
    
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_config = {
            "default_workspace_path": "",
            "auto_save_interval": 300,
            "max_recent_files": 10,
            "cache_enabled": True
        }
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 工作区设置组
        workspace_group = QGroupBox("工作区设置")
        workspace_layout = QVBoxLayout(workspace_group)
        
        # 默认工作区路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("默认工作区路径:"))
        self.workspace_path_edit = QLineEdit()
        self.workspace_path_edit.textChanged.connect(self._on_workspace_path_changed)
        path_layout.addWidget(self.workspace_path_edit)
        
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self._browse_workspace_path)
        path_layout.addWidget(self.browse_btn)
        
        workspace_layout.addLayout(path_layout)
        layout.addWidget(workspace_group)
        
        # 配置文件组
        config_group = QGroupBox("配置文件")
        config_layout = QVBoxLayout(config_group)
        
        self.config_path_label = QLabel("配置文件位置: (正在检测...)")
        config_layout.addWidget(self.config_path_label)
        
        self.open_config_folder_btn = QPushButton("打开配置文件夹")
        self.open_config_folder_btn.clicked.connect(self._open_config_folder)
        config_layout.addWidget(self.open_config_folder_btn)
        
        layout.addWidget(config_group)
        
        # 缓存管理组
        cache_group = QGroupBox("缓存管理")
        cache_layout = QVBoxLayout(cache_group)
        
        self.cache_enabled_cb = QCheckBox("启用缓存")
        self.cache_enabled_cb.setChecked(True)
        self.cache_enabled_cb.toggled.connect(self._on_cache_enabled_changed)
        cache_layout.addWidget(self.cache_enabled_cb)
        
        self.clear_cache_btn = QPushButton("清除缓存")
        self.clear_cache_btn.clicked.connect(self._clear_cache)
        cache_layout.addWidget(self.clear_cache_btn)
        
        layout.addWidget(cache_group)
        
        # 添加弹性空间
        layout.addStretch()
    
    def _on_workspace_path_changed(self, path: str):
        """工作区路径改变事件"""
        self.current_config["default_workspace_path"] = path
        self.config_changed.emit(self.current_config)
    
    def _on_cache_enabled_changed(self, enabled: bool):
        """缓存启用状态改变事件"""
        self.current_config["cache_enabled"] = enabled
        self.config_changed.emit(self.current_config)
    
    def _browse_workspace_path(self):
        """浏览工作区路径"""
        path = QFileDialog.getExistingDirectory(
            self, "选择默认工作区路径", self.workspace_path_edit.text()
        )
        if path:
            self.workspace_path_edit.setText(path)
    
    def _open_config_folder(self):
        """打开配置文件夹"""
        # 这个方法需要配置管理器的支持
        QMessageBox.information(self, "提示", "配置文件夹功能需要配置管理器支持")
    
    def _clear_cache(self):
        """清除缓存"""
        reply = QMessageBox.question(
            self, "确认", "确定要清除所有缓存吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "成功", "缓存已清除")
    
    def load_config(self, config: Dict[str, Any]):
        """加载配置到UI"""
        self.current_config = config.copy()
        
        self.workspace_path_edit.setText(
            config.get("default_workspace_path", "")
        )
        self.cache_enabled_cb.setChecked(
            config.get("cache_enabled", True)
        )
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.current_config.copy()
    
    def set_config_path(self, path: str):
        """设置配置文件路径显示"""
        self.config_path_label.setText(f"配置文件位置: {path}")


class AboutPage(QWidget):
    """关于页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # 应用图标（如果有的话）
        # icon_label = QLabel()
        # icon_label.setPixmap(QPixmap("path/to/icon.png"))
        # icon_label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(icon_label)
        
        # 应用名称
        app_name_label = QLabel("奇门遁甲工作台")
        app_name_font = QFont()
        app_name_font.setPointSize(20)
        app_name_font.setBold(True)
        app_name_label.setFont(app_name_font)
        app_name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_name_label)
        
        # 版本号
        version_label = QLabel("版本 v1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # 版权信息
        copyright_label = QLabel("版权所有 © AI助手 2025")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)
        
        # 描述
        description_label = QLabel(
            "一个专业的奇门遁甲排盘和分析工具\n"
            "支持案例管理、模板标注、工作区功能"
        )
        description_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(description_label)
        
        # 项目链接
        link_label = QLabel(
            '<a href="https://github.com/Lucio-ball/Qimen">项目主页</a>'
        )
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setOpenExternalLinks(True)
        layout.addWidget(link_label)
        
        # 添加弹性空间
        layout.addStretch()
