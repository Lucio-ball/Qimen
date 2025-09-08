"""
PalaceWidget - 奇门遁甲单宫显示组件

基于ParameterWidget构建的复合组件，用于显示完整的单个宫位信息。
内部管理9个ParameterWidget的布局和数据分发。
"""
import sys
import os
from typing import Dict, List, Optional
from PySide6.QtWidgets import QWidget, QGridLayout, QApplication, QMainWindow, QVBoxLayout, QLabel
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ui.widgets.parameter_widget import ParameterWidget
from ui.config import DisplayConfig
from core.models import Palace, ChartResult


class PalaceWidget(QWidget):
    """
    奇门遁甲单宫显示组件
    
    功能特性：
    - 内部管理9个ParameterWidget的3x3布局
    - 根据Palace数据自动分发信息到对应位置
    - 支持中宫特殊显示逻辑
    - 处理值符、值使的加粗显示
    - 查询五行颜色并应用到各个参数
    """
    
    def __init__(self, global_data: dict, parent=None):
        """
        初始化PalaceWidget
        
        Args:
            global_data: 从data/core_parameters.json加载的全局数据字典
            parent: 父控件
        """
        super().__init__(parent)
        
        self.global_data = global_data
        
        # 创建3x3网格布局
        self.layout = QGridLayout(self)
        self.layout.setSpacing(2)  # 设置间距
        
        # 创建9个ParameterWidget实例
        # 按照九宫格位置编号：1(左上) 2(上) 3(右上) 4(左) 5(中) 6(右) 7(左下) 8(下) 9(右下)
        self.param_widgets: Dict[int, ParameterWidget] = {}
        
        # 按网格位置创建并放置控件
        positions = {
            1: (0, 0),  # 左上
            2: (0, 1),  # 上
            3: (0, 2),  # 右上
            4: (1, 0),  # 左
            5: (1, 1),  # 中
            6: (1, 2),  # 右
            7: (2, 0),  # 左下
            8: (2, 1),  # 下
            9: (2, 2),  # 右下
        }
        
        for pos_id, (row, col) in positions.items():
            widget = ParameterWidget()
            widget.setMinimumSize(55, 50)  # 增加最小宽度以适应完整名称
            self.param_widgets[pos_id] = widget
            self.layout.addWidget(widget, row, col)
            
        # 五行颜色映射
        self.wuxing_colors = {
            "木": QColor(0, 180, 0),      # 深绿色
            "火": QColor(255, 0, 0),      # 红色  
            "土": QColor(139, 69, 19),    # 棕色 (SaddleBrown)
            "金": QColor(255, 215, 0),    # 金黄色 (Gold)
            "水": QColor(0, 0, 255),      # 蓝色
        }
        
    def update_data(self, palace_data: Palace, chart_data: ChartResult, 
                    config: DisplayConfig, global_data: dict):
        """
        更新宫位显示数据 - 升级版本，支持天地盘完整信息显示
        
        Args:
            palace_data: 包含此宫位所有基础信息的Palace对象
            chart_data: 包含全局信息（如值符、值使、局数）的ChartResult对象
            config: DisplayConfig对象，用于控制显示逻辑
            global_data: 从data/core_parameters.json加载的全局数据字典，用于查询五行等基础信息
        """
        # 1. 清空所有控件
        self._clear_all_widgets(config)
        
        # 2. 判断是否为中宫
        if palace_data.index == 5:
            self._update_center_palace(palace_data, chart_data, config, global_data)
        else:
            self._update_normal_palace(palace_data, chart_data, config, global_data)
            
    def _clear_all_widgets(self, config: DisplayConfig):
        """
        清空所有ParameterWidget的数据
        
        Args:
            config: DisplayConfig对象
        """
        for widget in self.param_widgets.values():
            widget.set_data("", config, QColor(0, 0, 0), False, "", None, None, "primary")
            
    def _update_center_palace(self, palace_data: Palace, chart_data: ChartResult,
                             config: DisplayConfig, global_data: dict):
        """
        更新中宫显示 - 升级版本
        
        Args:
            palace_data: 中宫Palace对象
            chart_data: ChartResult对象
            config: DisplayConfig对象
            global_data: 全局数据字典
        """
        # 存储全局数据供其他方法使用
        self.global_data = global_data
        
        # 中宫的格子应该无法选中，所以不设置参数ID或设置为空
        for i in range(1, 10):
            if i == 5:
                # 格子5：显示局数信息（中宫特有，不可操作）
                ju_shu_text = f"{chart_data.ju_shu_info.get('遁', '')}{chart_data.ju_shu_info.get('局', '')}局"
                tu_color = self.wuxing_colors["土"]  # 土行颜色
                # 不设置参数ID，使其无法右键操作
                self.param_widgets[5].set_data(ju_shu_text, config, tu_color, False, "", None, None, "primary")
            elif i == 9:
                # 格子9：显示中宫地盘干（中宫特有，不可操作）
                if palace_data.di_pan_stems:
                    earth_stem = palace_data.di_pan_stems[0]
                    color = self._get_wuxing_color("tianGan", earth_stem)
                    # 不设置参数ID，使其无法右键操作
                    self.param_widgets[9].set_data(earth_stem, config, color, False, "", None, None, "primary")
                else:
                    # 没有地盘干时，设置空的不可操作格子
                    self.param_widgets[9].set_data("", config, QColor(0, 0, 0), False, "", None, None, "primary")
            else:
                # 其他格子设置为空的且不可操作
                self.param_widgets[i].set_data("", config, QColor(0, 0, 0), False, "", None, None, "primary")
            
    def _update_normal_palace(self, palace_data: Palace, chart_data: ChartResult,
                             config: DisplayConfig, global_data: dict):
        """
        更新普通宫位显示 - 升级版本，支持完整天地盘信息展示
        
        新布局：
        格子1 (左上角): 地盘门
        格子2 (上中): 八神
        格子3 (右上角): 地盘星
        格子4 (左中): 天禽/中寄天盘干
        格子5 (正中): 天盘星
        格子6 (右中): 天盘干
        格子7 (左下): 中寄地盘干
        格子8 (下中): 天盘门
        格子9 (右下): 地盘干
        
        Args:
            palace_data: Palace对象
            chart_data: ChartResult对象
            config: DisplayConfig对象
            global_data: 全局数据字典
        """
        # 存储全局数据供其他方法使用
        self.global_data = global_data
        
        # 格子1：地盘门（左上角）- 次要样式
        if palace_data.di_pan_gate and config.show_di_pan_gate:
            color = self._get_wuxing_color("baMen", palace_data.di_pan_gate)
            display_text = self._get_full_name("baMen", palace_data.di_pan_gate)
            param_id = f"palace_{palace_data.index}_di_pan_gate"
            self.param_widgets[1].set_data(display_text, config, color, False, param_id, None, None, "secondary")
        
        # 格子2：八神（上中）- 主要样式
        if palace_data.zhi_fu:
            color = self._get_wuxing_color("baShen", palace_data.zhi_fu)
            display_text = self._get_full_name("baShen", palace_data.zhi_fu)
            param_id = f"palace_{palace_data.index}_zhi_fu"
            self.param_widgets[2].set_data(display_text, config, color, False, param_id, None, None, "primary")
        
        # 格子3：地盘星（右上角）- 次要样式
        if palace_data.di_pan_star and config.show_di_pan_star:
            color = self._get_wuxing_color("jiuXing", palace_data.di_pan_star)
            display_text = self._get_full_name("jiuXing", palace_data.di_pan_star)
            param_id = f"palace_{palace_data.index}_di_pan_star"
            self.param_widgets[3].set_data(display_text, config, color, False, param_id, None, None, "secondary")
        
        # 格子4：天禽/中寄天盘干（左中）- 主要样式
        if len(palace_data.tian_pan_stems) > 1:
            stem = palace_data.tian_pan_stems[1]  # 第二个天盘干
            color = self._get_wuxing_color("tianGan", stem)
            param_id = f"palace_{palace_data.index}_tian_pan_stem_1"
            self.param_widgets[4].set_data(stem, config, color, False, param_id, None, None, "primary")
        
        # 格子5：天盘星（正中）- 主要样式
        if palace_data.tian_pan_stars:
            # 处理双星情况（如禽芮）
            if len(palace_data.tian_pan_stars) == 2:
                star_text = self._format_stars(palace_data.tian_pan_stars)
                if "禽" in palace_data.tian_pan_stars and "芮" in palace_data.tian_pan_stars:
                    dual_stars = ["禽", "芮"]
                else:
                    dual_stars = palace_data.tian_pan_stars
            else:
                star_text = self._get_full_name("jiuXing", palace_data.tian_pan_stars[0])
                dual_stars = None
            
            color = self._get_wuxing_color("jiuXing", palace_data.tian_pan_stars[0])
            is_bold = chart_data.zhi_fu in palace_data.tian_pan_stars  # 检查是否包含值符星
            param_id = f"palace_{palace_data.index}_tian_pan_star_0"
            self.param_widgets[5].set_data(star_text, config, color, is_bold, param_id, None, dual_stars, "primary")
        
        # 格子6：天盘干（右中）- 主要样式
        if palace_data.tian_pan_stems:
            stem = palace_data.tian_pan_stems[0]  # 主要天盘干
            color = self._get_wuxing_color("tianGan", stem)
            param_id = f"palace_{palace_data.index}_tian_pan_stem_0"
            self.param_widgets[6].set_data(stem, config, color, False, param_id, None, None, "primary")
        
        # 格子7：中寄地盘干（左下）- 主要样式
        if len(palace_data.di_pan_stems) > 1:
            stem = palace_data.di_pan_stems[1]  # 第二个地盘干
            color = self._get_wuxing_color("tianGan", stem)
            param_id = f"palace_{palace_data.index}_di_pan_stem_1"
            self.param_widgets[7].set_data(stem, config, color, False, param_id, None, None, "primary")
        
        # 格子8：天盘门（下中）- 主要样式
        if palace_data.tian_pan_gates:
            gate = palace_data.tian_pan_gates[0]  # 主要天盘门
            color = self._get_wuxing_color("baMen", gate)
            is_bold = gate == chart_data.zhi_shi  # 检查是否为值使门
            display_text = self._get_full_name("baMen", gate)
            param_id = f"palace_{palace_data.index}_tian_pan_gate_0"
            self.param_widgets[8].set_data(display_text, config, color, is_bold, param_id, None, None, "primary")
        
        # 格子9：地盘干（右下）- 主要样式
        if palace_data.di_pan_stems:
            stem = palace_data.di_pan_stems[0]  # 主要地盘干
            color = self._get_wuxing_color("tianGan", stem)
            param_id = f"palace_{palace_data.index}_di_pan_stem_0"
            self.param_widgets[9].set_data(stem, config, color, False, param_id, None, None, "primary")
        
    def _get_full_name(self, param_type: str, param_name: str) -> str:
        """
        获取参数的完整名称
        
        Args:
            param_type: 参数类型 (jiuXing, baMen, baShen等)
            param_name: 参数简称
            
        Returns:
            完整名称，如果找不到则返回原名称
        """
        try:
            # 特殊处理八神简称映射
            if param_type == "baShen":
                bashen_map = {
                    "符": "值符",
                    "蛇": "螣蛇", 
                    "阴": "太阴",
                    "合": "六合",
                    "虎": "白虎",
                    "武": "玄武",
                    "地": "九地",
                    "天": "九天"
                }
                if param_name in bashen_map:
                    return bashen_map[param_name]
            
            param_list = self.global_data.get(param_type, [])
            for item in param_list:
                if item.get("cn") == param_name:
                    # 对于特殊情况的处理
                    if param_type == "jiuXing":
                        return f"天{param_name}"  # 蓬 -> 天蓬
                    elif param_type == "baMen":
                        return f"{param_name}门"  # 生 -> 生门
                    else:
                        return param_name
            return param_name
        except Exception:
            return param_name

    def _format_stars(self, stars: List[str]) -> str:
        """
        格式化星宿显示文本，处理双星情况
        
        Args:
            stars: 星宿列表
            
        Returns:
            格式化后的文本
        """
        if len(stars) == 1:
            return stars[0]
        elif len(stars) == 2:
            # 处理双星，特殊处理禽芮顺序
            if "禽" in stars and "芮" in stars:
                return "禽芮"  # 按传统顺序显示
            else:
                # 其他双星情况，保持原顺序
                return "".join(stars)
        else:
            # 多星情况，用逗号连接
            return ",".join(stars)
            
    def _get_wuxing_color(self, param_type: str, param_name: str) -> QColor:
        """
        根据参数类型和名称查询五行颜色
        
        Args:
            param_type: 参数类型 (tianGan, baMen, jiuXing, baShen)
            param_name: 参数名称
            
        Returns:
            对应的五行颜色，如果找不到返回黑色
        """
        try:
            # 对于八神，如果传入的是简称，先获取完整名称
            if param_type == "baShen":
                param_name = self._get_full_name("baShen", param_name)
            
            # 从global_data中查询
            param_list = self.global_data.get(param_type, [])
            for item in param_list:
                if item.get("cn") == param_name:
                    wuxing = item.get("wuxing", "")
                    return self.wuxing_colors.get(wuxing, QColor(0, 0, 0))
                    
            # 如果没找到，返回黑色
            return QColor(0, 0, 0)
            
        except Exception as e:
            print(f"查询五行颜色时出错: {param_type}, {param_name}, {e}")
            return QColor(0, 0, 0)
            
    def get_parameter_widgets(self):
        """获取所有ParameterWidget列表，用于连接标注信号"""
        return list(self.param_widgets.values())
        
    def refresh_annotations(self, annotations_dict):
        """
        刷新所有ParameterWidget的标注显示
        
        Args:
            annotations_dict: 案例的标注字典 {param_id: List[Dict[str, str]]}
        """
        for widget in self.param_widgets.values():
            param_id = widget.get_param_id()
            if not param_id:
                continue
                
            # 检查是否为双星
            dual_stars = widget.get_dual_stars()
            if dual_stars and len(dual_stars) == 2:
                # 双星情况：收集两个星的标注，不添加前缀
                all_annotations = []
                for star in dual_stars:
                    star_id = f"{param_id}_{star}"
                    if star_id in annotations_dict:
                        star_annotations = annotations_dict[star_id]
                        # 直接添加标注文本，添加星名前缀用于内部识别
                        for ann in star_annotations:
                            prefixed_text = f"{star}:{ann.get('text', '')}"
                            all_annotations.append(prefixed_text)
                
                widget.set_annotation_texts(all_annotations if all_annotations else None)
            else:
                # 单星情况：原有逻辑
                if param_id in annotations_dict:
                    annotations_list = annotations_dict[param_id]
                    annotation_texts = [ann.get('text', '') for ann in annotations_list]
                    widget.set_annotation_texts(annotation_texts)
                else:
                    widget.set_annotation_texts(None)


