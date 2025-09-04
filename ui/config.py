"""
UI配置相关的数据类定义
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DisplayConfig:
    """
    显示配置类，用于控制UI组件的显示逻辑
    """
    # 样式设置
    use_wuxing_colors: bool = True  # 是否使用五行颜色
    show_zhi_fu_shi_bold: bool = True  # 是否对值符使显示加粗
    auto_yue_ling_chong_kong: bool = True  # 月令自动填空
    auto_maxing_chong_mu_kong: bool = True  # 马星自动冲墓、冲空
    
    # 参数显示控制
    show_ri_kong: bool = True  # 显示日空
    show_shi_kong: bool = True  # 显示时空
    show_liu_ji: bool = True  # 显示六仪击刑
    show_ru_mu: bool = True  # 显示入墓
    show_ma_xing: bool = True  # 显示马星
    show_yue_ling: bool = True  # 显示月令
    
    # 原有的数值配置
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
