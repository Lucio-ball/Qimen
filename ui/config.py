"""
UI配置相关的数据类定义
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DisplayConfig:
    """
    显示配置类，用于控制ParameterWidget的显示逻辑
    """
    use_wuxing_colors: bool = True  # 是否使用五行颜色
    show_zhi_fu_shi_bold: bool = True  # 是否对值符使显示加粗
    annotation_background_alpha: int = 128  # 标注背景透明度 (0-255)
    selected_border_width: int = 2  # 选中边框宽度
    annotation_circle_radius: int = 8  # 标注圆圈半径
    
    def __post_init__(self):
        """验证配置参数的有效性"""
        if not 0 <= self.annotation_background_alpha <= 255:
            raise ValueError("annotation_background_alpha must be between 0 and 255")
        if self.selected_border_width < 0:
            raise ValueError("selected_border_width must be non-negative")
        if self.annotation_circle_radius < 0:
            raise ValueError("annotation_circle_radius must be non-negative")