def create_test_data():
    """创建测试数据 - 升级版本，测试完整天地盘信息显示"""
    # 创建测试用的Palace对象（坎1宫）
    test_palace = Palace(1)
    
    # 新版Palace数据模型属性
    test_palace.zhi_fu = "值符"                    # 八神
    test_palace.tian_pan_stars = ["蓬"]             # 天盘星
    test_palace.tian_pan_gates = ["休"]             # 天盘门
    test_palace.tian_pan_stems = ["甲", "乙"]       # 天盘干（主+寄宫）
    test_palace.di_pan_stems = ["庚", "癸"]         # 地盘干（主+寄宫）
    test_palace.di_pan_star = "蓬"                  # 地盘星（故乡星）
    test_palace.di_pan_gate = "开"                  # 地盘门（故乡门）
    
    # 保持向后兼容的属性（仍需要设置以支持旧代码）
    test_palace.god = test_palace.zhi_fu
    test_palace.stars = test_palace.tian_pan_stars
    test_palace.gates = test_palace.tian_pan_gates[0] if test_palace.tian_pan_gates else ""
    test_palace.heaven_stems = test_palace.tian_pan_stems
    test_palace.earth_stems = test_palace.di_pan_stems
    test_palace.original_star = test_palace.di_pan_star
    test_palace.original_gate = test_palace.di_pan_gate
    
    # 创建双星测试用的Palace对象（艮8宫 - 禽芮双星）
    dual_star_palace = Palace(8)
    dual_star_palace.zhi_fu = "九天"
    dual_star_palace.tian_pan_stars = ["禽", "芮"]      # 双星
    dual_star_palace.tian_pan_gates = ["生"]
    dual_star_palace.tian_pan_stems = ["丙"]
    dual_star_palace.di_pan_stems = ["丙"]
    dual_star_palace.di_pan_star = "冲"
    dual_star_palace.di_pan_gate = "伤"
    
    # 向后兼容属性
    dual_star_palace.god = dual_star_palace.zhi_fu
    dual_star_palace.stars = dual_star_palace.tian_pan_stars
    dual_star_palace.gates = dual_star_palace.tian_pan_gates[0] if dual_star_palace.tian_pan_gates else ""
    dual_star_palace.heaven_stems = dual_star_palace.tian_pan_stems
    dual_star_palace.earth_stems = dual_star_palace.di_pan_stems
    dual_star_palace.original_star = dual_star_palace.di_pan_star
    dual_star_palace.original_gate = dual_star_palace.di_pan_gate
    
    # 创建测试用的中宫Palace对象
    center_palace = Palace(5)
    center_palace.di_pan_stems = ["戊"]
    center_palace.earth_stems = center_palace.di_pan_stems  # 向后兼容
    
    # 创建测试用的ChartResult对象
    test_chart = ChartResult()
    test_chart.ju_shu_info = {"遁": "阴", "局": "8"}
    test_chart.zhi_fu = "蓬"   # 值符星应该是九星名称
    test_chart.zhi_shi = "休"  # 值使门是八门名称
    
    return test_palace, dual_star_palace, center_palace, test_chart


