"""
标注管理面板 - 管理当前案例的标注列表，支持模板和图层功能
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
                               QPushButton, QHBoxLayout, QFrame, QSizePolicy,
                               QComboBox, QLineEdit, QColorDialog, QMenu, QLabel,
                               QGroupBox, QCheckBox, QInputDialog, QMessageBox,
                               QSplitter, QTabWidget)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon, QAction
from typing import Dict, List, Optional
from ..dialogs.annotation_dialog import AnnotationDialog
import json
import os


class AnnotationListItem(QListWidgetItem):
    """标注列表项 - 支持多重标注显示"""
    def __init__(self, param_id: str, annotations: List[Dict[str, str]]):
        super().__init__()
        self.param_id = param_id
        self.annotations = annotations
        self._update_display()
        
    def _update_display(self):
        """更新显示内容"""
        if not self.annotations:
            return
            
        # 获取所有标注文本
        texts = [annotation.get('text', '标注') for annotation in self.annotations]
        combined_text = "、".join(texts)
        
        # 使用第一个标注的颜色和形状作为图标
        first_annotation = self.annotations[0]
        color = first_annotation.get('color', '#FF0000')
        shape = first_annotation.get('shape', 'circle')
        
        # 创建颜色图标
        icon = self._create_color_icon(color, shape)
        self.setIcon(icon)
        
        # 设置显示文本（参数ID + 标注文本）
        param_display = self._format_param_id(self.param_id)
        self.setText(f"{param_display}: {combined_text}")
        
        # 如果有多个标注，在tooltip中显示详细信息
        if len(self.annotations) > 1:
            tooltip_lines = [f"{param_display}:"]
            for i, annotation in enumerate(self.annotations, 1):
                tooltip_lines.append(f"  {i}. {annotation.get('text', '')}")
            self.setToolTip("\n".join(tooltip_lines))
        
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
        
    def _format_param_id(self, param_id: str) -> str:
        """格式化参数ID为人类可读形式"""
        # 例如: "palace_7_heaven_stem_0" -> "七宫-天盘干-1"
        parts = param_id.split('_')
        if len(parts) >= 3 and parts[0] == 'palace':
            palace_num = parts[1]
            param_type = parts[2]
            
            # 宫位中文映射
            palace_map = {
                '1': '一宫', '2': '二宫', '3': '三宫', '4': '四宫',
                '5': '五宫', '6': '六宫', '7': '七宫', '8': '八宫', '9': '九宫'
            }
            
            # 参数类型映射
            type_map = {
                'heaven': '天盘干',
                'earth': '地盘干', 
                'star': '九星',
                'gate': '八门',
                'god': '八神',
                'ju': '局数'
            }
            
            palace_name = palace_map.get(palace_num, f"{palace_num}宫")
            
            # 处理复合类型 (如 heaven_stem)
            if len(parts) >= 4 and param_type in ['heaven', 'earth']:
                type_key = param_type
                type_name = type_map.get(type_key, param_type)
                
                if len(parts) >= 5 and parts[4].isdigit():  # 有索引
                    index = int(parts[4]) + 1  # 0-based转1-based
                    return f"{palace_name}-{type_name}-{index}"
                else:
                    return f"{palace_name}-{type_name}"
            else:
                type_name = type_map.get(param_type, param_type)
                return f"{palace_name}-{type_name}"
        
        return param_id  # fallback


class LayerListItem(QListWidgetItem):
    """图层列表项"""
    def __init__(self, layer_index: int, layer_data: Dict):
        super().__init__()
        self.layer_index = layer_index
        self.layer_data = layer_data
        self._update_display()
        
    def _update_display(self):
        """更新显示内容"""
        name = self.layer_data.get("name", f"图层 {self.layer_index}")
        is_visible = self.layer_data.get("is_visible", True)
        annotations_count = len(self.layer_data.get("annotations", {}))
        
        # 设置文本
        self.setText(f"{name} ({annotations_count}标注)")
        
        # 设置复选框状态（通过setCheckState实现可见性控制）
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
        self.setCheckState(Qt.Checked if is_visible else Qt.Unchecked)
        
    def update_layer_data(self, layer_data: Dict):
        """更新图层数据"""
        self.layer_data = layer_data
        self._update_display()


class AnnotationPanelWidget(QWidget):
    """标注管理面板组件 - 支持模板和图层管理"""
    
    # 信号定义
    annotation_selected = Signal(str)  # 选择标注时发射参数ID
    annotation_edited = Signal(str, dict)  # 编辑标注时发射参数ID和新标注数据
    annotation_deleted = Signal(str)  # 删除标注时发射参数ID
    annotations_changed = Signal()  # 标注发生变化时发射，用于刷新图表显示
    template_applied = Signal(str)  # 应用模板时发射模板名称
    layer_changed = Signal()  # 图层变化时发射
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_case = None  # 当前案例对象
        self.templates = {}  # 模板数据
        self._load_templates()
        self._setup_ui()
        self._connect_signals()
        
    def _load_templates(self):
        """加载模板数据"""
        try:
            # 假设templates.json在项目根目录的data文件夹下
            template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                       "data", "templates.json")
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            else:
                self.templates = {}
                print(f"模板文件未找到: {template_path}")
        except Exception as e:
            print(f"加载模板失败: {e}")
            self.templates = {}
        
    def _setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title_label = QLabel("标注管理 v2.0")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        layout.addWidget(title_label)
        
        # 创建选项卡widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 标注管理选项卡
        annotation_tab = QWidget()
        self._setup_annotation_tab(annotation_tab)
        tab_widget.addTab(annotation_tab, "标注管理")
        
        # 模板选项卡
        template_tab = QWidget()
        self._setup_template_tab(template_tab)
        tab_widget.addTab(template_tab, "模板应用")
        
        # 图层管理选项卡
        layer_tab = QWidget()
        self._setup_layer_tab(layer_tab)
        tab_widget.addTab(layer_tab, "图层管理")
        
        # 统计信息
        self.stats_label = QLabel("标注总数: 0")
        self.stats_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.stats_label)
        
    def _setup_annotation_tab(self, parent):
        """设置标注管理选项卡"""
        layout = QVBoxLayout(parent)
        
        # 当前图层显示
        self.current_layer_label = QLabel("当前图层: 默认图层")
        self.current_layer_label.setStyleSheet("font-weight: bold; color: #0066CC;")
        layout.addWidget(self.current_layer_label)
        
        # 标注列表
        list_group = QGroupBox("标注列表")
        list_layout = QVBoxLayout(list_group)
        
        self.annotation_list = QListWidget()
        self.annotation_list.setContextMenuPolicy(Qt.CustomContextMenu)
        list_layout.addWidget(self.annotation_list)
        
        layout.addWidget(list_group)
        
        # 编辑区域
        edit_group = QGroupBox("标注信息（双击列表项编辑）")
        edit_layout = QVBoxLayout(edit_group)
        
        # 标注文本
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("文本:"))
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("输入标注文本...")
        text_layout.addWidget(self.text_edit)
        edit_layout.addLayout(text_layout)
        
        # 形状选择
        shape_layout = QHBoxLayout()
        shape_layout.addWidget(QLabel("形状:"))
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["circle", "square", "triangle"])
        shape_layout.addWidget(self.shape_combo)
        edit_layout.addLayout(shape_layout)
        
        # 颜色选择
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("颜色:"))
        self.color_button = QPushButton()
        self.color_button.setMaximumSize(30, 25)
        self.color_button.setStyleSheet("background-color: #FF0000;")
        self.current_color = "#FF0000"
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        edit_layout.addLayout(color_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("编辑标注")
        self.delete_button = QPushButton("删除标注")
        self.clear_all_button = QPushButton("清空当前图层")
        
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_all_button)
        edit_layout.addLayout(button_layout)
        
        layout.addWidget(edit_group)
        
    def _setup_template_tab(self, parent):
        """设置模板选项卡"""
        layout = QVBoxLayout(parent)
        
        # 模板选择
        template_group = QGroupBox("模板应用")
        template_layout = QVBoxLayout(template_group)
        
        # 模板选择下拉框
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("选择模板:"))
        self.template_combo = QComboBox()
        self.template_combo.addItem("请选择模板...")
        self.template_combo.addItems(list(self.templates.keys()))
        select_layout.addWidget(self.template_combo)
        template_layout.addLayout(select_layout)
        
        # 应用按钮
        self.apply_template_button = QPushButton("应用模板到当前图层")
        self.apply_template_button.setEnabled(False)
        template_layout.addWidget(self.apply_template_button)
        
        # 模板预览
        preview_group = QGroupBox("模板预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.template_preview = QListWidget()
        self.template_preview.setMaximumHeight(150)
        preview_layout.addWidget(self.template_preview)
        
        template_layout.addWidget(preview_group)
        layout.addWidget(template_group)
        
        layout.addStretch()
        
    def _setup_layer_tab(self, parent):
        """设置图层管理选项卡"""
        layout = QVBoxLayout(parent)
        
        # 图层列表
        layer_group = QGroupBox("图层列表")
        layer_layout = QVBoxLayout(layer_group)
        
        self.layer_list = QListWidget()
        self.layer_list.setContextMenuPolicy(Qt.CustomContextMenu)
        layer_layout.addWidget(self.layer_list)
        
        # 图层操作按钮
        layer_button_layout = QHBoxLayout()
        self.add_layer_button = QPushButton("新建图层")
        self.rename_layer_button = QPushButton("重命名")
        self.delete_layer_button = QPushButton("删除图层")
        
        self.rename_layer_button.setEnabled(False)
        self.delete_layer_button.setEnabled(False)
        
        layer_button_layout.addWidget(self.add_layer_button)
        layer_button_layout.addWidget(self.rename_layer_button)
        layer_button_layout.addWidget(self.delete_layer_button)
        layer_layout.addLayout(layer_button_layout)
        
        layout.addWidget(layer_group)
        
        # 图层信息
        info_group = QGroupBox("图层信息")
        info_layout = QVBoxLayout(info_group)
        
        self.layer_info_label = QLabel("选择图层查看详细信息")
        info_layout.addWidget(self.layer_info_label)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        
    def _connect_signals(self):
        """连接信号槽"""
        # 标注管理选项卡信号
        self.annotation_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.annotation_list.customContextMenuRequested.connect(self._show_context_menu)
        self.annotation_list.itemDoubleClicked.connect(self._on_double_click)
        self.color_button.clicked.connect(self._choose_color)
        self.update_button.clicked.connect(self._update_annotation)
        self.delete_button.clicked.connect(self._delete_annotation)
        self.clear_all_button.clicked.connect(self._clear_all_annotations)
        
        # 模板选项卡信号
        self.template_combo.currentTextChanged.connect(self._on_template_selected)
        self.apply_template_button.clicked.connect(self._apply_template)
        
        # 图层选项卡信号
        self.layer_list.itemSelectionChanged.connect(self._on_layer_selection_changed)
        self.layer_list.customContextMenuRequested.connect(self._show_layer_context_menu)
        self.layer_list.itemChanged.connect(self._on_layer_visibility_changed)
        self.add_layer_button.clicked.connect(self._add_layer)
        self.rename_layer_button.clicked.connect(self._rename_layer)
        self.delete_layer_button.clicked.connect(self._delete_layer)
        
    def set_case(self, case):
        """设置当前案例"""
        self.current_case = case
        self._refresh_annotation_list()
        self._refresh_layer_list()
        self._update_current_layer_display()
        
    def _refresh_annotation_list(self):
        """刷新标注列表（显示当前激活图层的标注）"""
        self.annotation_list.clear()
        
        if not self.current_case:
            self._update_stats(0)
            return
            
        # 获取当前激活图层的标注
        active_annotations = self.current_case.get_active_annotations()
        
        # 添加标注项
        total_annotations = 0
        for param_id, annotations_list in active_annotations.items():
            if annotations_list:  # 只显示非空的标注列表
                item = AnnotationListItem(param_id, annotations_list)
                self.annotation_list.addItem(item)
                total_annotations += len(annotations_list)
            
        self._update_stats(total_annotations)
        
    def _refresh_layer_list(self):
        """刷新图层列表"""
        self.layer_list.clear()
        
        if not self.current_case:
            return
            
        for i, layer_data in enumerate(self.current_case.annotation_layers):
            item = LayerListItem(i, layer_data)
            self.layer_list.addItem(item)
            
            # 如果是激活图层，选中它
            if i == self.current_case.active_layer_index:
                self.layer_list.setCurrentItem(item)
                
    def _update_current_layer_display(self):
        """更新当前图层显示"""
        if not self.current_case:
            self.current_layer_label.setText("当前图层: 无")
            return
            
        active_layer = self.current_case.get_active_layer()
        if active_layer:
            layer_name = active_layer.get("name", "未命名图层")
            self.current_layer_label.setText(f"当前图层: {layer_name}")
        else:
            self.current_layer_label.setText("当前图层: 无")
        
    def _update_stats(self, count: int):
        """更新统计信息"""
        self.stats_label.setText(f"标注总数: {count}")
        
    # 模板相关方法
    def _on_template_selected(self, template_name: str):
        """模板选择变化"""
        if template_name == "请选择模板..." or template_name not in self.templates:
            self.apply_template_button.setEnabled(False)
            self.template_preview.clear()
            return
            
        self.apply_template_button.setEnabled(True)
        self._update_template_preview(template_name)
        
    def _update_template_preview(self, template_name: str):
        """更新模板预览"""
        self.template_preview.clear()
        
        if template_name not in self.templates:
            return
            
        template_data = self.templates[template_name]
        for item in template_data:
            param_type = item.get("param_type", "")
            param_value = item.get("param_value", "")
            label = item.get("label", "")
            
            preview_text = f"类型: {param_type}"
            if param_value:
                preview_text += f", 值: {param_value}"
            preview_text += f" -> {label}"
            
            self.template_preview.addItem(preview_text)
            
    def _apply_template(self):
        """应用模板到当前图层"""
        if not self.current_case:
            QMessageBox.warning(self, "警告", "请先选择一个案例")
            return
            
        template_name = self.template_combo.currentText()
        if template_name == "请选择模板..." or template_name not in self.templates:
            QMessageBox.warning(self, "警告", "请选择有效的模板")
            return
            
        # 获取当前激活图层
        active_layer = self.current_case.get_active_layer()
        if not active_layer:
            QMessageBox.warning(self, "警告", "没有激活的图层")
            return
            
        # 应用模板
        applied_count = self._apply_template_to_layer(template_name, active_layer)
        
        if applied_count > 0:
            # 刷新显示
            self._refresh_annotation_list()
            self._refresh_layer_list()
            self.annotations_changed.emit()
            self.template_applied.emit(template_name)
            
            QMessageBox.information(self, "成功", f"成功应用模板 '{template_name}'，添加了 {applied_count} 个标注")
        else:
            QMessageBox.information(self, "提示", f"模板 '{template_name}' 没有找到匹配的参数")
            
    def _apply_template_to_layer(self, template_name: str, layer: Dict) -> int:
        """将模板应用到指定图层，返回添加的标注数量"""
        if template_name not in self.templates:
            return 0
            
        template_data = self.templates[template_name]
        applied_count = 0
        
        for item in template_data:
            param_type = item.get("param_type", "")
            param_value = item.get("param_value")
            label = item.get("label", "标注")
            
            # 根据参数类型查找匹配的参数ID
            matching_param_ids = self._find_matching_params(param_type, param_value)
            
            for param_id in matching_param_ids:
                # 添加标注到图层
                annotations = layer["annotations"]
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
                    
        return applied_count
        
    def _find_matching_params(self, param_type: str, param_value) -> List[str]:
        """根据参数类型和值查找匹配的参数ID"""
        if not self.current_case or not self.current_case.chart_result:
            return []
            
        matching_ids = []
        chart_result = self.current_case.chart_result
        
        # 根据不同的参数类型查找匹配项
        if param_type == "riGan":
            # 日干 - 需要从四柱信息中获取
            ri_gan = chart_result.si_zhu.get("日", "")
            if ri_gan:
                ri_gan_char = ri_gan[0] if len(ri_gan) >= 1 else ""
                # 在所有宫位中查找日干
                for palace in chart_result.palaces:
                    if palace.index == 0 or palace.index == 5:  # 跳过无效宫位
                        continue
                    for i, stem in enumerate(palace.heaven_stems):
                        if stem == ri_gan_char:
                            matching_ids.append(f"palace_{palace.index}_heaven_stem_{i}")
                            
        elif param_type == "zhiFu":
            # 值符 - 查找值符星
            zhi_fu = chart_result.zhi_fu
            for palace in chart_result.palaces:
                if palace.index == 0 or palace.index == 5:  # 跳过无效宫位
                    continue
                for i, star in enumerate(palace.stars):
                    if star == zhi_fu:
                        matching_ids.append(f"palace_{palace.index}_star_{i}")
                        
        elif param_type == "zhiShi":
            # 值使 - 查找值使门
            zhi_shi = chart_result.zhi_shi
            for palace in chart_result.palaces:
                if palace.index == 0 or palace.index == 5:  # 跳过无效宫位
                    continue
                if palace.gates == zhi_shi:
                    matching_ids.append(f"palace_{palace.index}_gate")
                        
        elif param_type == "tianGan":
            # 天干 - 查找指定的天干
            if param_value:
                for palace in chart_result.palaces:
                    if palace.index == 0 or palace.index == 5:  # 跳过无效宫位
                        continue
                    for i, stem in enumerate(palace.heaven_stems):
                        if stem == param_value:
                            matching_ids.append(f"palace_{palace.index}_heaven_stem_{i}")
                            
        elif param_type == "jiuXing":
            # 九星 - 查找指定的九星
            if param_value:
                for palace in chart_result.palaces:
                    if palace.index == 0 or palace.index == 5:  # 跳过无效宫位
                        continue
                    for i, star in enumerate(palace.stars):
                        if star == param_value:
                            matching_ids.append(f"palace_{palace.index}_star_{i}")
                            
        elif param_type == "baMen":
            # 八门 - 查找指定的八门
            if param_value:
                for palace in chart_result.palaces:
                    if palace.index == 0 or palace.index == 5:  # 跳过无效宫位
                        continue
                    if palace.gates == param_value:
                        matching_ids.append(f"palace_{palace.index}_gate")
                        
        elif param_type == "baShen":
            # 八神 - 查找指定的八神
            if param_value:
                for palace in chart_result.palaces:
                    if palace.index == 0 or palace.index == 5:  # 跳过无效宫位
                        continue
                    if palace.god == param_value:
                        matching_ids.append(f"palace_{palace.index}_god")
                        
        return matching_ids
        
    # 图层相关方法
    def _on_layer_selection_changed(self):
        """图层选择变化"""
        current_item = self.layer_list.currentItem()
        has_selection = current_item is not None
        
        self.rename_layer_button.setEnabled(has_selection)
        self.delete_layer_button.setEnabled(has_selection and len(self.current_case.annotation_layers) > 1)
        
        if has_selection and isinstance(current_item, LayerListItem):
            layer_data = current_item.layer_data
            layer_name = layer_data.get("name", "未命名图层")
            is_visible = layer_data.get("is_visible", True)
            annotations_count = len(layer_data.get("annotations", {}))
            
            info_text = f"图层名称: {layer_name}\n"
            info_text += f"可见性: {'可见' if is_visible else '隐藏'}\n"
            info_text += f"标注数量: {annotations_count}"
            
            self.layer_info_label.setText(info_text)
            
            # 切换激活图层
            if self.current_case:
                self.current_case.set_active_layer(current_item.layer_index)
                self._update_current_layer_display()
                self._refresh_annotation_list()
                self.layer_changed.emit()
        else:
            self.layer_info_label.setText("选择图层查看详细信息")
            
    def _on_layer_visibility_changed(self, item):
        """图层可见性变化"""
        if isinstance(item, LayerListItem) and self.current_case:
            is_visible = item.checkState() == Qt.Checked
            self.current_case.set_layer_visibility(item.layer_index, is_visible)
            item.layer_data["is_visible"] = is_visible
            item.update_layer_data(item.layer_data)
            self.layer_changed.emit()
            self.annotations_changed.emit()
            
    def _add_layer(self):
        """添加新图层"""
        if not self.current_case:
            QMessageBox.warning(self, "警告", "请先选择一个案例")
            return
            
        name, ok = QInputDialog.getText(self, "新建图层", "请输入图层名称:", text="新图层")
        if ok and name.strip():
            layer_index = self.current_case.add_layer(name.strip())
            self._refresh_layer_list()
            self._update_current_layer_display()
            self._refresh_annotation_list()
            self.layer_changed.emit()
            
    def _rename_layer(self):
        """重命名图层"""
        current_item = self.layer_list.currentItem()
        if not isinstance(current_item, LayerListItem) or not self.current_case:
            return
            
        old_name = current_item.layer_data.get("name", "")
        name, ok = QInputDialog.getText(self, "重命名图层", "请输入新的图层名称:", text=old_name)
        if ok and name.strip():
            self.current_case.rename_layer(current_item.layer_index, name.strip())
            current_item.layer_data["name"] = name.strip()
            current_item.update_layer_data(current_item.layer_data)
            self._update_current_layer_display()
            self.layer_changed.emit()
            
    def _delete_layer(self):
        """删除图层"""
        current_item = self.layer_list.currentItem()
        if not isinstance(current_item, LayerListItem) or not self.current_case:
            return
            
        if len(self.current_case.annotation_layers) <= 1:
            QMessageBox.warning(self, "警告", "至少需要保留一个图层")
            return
            
        layer_name = current_item.layer_data.get("name", "未命名图层")
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除图层 '{layer_name}' 吗？\n这将删除该图层的所有标注。",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.current_case.remove_layer(current_item.layer_index)
            self._refresh_layer_list()
            self._update_current_layer_display()
            self._refresh_annotation_list()
            self.layer_changed.emit()
            
    def _show_layer_context_menu(self, position):
        """显示图层右键菜单"""
        item = self.layer_list.itemAt(position)
        if not isinstance(item, LayerListItem):
            return
            
        menu = QMenu(self)
        
        rename_action = QAction("重命名", self)
        rename_action.triggered.connect(self._rename_layer)
        menu.addAction(rename_action)
        
        if len(self.current_case.annotation_layers) > 1:
            delete_action = QAction("删除", self)
            delete_action.triggered.connect(self._delete_layer)
            menu.addAction(delete_action)
        
        menu.exec_(self.layer_list.mapToGlobal(position))
        
    def _on_selection_changed(self):
        """列表选择变化"""
        current_item = self.annotation_list.currentItem()
        has_selection = current_item is not None
        
        # 现在使用对话框编辑，编辑按钮用于打开对话框
        self.update_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
        if has_selection:
            # 显示多个标注的摘要信息（仅用于显示）
            annotations = current_item.annotations
            if annotations:
                # 显示第一个标注的信息作为示例
                first_annotation = annotations[0]
                self.text_edit.setText(f"共{len(annotations)}个标注: {first_annotation.get('text', '')}")
                self.text_edit.setEnabled(False)  # 只读
                
                shape = first_annotation.get('shape', 'circle')
                index = self.shape_combo.findText(shape)
                if index >= 0:
                    self.shape_combo.setCurrentIndex(index)
                self.shape_combo.setEnabled(False)  # 只读
                    
                color = first_annotation.get('color', '#FF0000')
                self._set_color(color)
                self.color_button.setEnabled(False)  # 只读
            
            # 发射选择信号
            self.annotation_selected.emit(current_item.param_id)
        else:
            # 清空编辑区域
            self.text_edit.clear()
            self.text_edit.setEnabled(True)
            self.shape_combo.setCurrentIndex(0)
            self.shape_combo.setEnabled(True)
            self.color_button.setEnabled(True)
            self._set_color("#FF0000")
            
    def _choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor(QColor(self.current_color), self)
        if color.isValid():
            self._set_color(color.name())
            
    def _set_color(self, color: str):
        """设置颜色"""
        self.current_color = color
        self.color_button.setStyleSheet(f"background-color: {color};")
        
    def _update_annotation(self):
        """更新当前标注（现在使用对话框）"""
        # 现在使用双击或右键菜单来编辑，这个方法不再使用
        # 直接调用双击编辑
        current_item = self.annotation_list.currentItem()
        if current_item:
            self._on_double_click(current_item)
        
    def _delete_annotation(self):
        """删除当前标注"""
        current_item = self.annotation_list.currentItem()
        if not current_item or not self.current_case:
            return
            
        param_id = current_item.param_id
        active_layer = self.current_case.get_active_layer()
        if not active_layer:
            return
            
        # 获取当前图层的标注
        layer_annotations = active_layer["annotations"]
        current_annotations = layer_annotations.get(param_id, [])
        
        if len(current_annotations) > 1:
            dialog = AnnotationDialog(param_id, param_id, current_annotations, self)
            dialog.setWindowTitle(f"管理参数 {param_id} 的标注")
            
            if dialog.exec():
                # 获取用户编辑后的标注列表
                new_annotations = dialog.get_annotations()
                
                if new_annotations:
                    # 更新标注列表
                    layer_annotations[param_id] = new_annotations
                else:
                    # 如果没有标注了，删除整个参数
                    layer_annotations.pop(param_id, None)
                    
                # 刷新列表
                self._refresh_annotation_list()
                self._refresh_layer_list()
                self._emit_change()
        else:
            # 只有一个标注，直接删除整个参数
            layer_annotations.pop(param_id, None)
            
            # 从列表中删除
            self.annotation_list.takeItem(self.annotation_list.row(current_item))
            
            # 更新统计
            total_annotations = sum(len(annotations) for annotations in layer_annotations.values())
            self._update_stats(total_annotations)
            
            # 刷新图层列表（更新标注计数）
            self._refresh_layer_list()
            
            self._emit_change()
        
        # 发射删除信号
        self.annotation_deleted.emit(param_id)
        
    def _clear_all_annotations(self):
        """清空当前图层的所有标注"""
        if not self.current_case:
            return
            
        active_layer = self.current_case.get_active_layer()
        if not active_layer:
            return
            
        # 获取当前图层的标注ID列表
        param_ids = list(active_layer["annotations"].keys())
        
        # 清空当前图层的标注数据
        active_layer["annotations"].clear()
        
        # 清空列表
        self.annotation_list.clear()
        
        # 更新统计
        self._update_stats(0)
        
        # 刷新图层列表（更新标注计数）
        self._refresh_layer_list()
        
        # 为每个删除的标注发射删除信号
        for param_id in param_ids:
            self.annotation_deleted.emit(param_id)
            
        self._emit_change()
            
    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.annotation_list.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(lambda: self._on_double_click(item))
        menu.addAction(edit_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self._delete_annotation)
        menu.addAction(delete_action)
        
        menu.exec_(self.annotation_list.mapToGlobal(position))
        
    def _on_double_click(self, item):
        """双击列表项编辑标注"""
        if not item or not self.current_case:
            return
            
        param_id = item.param_id
        active_layer = self.current_case.get_active_layer()
        if not active_layer:
            return
            
        current_annotations = active_layer["annotations"].get(param_id, [])
        
        # 打开标注对话框
        dialog = AnnotationDialog(param_id, param_id, current_annotations, self)
        dialog.setWindowTitle(f"编辑参数 {param_id} 的标注")
        
        if dialog.exec():
            # 获取用户编辑后的标注列表
            new_annotations = dialog.get_annotations()
            
            if new_annotations:
                # 更新标注列表
                active_layer["annotations"][param_id] = new_annotations
            else:
                # 如果没有标注了，删除整个参数
                active_layer["annotations"].pop(param_id, None)
                
            # 刷新列表
            self._refresh_annotation_list()
            self._refresh_layer_list()
            self._emit_change()
        
    def _focus_edit_area(self):
        """聚焦到编辑区域"""
        self.text_edit.setFocus()
        self.text_edit.selectAll()
        
    def show_annotation_dialog_for_param(self, param_id: str):
        """为指定参数显示标注对话框（让用户从空白开始输入）"""
        if not self.current_case:
            return
            
        active_layer = self.current_case.get_active_layer()
        if not active_layer:
            return
            
        # 获取当前标注列表（不添加默认项）
        current_annotations = active_layer["annotations"].get(param_id, [])
        
        # 创建对话框
        dialog = AnnotationDialog(param_id, param_id, current_annotations, self)
        
        if dialog.exec():
            # 获取用户编辑后的标注列表
            final_annotations = dialog.get_annotations()
            
            # 更新案例数据
            active_layer["annotations"][param_id] = final_annotations
            
            # 刷新显示
            self.set_case(self.current_case)
            
            # 发出信号通知标注已更改
            self.annotations_changed.emit()
        
    def add_annotation_for_param(self, param_id: str, text: str = "新标注"):
        """为指定参数添加标注（从外部调用）"""
        if not self.current_case:
            return
            
        active_layer = self.current_case.get_active_layer()
        if not active_layer:
            return
            
        # 获取当前标注并添加新的默认标注
        current_annotations = active_layer["annotations"].get(param_id, [])
        new_annotations = current_annotations.copy()
        new_annotations.append({
            'text': text,
            'color': '#FF0000',
            'shape': 'circle'
        })
        
        # 创建对话框，传入包含新标注的列表
        dialog = AnnotationDialog(param_id, param_id, new_annotations, self)
        
        if dialog.exec():
            # 获取用户编辑后的标注列表
            final_annotations = dialog.get_annotations()
            
            # 更新案例数据
            active_layer["annotations"][param_id] = final_annotations
            
            # 刷新列表
            self._refresh_annotation_list()
            self._refresh_layer_list()
            
            # 选择新添加的项
            for i in range(self.annotation_list.count()):
                item = self.annotation_list.item(i)
                if isinstance(item, AnnotationListItem) and item.param_id == param_id:
                    self.annotation_list.setCurrentItem(item)
                    break
                    
            # 发送变更信号
            self._emit_change()
                
    def highlight_annotation(self, param_id: str):
        """高亮显示指定标注"""
        for i in range(self.annotation_list.count()):
            item = self.annotation_list.item(i)
            if isinstance(item, AnnotationListItem) and item.param_id == param_id:
                self.annotation_list.setCurrentItem(item)
                break
                
    def _emit_change(self):
        """发射数据变更信号"""
        # 发射一个通用的数据变更信号，让主窗口刷新图表显示
        # 这里我们模拟发射编辑信号来触发图表刷新
        if hasattr(self, 'current_case') and self.current_case:
            # 触发图表刷新，传入一个空的参数ID
            self.annotation_edited.emit("", {})
