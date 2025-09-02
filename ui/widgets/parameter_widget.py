"""
ParameterWidget - 可高度自定义绘制的奇门参数显示组件

用于显示单个奇门参数及其所有附加状态（颜色、样式、选中、标注等）。
通过重写paintEvent方法实现自定义绘制，不使用子控件。
"""
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QFontMetrics
from PySide6.QtCore import Qt, QRect
from typing import Optional
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
    - 预留标注覆盖绘制功能
    """
    
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
        self._annotation_text: Optional[str] = None
        self._is_selected: bool = False
        
        # 设置控件的基本属性 - 调整尺寸以适应更长文本
        self.setMinimumSize(45, 40)
        self.setMaximumSize(80, 60)  # 增加最大宽度以适应"天蓬"、"生门"等完整名称
        self.resize(55, 50)
        
    def set_data(self, text: str, config: DisplayConfig, color: QColor, 
                 is_bold: bool, annotation_text: Optional[str] = None):
        """
        设置控件的显示数据和配置
        
        Args:
            text: 要显示的主要文本 (e.g., "庚", "休门")
            config: DisplayConfig 对象，用于控制显示逻辑
            color: QColor 对象，代表参数的五行颜色
            is_bold: 布尔值，决定文本是否加粗
            annotation_text: 字符串，代表要覆盖显示的标注小字。默认为None
        """
        self._text = text
        self._config = config
        self._color = color
        self._is_bold = is_bold
        self._annotation_text = annotation_text
        
        # 触发重绘
        self.update()
        
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
            if self._annotation_text:
                self._draw_annotation(painter)
                
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
        if text_len == 0:
            font.setPointSize(10)  # 空文本
        elif text_len == 1:
            font.setPointSize(16)  # 单字符，如"蓬"、"生"
        elif text_len == 2:
            font.setPointSize(14)  # 双字符，如"天蓬"、"生门"、"禽芮"
        elif text_len <= 4:
            font.setPointSize(10)  # 3-4字符，如"值符"、"三奇局"
        else:
            font.setPointSize(8)   # 更长文本
            
        painter.setFont(font)
        
        # 设置颜色
        if self._config.use_wuxing_colors:
            painter.setPen(QPen(self._color))
        else:
            painter.setPen(QPen(QColor(0, 0, 0)))  # 默认黑色
            
        # 绘制文本（居中）
        text_rect = QRect(0, 0, self.width(), self.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self._text)
        
    def _draw_annotation(self, painter: QPainter):
        """
        绘制覆盖式标注
        
        Args:
            painter: QPainter对象
        """
        if not self._annotation_text:
            return
            
        # 计算圆圈位置（控件中央偏上）
        center_x = self.width() // 2
        center_y = self.height() // 2 - 5
        radius = self._config.annotation_circle_radius
        
        # 绘制半透明背景圆圈
        circle_color = QColor(255, 255, 0, self._config.annotation_background_alpha)  # 半透明黄色
        painter.setBrush(QBrush(circle_color))
        painter.setPen(QPen(QColor(255, 0, 0), 1))  # 红色边框
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # 设置标注文字的字体和颜色
        annotation_font = QFont()
        annotation_font.setPointSize(8)
        annotation_font.setBold(True)
        painter.setFont(annotation_font)
        painter.setPen(QPen(QColor(255, 0, 0)))  # 红色文字
        
        # 绘制标注文字（在圆圈中央）
        annotation_rect = QRect(
            center_x - radius, 
            center_y - radius, 
            radius * 2, 
            radius * 2
        )
        painter.drawText(annotation_rect, Qt.AlignmentFlag.AlignCenter, self._annotation_text)
        
    def mousePressEvent(self, event):
        """
        处理鼠标点击事件，切换选中状态
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_selected = not self._is_selected
            self.update()  # 触发重绘以显示/隐藏选中边框
            
        super().mousePressEvent(event)


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
    widget1.set_data("庚", config, QColor(255, 215, 0), False)  # 金黄色（金）
    
    widget2 = ParameterWidget()
    widget2.set_data("乙", config, QColor(0, 180, 0), False)  # 深绿色（木）
    
    widget3 = ParameterWidget()
    widget3.set_data("丙", config, QColor(255, 0, 0), True)  # 红色（火），加粗
    
    row1.addWidget(widget1)
    row1.addWidget(widget2)
    row1.addWidget(widget3)
    layout.addLayout(row1)
    
    # 测试场景2：关闭五行颜色
    config_no_color = DisplayConfig(use_wuxing_colors=False)
    
    row2 = QHBoxLayout()
    
    widget4 = ParameterWidget()
    widget4.set_data("壬", config_no_color, QColor(0, 0, 255), False)  # 应显示为黑色
    
    widget5 = ParameterWidget()
    widget5.set_data("戊", config_no_color, QColor(139, 69, 19), True)  # 应显示为黑色加粗
    
    row2.addWidget(widget4)
    row2.addWidget(widget5)
    layout.addLayout(row2)
    
    # 测试场景3：带标注显示
    row3 = QHBoxLayout()
    
    widget6 = ParameterWidget()
    widget6.set_data("休门", config, QColor(0, 180, 0), False, "旺")
    
    widget7 = ParameterWidget()
    widget7.set_data("死门", config, QColor(139, 69, 19), True, "空")
    
    row3.addWidget(widget6)
    row3.addWidget(widget7)
    layout.addLayout(row3)
    
    # 显示说明
    from PySide6.QtWidgets import QLabel
    info_label = QLabel("点击任意控件可切换选中状态（红色边框）")
    info_label.setStyleSheet("color: blue; font-size: 12px; margin: 10px;")
    layout.addWidget(info_label)
    
    main_window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
