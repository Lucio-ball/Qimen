"""
ParameterWidget - 可高度自定义绘制的奇门参数显示组件

用于显示单个奇门参数及其所有附加状态（颜色、样式、选中、标注等）。
通过重写paintEvent方法实现自定义绘制，不使用子控件。
"""
from PySide6.QtWidgets import (QWidget, QApplication, QVBoxLayout, QHBoxLayout, 
                              QMenu, QLabel)
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QFontMetrics, QAction
from PySide6.QtCore import Qt, QRect, Signal
from typing import Optional, Dict, List
import sys
import os

# 添加项目根目录到路径，以便导入ui.config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from ui.config import DisplayConfig


class ParameterWidget(QWidget):
    """
    可高度自定义绘制的参数显示组件
    
    功能特性：
    - 通过paintEvent自定义绘制所有内容
    - 支持文本、颜色、样式的完全控制
    - 支持鼠标点击选中状态
    - 支持右键菜单进行标注操作
    - 支持标注覆盖绘制功能
    """
    
    # 标注相关信号
    annotation_requested = Signal(str)  # 请求添加标注时发射参数ID
    annotation_remove_requested = Signal(str)  # 请求删除标注时发射参数ID
    
    def __init__(self, parent=None):
        """
        初始化ParameterWidget
        
        Args:
            parent: 父控件
        """
        super().__init__(parent)
        
        # 内部状态
        self._text: str = ""
        self._config: Optional[DisplayConfig] = None
        self._color: QColor = QColor(0, 0, 0)  # 默认黑色
        self._is_bold: bool = False
        self._is_selected: bool = False
        self._style_type: str = "primary"  # 样式类型，primary为主要样式，secondary为次要样式
        
        # 标注相关
        self._param_id: str = ""  # 唯一的参数标识符
        self._annotation: Optional[Dict[str, str]] = None  # 标注数据
        self._annotation_texts: List[str] = []  # 多重标注文本
        self._dual_stars: List[str] = []  # 双星信息
        
        # 设置控件的基本属性 - 调整尺寸以适应更长文本
        self.setMinimumSize(45, 40)
        self.setMaximumSize(80, 60)  # 增加最大宽度以适应"天蓬"、"生门"等完整名称
        self.resize(55, 50)
        
        # 启用右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def set_data(self, text: str, config: DisplayConfig, color: QColor, 
                 is_bold: bool, param_id: str = "", annotation_texts: Optional[List[str]] = None,
                 dual_stars: Optional[List[str]] = None, style_type: str = "primary"):
        """
        设置控件的显示数据和配置
        
        Args:
            text: 要显示的主要文本 (e.g., "庚", "休门")
            config: DisplayConfig 对象，用于控制显示逻辑
            color: QColor 对象，代表参数的五行颜色
            is_bold: 布尔值，决定文本是否加粗
            param_id: 字符串，唯一的参数标识符 (e.g., "palace_7_heaven_stem_0")
            annotation_texts: 标注文本列表 (e.g., ["用神", "丈夫"])
            dual_stars: 双星列表，用于禽芮等情况 (e.g., ["芮", "禽"])
            style_type: 样式类型，'primary'为主要样式（天盘），'secondary'为次要样式（地盘）
        """
        self._text = text
        self._config = config
        self._color = color
        self._is_bold = is_bold
        self._param_id = param_id
        self._annotation_texts = annotation_texts or []
        self._dual_stars = dual_stars or []  # 存储双星信息
        self._style_type = style_type  # 存储样式类型
        
        # 触发重绘
        self.update()
        
    def set_annotation_texts(self, annotation_texts: Optional[List[str]]):
        """
        设置或清除标注文本列表
        
        Args:
            annotation_texts: 标注文本列表，None或空列表表示清除标注
        """
        self._annotation_texts = annotation_texts or []
        self.update()
        
    def get_param_id(self) -> str:
        """获取参数ID"""
        return self._param_id
        
    def get_dual_stars(self) -> Optional[List[str]]:
        """获取双星信息"""
        return self._dual_stars
        
    def has_annotation(self) -> bool:
        """检查是否有标注"""
        return len(self._annotation_texts) > 0
        
    def get_annotation_count(self) -> int:
        """获取标注数量"""
        return len(self._annotation_texts)
        
    def paintEvent(self, event):
        """
        自定义绘制事件处理
        
        绘制逻辑：
        1. 初始化QPainter并启用抗锯齿
        2. 绘制背景/选中边框
        3. 设置字体和颜色
        4. 绘制主文本
        5. 绘制标注（如果有）
        """
        if not self._config:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        try:
            # 1. 绘制背景和选中边框
            self._draw_background_and_border(painter)
            
            # 2. 绘制主文本
            self._draw_main_text(painter)
            
            # 3. 绘制标注（如果有）
            if self._annotation_texts:
                self._draw_annotations(painter)
                
        finally:
            painter.end()
            
    def _draw_background_and_border(self, painter: QPainter):
        """
        绘制背景和选中状态边框
        
        Args:
            painter: QPainter对象
        """
        if self._is_selected:
            # 绘制选中状态的边框
            pen = QPen(QColor(255, 0, 0), self._config.selected_border_width)
            painter.setPen(pen)
            painter.setBrush(QBrush())  # 无填充
            
            # 绘制边框，稍微内缩以避免被裁剪
            border_rect = QRect(
                self._config.selected_border_width // 2,
                self._config.selected_border_width // 2,
                self.width() - self._config.selected_border_width,
                self.height() - self._config.selected_border_width
            )
            painter.drawRect(border_rect)
            
    def _draw_main_text(self, painter: QPainter):
        """
        绘制主要文本
        
        Args:
            painter: QPainter对象
        """
        # 设置字体
        font = painter.font()
        
        # 根据配置决定是否加粗
        if self._is_bold and self._config.show_zhi_fu_shi_bold:
            font.setBold(True)
        else:
            font.setBold(False)
            
        # 根据文本长度和内容调整字体大小
        text_len = len(self._text)
        base_size = 16  # 主要样式的基础字体大小
        
        # 如果是次要样式（地盘），字体大小减小
        if self._style_type == "secondary":
            base_size = 12  # 地盘信息使用较小字体
        
        if text_len == 0:
            font.setPointSize(10)  # 空文本
        elif text_len == 1:
            font.setPointSize(base_size)  # 单字符，如"蓬"、"生"
        elif text_len == 2:
            font.setPointSize(base_size - 2)  # 双字符，如"天蓬"、"生门"、"禽芮"
        elif text_len <= 4:
            font.setPointSize(base_size - 6)  # 3-4字符，如"值符"、"三奇局"
        else:
            font.setPointSize(base_size - 8)   # 更长文本
            
        painter.setFont(font)
        
        # 设置颜色
        if self._config.use_wuxing_colors:
            color = self._color
            # 如果是次要样式（地盘），颜色调为较浅的灰色调
            if self._style_type == "secondary":
                # 将颜色转换为较浅的灰色调
                color = QColor(128, 128, 128)  # 中等灰色
            painter.setPen(QPen(color))
        else:
            # 根据样式类型设置颜色
            if self._style_type == "secondary":
                painter.setPen(QPen(QColor(128, 128, 128)))  # 次要样式使用灰色
            else:
                painter.setPen(QPen(QColor(0, 0, 0)))  # 默认黑色
            
        # 绘制文本（居中）
        text_rect = QRect(0, 0, self.width(), self.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self._text)
        
    def _draw_annotations(self, painter: QPainter):
        """
        绘制多重标注 - 支持双星分离显示
        
        Args:
            painter: QPainter对象
        """
        if not self._annotation_texts:
            return
            
        # 检查是否为双星
        if self._dual_stars and len(self._dual_stars) == 2:
            self._draw_dual_star_annotations(painter)
        else:
            self._draw_single_star_annotations(painter)
    
    def _draw_single_star_annotations(self, painter: QPainter):
        """绘制单星标注（原逻辑）"""
        # 计算圆圈位置（控件中央）
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = 18
        
        # 绘制空心圆圈（不填充）
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # 合并标注文本
        combined_text = "、".join(self._annotation_texts)
        
        # 设置标注文字的字体和颜色
        annotation_font = QFont()
        annotation_font.setPointSize(7)
        annotation_font.setBold(True)
        painter.setFont(annotation_font)
        painter.setPen(QPen(QColor(255, 0, 0)))
        
        # 计算文字位置（在控件顶部）
        text_rect = QRect(0, 0, self.width(), 12)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, combined_text)
    
    def _draw_dual_star_annotations(self, painter: QPainter):
        """绘制双星分离标注"""
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = 10   # 圆圈大小
        
        # 获取字体信息来计算字符位置
        font_metrics = painter.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self._text)
        char_width = text_width // len(self._text) if self._text else 0
        
        # 计算两个字符的中心位置
        first_char_x = center_x - text_width // 2 + char_width // 2  # 第一个字符"芮"的中心
        second_char_x = center_x + text_width // 2 - char_width // 2  # 第二个字符"芮"的中心
        
        # 分离双星的标注
        star1_annotations = []
        star2_annotations = []
        
        for annotation in self._annotation_texts:
            if annotation.startswith(f"{self._dual_stars[0]}:"):
                # 移除前缀，只保留标注内容
                star1_annotations.append(annotation[len(f"{self._dual_stars[0]}:"):])
            elif annotation.startswith(f"{self._dual_stars[1]}:"):
                # 移除前缀，只保留标注内容
                star2_annotations.append(annotation[len(f"{self._dual_stars[1]}:"):])
        
        # 绘制第一个星的标注（禽字位置）- 但显示在下方
        if star1_annotations:
            # 对于禽芮组合，禽星标注显示在下方
            position = "bottom" if self._dual_stars == ["禽", "芮"] else "top"
            self._draw_star_circle_and_text(painter, first_char_x, center_y, radius, 
                                          star1_annotations, self._dual_stars[0], position)
        
        # 绘制第二个星的标注（芮字位置）- 但显示在上方
        if star2_annotations:
            # 对于禽芮组合，芮星标注显示在上方
            position = "top" if self._dual_stars == ["禽", "芮"] else "bottom"
            self._draw_star_circle_and_text(painter, second_char_x, center_y, radius, 
                                          star2_annotations, self._dual_stars[1], position)
    
    def _draw_star_circle_and_text(self, painter: QPainter, x: int, y: int, radius: int, 
                                   annotations: List[str], star_name: str, position: str):
        """绘制单个星的圆圈和标注文本"""
        # 绘制圆圈
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)
        
        # 设置字体
        annotation_font = QFont()
        annotation_font.setPointSize(6)  # 适中的字体大小
        annotation_font.setBold(True)
        painter.setFont(annotation_font)
        painter.setPen(QPen(QColor(255, 0, 0)))
        
        # 合并标注文本，不添加星名前缀
        combined_text = "、".join(annotations)
        
        # 根据星字位置和标注位置需求，调整文字显示区域
        if position == "top":
            # 芮星标注显示在芮字附近的上方
            # 芮字在右侧，标注也在右侧上方
            text_x = x - 20  # 从星字中心往左偏移
            text_y = y - radius - 15  # 圆圈上方
            text_rect = QRect(text_x, text_y, 40, 12)
        else:  # bottom
            # 禽星标注显示在禽字附近的下方  
            # 禽字在左侧，标注也在左侧下方
            text_x = x - 20  # 从星字中心往左偏移
            text_y = y + radius + 3   # 圆圈下方
            text_rect = QRect(text_x, text_y, 40, 12)
        
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, combined_text)
    
    def mousePressEvent(self, event):
        """
        处理鼠标点击事件
        
        Args:
            event: 鼠标事件
        """
        # 移除左键选中功能，只保留右键菜单
        super().mousePressEvent(event)
        
    def _show_context_menu(self, position):
        """
        显示右键上下文菜单
        
        Args:
            position: 菜单显示位置
        """
        if not self._param_id:  # 没有参数ID则不显示菜单
            return
            
        menu = QMenu(self)
        
        # 设置菜单样式，确保文字在hover时可见
        menu.setStyleSheet("""
            QMenu {
                background-color: #f0f0f0;
                border: 1px solid #999;
                border-radius: 3px;
                padding: 2px;
            }
            QMenu::item {
                background-color: transparent;
                color: #000000;
                padding: 5px 20px;
                margin: 1px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #4285f4;
                color: #ffffff;
            }
            QMenu::item:disabled {
                color: #666666;
                background-color: transparent;
            }
            QMenu::separator {
                height: 1px;
                background-color: #cccccc;
                margin: 2px 0px;
            }
        """)
        
        # 检查是否为双星情况
        if self._dual_stars and len(self._dual_stars) == 2:
            # 双星情况：只提供分别标注选项
            star1_action = QAction(f"标注 {self._dual_stars[0]}", self)
            star1_id = f"{self._param_id}_{self._dual_stars[0]}"
            star1_action.triggered.connect(lambda: self.annotation_requested.emit(star1_id))
            menu.addAction(star1_action)
            
            star2_action = QAction(f"标注 {self._dual_stars[1]}", self)
            star2_id = f"{self._param_id}_{self._dual_stars[1]}"
            star2_action.triggered.connect(lambda: self.annotation_requested.emit(star2_id))
            menu.addAction(star2_action)
        else:
            # 单星情况：保留原有的添加新标注选项
            add_action = QAction("添加新标注", self)
            add_action.triggered.connect(lambda: self.annotation_requested.emit(self._param_id))
            menu.addAction(add_action)
        
        if self._annotation_texts:
            menu.addSeparator()
            
            # 显示当前标注信息
            annotations_text = "、".join(self._annotation_texts)
            info_action = QAction(f"当前标注: {annotations_text}", self)
            info_action.setEnabled(False)
            menu.addAction(info_action)
            
        # 添加分隔线和参数信息
        menu.addSeparator()
        param_info_action = QAction(f"参数: {self._text}", self)
        param_info_action.setEnabled(False)
        menu.addAction(param_info_action)
        
        # 显示菜单
        menu.exec_(self.mapToGlobal(position))


