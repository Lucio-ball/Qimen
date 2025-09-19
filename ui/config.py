"""
UI配置相关的数据类定义
"""
from dataclasses import dataclass, field
from typing import Optional
from PySide6.QtGui import QColor


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
    show_di_pan_gate: bool = True  # 显示地盘门
    show_di_pan_star: bool = True  # 显示地盘星
    
    # 参数状态角标配置（新增）
    show_parameter_states: bool = True  # 参数状态角标总开关
    show_tiangan_changsheng: bool = True  # 显示天干长生状态
    show_bamen_wangxiang: bool = True     # 显示八门旺相状态
    show_jiuxing_wangxiang: bool = True   # 显示九星旺相状态
    show_bashen_wangxiang: bool = True    # 显示八神旺相状态
    
    # 五行颜色自定义配置（新增）
    wuxing_colors: dict[str, str] = field(default_factory=lambda: {
        "金": "#f5aa11",  # 金黄色
        "木": "#39a75a",  # 绿色
        "水": "#437ee4",  # 蓝色
        "火": "#e64a35",  # 红色
        "土": "#c77f37"   # 土黄色
    })
    
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
            
    def get_wuxing_color(self, param_type: str, param_name: str) -> QColor:
        """获取五行颜色"""
        if not self.use_wuxing_colors:
            return QColor(0, 0, 0)  # 黑色
            
        # 使用自定义的五行颜色配置
        default_colors = {
            "木": QColor(self.wuxing_colors["木"]),
            "火": QColor(self.wuxing_colors["火"]),
            "土": QColor(self.wuxing_colors["土"]),
            "金": QColor(self.wuxing_colors["金"]),
            "水": QColor(self.wuxing_colors["水"]),
        }
        
        # 简化的映射逻辑（在实际应用中应该查询data/core_parameters.json）
        color_map = {
            # 天干
            "甲": "木", "乙": "木",
            "丙": "火", "丁": "火", 
            "戊": "土", "己": "土",
            "庚": "金", "辛": "金",
            "壬": "水", "癸": "水",
            # 八神
            "值符": "土", "腾蛇": "火", "太阴": "金", "六合": "木",
            "白虎": "金", "玄武": "水", "九地": "土", "九天": "火",
            # 九星
            "天蓬": "水", "天芮": "土", "天冲": "木", "天辅": "木",
            "天禽": "土", "天心": "金", "天柱": "金", "天任": "土", "天英": "火",
            # 八门
            "休门": "水", "死门": "土", "伤门": "木", "杜门": "木",
            "开门": "金", "惊门": "金", "生门": "土", "景门": "火"
        }
        
        wuxing = color_map.get(param_name, "土")  # 默认土
        return default_colors.get(wuxing, QColor(0, 0, 0))
    
    def get_parameter_state_color(self, state: str) -> QColor:
        """获取参数状态对应的角标颜色（浅色）"""
        state_colors = {
            # 天干长生状态
            "长生": QColor(46, 125, 50, 100),    # 浅绿色
            "沐浴": QColor(33, 150, 243, 100),   # 浅蓝色
            "冠带": QColor(156, 39, 176, 100),   # 浅紫色
            "临官": QColor(255, 152, 0, 100),    # 浅橙色
            "帝旺": QColor(244, 67, 54, 100),    # 浅红色
            "衰": QColor(121, 85, 72, 100),      # 浅棕色
            "病": QColor(158, 158, 158, 100),    # 浅灰色
            "死": QColor(96, 125, 139, 100),     # 浅蓝灰色
            "墓": QColor(55, 71, 79, 100),       # 浅深灰色
            "绝": QColor(0, 0, 0, 100),          # 浅黑色
            "胎": QColor(255, 193, 7, 100),      # 浅黄色
            "养": QColor(76, 175, 80, 100),      # 浅绿色
            # 八门、九星、八神旺相状态
            "旺": QColor(244, 67, 54, 120),      # 红色（较深）
            "相": QColor(255, 152, 0, 120),      # 橙色（较深）
            "休": QColor(96, 125, 139, 100),     # 蓝灰色
            "囚": QColor(121, 85, 72, 100),      # 棕色
            "死": QColor(158, 158, 158, 100),    # 灰色
        }
        return state_colors.get(state, QColor(128, 128, 128, 80))  # 默认浅灰色