def main():
    """
    测试脚本：验证PalaceWidget的显示功能
    """
    app = QApplication(sys.argv)
    
    # 加载测试数据
    try:
        with open("data/core_parameters.json", "r", encoding="utf-8") as f:
            global_data = json.load(f)
    except FileNotFoundError:
        # 如果找不到core_parameters.json，创建基本的测试数据
        global_data = {
            "tianGan": [
                {"cn": "甲", "wuxing": "木"},
                {"cn": "乙", "wuxing": "木"},
                {"cn": "庚", "wuxing": "金"},
                {"cn": "癸", "wuxing": "水"},
                {"cn": "丙", "wuxing": "火"},
                {"cn": "戊", "wuxing": "土"}
            ],
            "baShen": [
                {"cn": "值符", "wuxing": "土"},
                {"cn": "九天", "wuxing": "金"}
            ],
            "jiuXing": [
                {"cn": "蓬", "wuxing": "水"},
                {"cn": "禽", "wuxing": "土"},
                {"cn": "芮", "wuxing": "土"},
                {"cn": "冲", "wuxing": "金"}
            ],
            "baMen": [
                {"cn": "休", "wuxing": "水"},
                {"cn": "开", "wuxing": "金"},
                {"cn": "生", "wuxing": "土"},
                {"cn": "伤", "wuxing": "木"}
            ]
        }
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("PalaceWidget 测试")
    main_window.resize(600, 400)
    
    # 创建中央控件和布局
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # 创建显示配置
    config = DisplayConfig(
        use_wuxing_colors=True,
        show_zhi_fu_shi_bold=True
    )
    
    # 测试标题
    title_label = QLabel("PalaceWidget 测试演示")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
    layout.addWidget(title_label)
    
    # 创建测试数据
    test_palace, dual_star_palace, center_palace, test_chart = create_test_data()
    
    # 测试1：普通宫位（坎1宫）
    normal_label = QLabel("普通宫位测试（坎1宫）- 完整天地盘信息：")
    normal_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
    layout.addWidget(normal_label)
    
    normal_widget = PalaceWidget(global_data)
    normal_widget.setMaximumSize(220, 220)
    normal_widget.update_data(test_palace, test_chart, config, global_data)
    layout.addWidget(normal_widget)
    
    # 测试2：双星宫位（艮8宫）
    dual_star_label = QLabel("双星宫位测试（艮8宫）- 禽芮双星：")
    dual_star_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
    layout.addWidget(dual_star_label)
    
    dual_star_widget = PalaceWidget(global_data)
    dual_star_widget.setMaximumSize(220, 220)
    dual_star_widget.update_data(dual_star_palace, test_chart, config, global_data)
    layout.addWidget(dual_star_widget)
    
    # 测试3：中宫
    center_label = QLabel("中宫测试（5宫）：")
    center_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
    layout.addWidget(center_label)
    
    center_widget = PalaceWidget(global_data)
    center_widget.setMaximumSize(220, 220)
    center_widget.update_data(center_palace, test_chart, config, global_data)
    layout.addWidget(center_widget)
    
    # 说明信息
    info_label = QLabel(
        "升级后布局说明：\n"
        "• 左上角：地盘门（次要样式，灰色较小字体）\n"
        "• 上中：八神（主要样式）\n"
        "• 右上角：地盘星（次要样式，灰色较小字体）\n"
        "• 左中：中寄天盘干\n"
        "• 正中：天盘星（主要样式，值符加粗）\n"
        "• 右中：天盘干\n"
        "• 左下：中寄地盘干\n"
        "• 下中：天盘门（主要样式，值使加粗）\n"
        "• 右下：地盘干\n"
        "• 样式区分：天盘信息为主要样式，地盘信息为次要样式（灰色+较小字体）"
    )
    info_label.setStyleSheet("color: #666; font-size: 11px; margin: 10px; padding: 10px; background-color: #f0f0f0;")
    info_label.setWordWrap(True)
    layout.addWidget(info_label)
    
    main_window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
