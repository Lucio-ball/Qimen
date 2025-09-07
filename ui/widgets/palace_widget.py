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
        更新宫位显示数据
        
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
            widget.set_data("", config, QColor(0, 0, 0), False, "")
            
    def _update_center_palace(self, palace_data: Palace, chart_data: ChartResult,
                             config: DisplayConfig, global_data: dict):
        """
        更新中宫显示
        
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
                self.param_widgets[5].set_data(ju_shu_text, config, tu_color, False, "")
            elif i == 9:
                # 格子9：显示中宫地盘干（中宫特有，不可操作）
                if palace_data.earth_stems:
                    earth_stem = palace_data.earth_stems[0]
                    color = self._get_wuxing_color("tianGan", earth_stem)
                    # 不设置参数ID，使其无法右键操作
                    self.param_widgets[9].set_data(earth_stem, config, color, False, "")
                else:
                    # 没有地盘干时，设置空的不可操作格子
                    self.param_widgets[9].set_data("", config, "#000000", False, "")
            else:
                # 其他格子设置为空的且不可操作
                self.param_widgets[i].set_data("", config, "#000000", False, "")
            
    def _update_normal_palace(self, palace_data: Palace, chart_data: ChartResult,
                             config: DisplayConfig, global_data: dict):
        """
        更新普通宫位显示
        
        Args:
            palace_data: Palace对象
            chart_data: ChartResult对象
            config: DisplayConfig对象
            global_data: 全局数据字典
        """
        # 存储全局数据供其他方法使用
        self.global_data = global_data
        
        # 格子2：八神（八神本身不加粗）
        if palace_data.god:
            color = self._get_wuxing_color("baShen", palace_data.god)
            is_bold = False  # 八神本身不加粗
            # 始终显示完整名称
            display_text = self._get_full_name("baShen", palace_data.god)
            param_id = f"palace_{palace_data.index}_god"
            self.param_widgets[2].set_data(display_text, config, color, is_bold, param_id)
            
        # 格子5：九星（值符星需要加粗）
        if palace_data.stars:
            # 处理双星情况（如禽芮）
            if len(palace_data.stars) == 2:
                # 双星情况使用简化显示，避免过长
                star_text = self._format_stars(palace_data.stars)
                # 传递双星信息给ParameterWidget，特殊处理禽芮顺序
                if "禽" in palace_data.stars and "芮" in palace_data.stars:
                    dual_stars = ["禽", "芮"]  # 按传统顺序
                else:
                    dual_stars = palace_data.stars
            else:
                # 单星情况始终显示完整名称
                star_text = self._get_full_name("jiuXing", palace_data.stars[0])
                dual_stars = None
            
            color = self._get_wuxing_color("jiuXing", palace_data.stars[0])
            is_bold = chart_data.zhi_fu in palace_data.stars  # 检查是否包含值符星
            param_id = f"palace_{palace_data.index}_star_0"
            self.param_widgets[5].set_data(star_text, config, color, is_bold, param_id, annotation_texts=None, dual_stars=dual_stars)
            
        # 格子8：八门
        if palace_data.gates:
            color = self._get_wuxing_color("baMen", palace_data.gates)
            is_bold = palace_data.gates == chart_data.zhi_shi
            # 始终显示完整名称
            display_text = self._get_full_name("baMen", palace_data.gates)
            param_id = f"palace_{palace_data.index}_gate"
            self.param_widgets[8].set_data(display_text, config, color, is_bold, param_id)
            
        # 格子6：天盘干（主要）
        if palace_data.heaven_stems:
            heaven_stem = palace_data.heaven_stems[0]
            color = self._get_wuxing_color("tianGan", heaven_stem)
            param_id = f"palace_{palace_data.index}_heaven_stem_0"
            self.param_widgets[6].set_data(heaven_stem, config, color, False, param_id)
            
        # 格子9：地盘干（主要）
        if palace_data.earth_stems:
            earth_stem = palace_data.earth_stems[0]
            color = self._get_wuxing_color("tianGan", earth_stem)
            param_id = f"palace_{palace_data.index}_earth_stem_0"
            self.param_widgets[9].set_data(earth_stem, config, color, False, param_id)
            
        # 处理寄宫天干（格子4和格子7）
        self._handle_additional_stems(palace_data, config)
        
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
            
    def _handle_additional_stems(self, palace_data: Palace, config: DisplayConfig):
        """
        处理寄宫天干，显示到格子4和格子7
        
        Args:
            palace_data: Palace对象
            config: DisplayConfig对象
        """
        # 天盘干的额外显示
        if len(palace_data.heaven_stems) > 1:
            for i, stem in enumerate(palace_data.heaven_stems[1:], 1):
                if i == 1 and 4 in self.param_widgets:  # 格子4
                    color = self._get_wuxing_color("tianGan", stem)
                    param_id = f"palace_{palace_data.index}_heaven_stem_{i}"
                    self.param_widgets[4].set_data(stem, config, color, False, param_id)
                elif i == 2 and 7 in self.param_widgets:  # 格子7
                    color = self._get_wuxing_color("tianGan", stem)
                    param_id = f"palace_{palace_data.index}_heaven_stem_{i}"
                    self.param_widgets[7].set_data(stem, config, color, False, param_id)
                    
        # 地盘干的额外显示
        if len(palace_data.earth_stems) > 1:
            for i, stem in enumerate(palace_data.earth_stems[1:], 1):
                if i == 1 and 7 in self.param_widgets:  # 格子7（左下角）
                    color = self._get_wuxing_color("tianGan", stem)
                    param_id = f"palace_{palace_data.index}_earth_stem_{i}"
                    self.param_widgets[7].set_data(stem, config, color, False, param_id)
                elif i == 2 and 3 in self.param_widgets:  # 格子3
                    color = self._get_wuxing_color("tianGan", stem)
                    param_id = f"palace_{palace_data.index}_earth_stem_{i}"
                    self.param_widgets[3].set_data(stem, config, color, False, param_id)
                    
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
    """创建测试数据"""
    # 创建测试用的Palace对象
    test_palace = Palace(1)
    test_palace.god = "值符"
    test_palace.stars = ["蓬"]
    test_palace.gates = "休"
    test_palace.heaven_stems = ["甲", "乙"]
    test_palace.earth_stems = ["庚"]
    
    # 创建测试用的中宫Palace对象
    center_palace = Palace(5)
    center_palace.earth_stems = ["戊"]
    
    # 创建测试用的ChartResult对象
    test_chart = ChartResult()
    test_chart.ju_shu_info = {"遁": "阴", "局": "8"}
    test_chart.zhi_fu = "蓬"  # 值符星应该是九星名称，比如"蓬"
    test_chart.zhi_shi = "休"  # 值使门是八门名称
    
    return test_palace, center_palace, test_chart


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
                {"cn": "戊", "wuxing": "土"}
            ],
            "baShen": [
                {"cn": "值符", "wuxing": "土"}
            ],
            "jiuXing": [
                {"cn": "蓬", "wuxing": "水"}
            ],
            "baMen": [
                {"cn": "休", "wuxing": "水"}
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
    test_palace, center_palace, test_chart = create_test_data()
    
    # 测试1：普通宫位
    normal_label = QLabel("普通宫位测试（坎1宫）：")
    normal_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
    layout.addWidget(normal_label)
    
    normal_widget = PalaceWidget(global_data)
    normal_widget.setMaximumSize(200, 200)
    normal_widget.update_data(test_palace, test_chart, config, global_data)
    layout.addWidget(normal_widget)
    
    # 测试2：中宫
    center_label = QLabel("中宫测试（5宫）：")
    center_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
    layout.addWidget(center_label)
    
    center_widget = PalaceWidget(global_data)
    center_widget.setMaximumSize(200, 200)
    center_widget.update_data(center_palace, test_chart, config, global_data)
    layout.addWidget(center_widget)
    
    # 说明信息
    info_label = QLabel(
        "说明：\n"
        "• 普通宫位显示：八神(左上)、九星(中)、八门(上)、天盘干(右)、地盘干(右下)\n"
        "• 中宫显示：局数信息(中)、地盘干(右下)\n"
        "• 加粗显示：值符、值使\n"
        "• 颜色：根据五行属性显示对应颜色"
    )
    info_label.setStyleSheet("color: #666; font-size: 11px; margin: 10px; padding: 10px; background-color: #f0f0f0;")
    info_label.setWordWrap(True)
    layout.addWidget(info_label)
    
    main_window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