def main():
    """
    测试脚本：验证ParameterWidget的各种显示功能
    """
    app = QApplication(sys.argv)
    
    # 创建主窗口
    from PySide6.QtWidgets import QMainWindow, QWidget
    
    main_window = QMainWindow()
    main_window.setWindowTitle("ParameterWidget 测试")
    main_window.resize(400, 300)
    
    # 创建中央控件和布局
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # 创建显示配置
    config = DisplayConfig(
        use_wuxing_colors=True,
        show_zhi_fu_shi_bold=True,
        annotation_background_alpha=150,
        selected_border_width=3,
        annotation_circle_radius=10
    )
    
    # 测试场景1：正常显示
    row1 = QHBoxLayout()
    
    widget1 = ParameterWidget()
    widget1.set_data("庚", config, QColor(255, 215, 0), False, "palace_1_heaven_stem_0")  # 金黄色（金）
    
    widget2 = ParameterWidget()
    widget2.set_data("乙", config, QColor(0, 180, 0), False, "palace_2_heaven_stem_0")  # 深绿色（木）
    
    widget3 = ParameterWidget()
    widget3.set_data("丙", config, QColor(255, 0, 0), True, "palace_3_heaven_stem_0")  # 红色（火），加粗
    
    row1.addWidget(widget1)
    row1.addWidget(widget2)
    row1.addWidget(widget3)
    layout.addLayout(row1)
    
    # 测试场景2：关闭五行颜色
    config_no_color = DisplayConfig(use_wuxing_colors=False)
    
    row2 = QHBoxLayout()
    
    widget4 = ParameterWidget()
    widget4.set_data("壬", config_no_color, QColor(0, 0, 255), False, "palace_4_heaven_stem_0")  # 应显示为黑色
    
    widget5 = ParameterWidget()
    widget5.set_data("戊", config_no_color, QColor(139, 69, 19), True, "palace_5_heaven_stem_0")  # 应显示为黑色加粗
    
    row2.addWidget(widget4)
    row2.addWidget(widget5)
    layout.addLayout(row2)
    
    # 测试场景3：带标注显示
    row3 = QHBoxLayout()
    
    widget6 = ParameterWidget()
    annotation1 = {"text": "旺", "shape": "circle", "color": "#00FF00"}
    widget6.set_data("休门", config, QColor(0, 180, 0), False, "palace_6_gate", annotation1)
    
    widget7 = ParameterWidget()
    annotation2 = {"text": "空", "shape": "square", "color": "#FF0000"}
    widget7.set_data("死门", config, QColor(139, 69, 19), True, "palace_7_gate", annotation2)
    
    row3.addWidget(widget6)
    row3.addWidget(widget7)
    layout.addLayout(row3)
    
    # 连接信号以测试右键菜单功能
    def on_annotation_requested(param_id):
        print(f"请求为 {param_id} 添加标注")
        
    def on_annotation_remove_requested(param_id):
        print(f"请求删除 {param_id} 的标注")
        
    # 连接所有测试控件的信号
    for widget in [widget1, widget2, widget3, widget4, widget5, widget6, widget7]:
        widget.annotation_requested.connect(on_annotation_requested)
        widget.annotation_remove_requested.connect(on_annotation_remove_requested)
    
    # 显示说明
    from PySide6.QtWidgets import QLabel
    info_label = QLabel("点击任意控件可切换选中状态（红色边框）")
    info_label.setStyleSheet("color: blue; font-size: 12px; margin: 10px;")
    layout.addWidget(info_label)
    
    main_window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
