"""
ChartWidget - 奇门遁甲完整盘面显示组件

整合所有UI组件的顶层容器，负责显示完整的奇门遁甲盘面，
包括九宫格、全局信息面板和宫侧方标注。
"""
import sys
import os
from typing import Dict, Optional, Union
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, 
                               QLabel, QApplication, QMainWindow, QPushButton, QLineEdit, QSizePolicy)
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtCore import Qt, QSize
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ui.widgets.palace_widget import PalaceWidget
from ui.config import DisplayConfig
from core.models import ChartResult
from core.paipan_engine import PaiPanEngine


class SquareWidget(QWidget):
    """保持正方形纵横比的容器控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def resizeEvent(self, event):
        """重写调整大小事件，强制保持正方形"""
        size = min(event.size().width(), event.size().height())
        self.setFixedSize(size, size)
        super().resizeEvent(event)
    
    def sizeHint(self):
        """返回推荐大小"""
        return QSize(700, 700)


class ChartWidget(QWidget):
    """
    奇门遁甲完整盘面显示组件
    
    功能特性：
    - 整合九个PalaceWidget显示完整九宫格
    - 显示四柱、时间、值符值使等全局信息
    - 显示十二地支位的宫侧方标注
    - 支持配置更新和实时重绘
    - 使用5x5布局实现外圈标注和中心九宫格
    """
    
    def __init__(self, global_data: dict, config: DisplayConfig, parent=None):
        """
        初始化ChartWidget
        
        Args:
            global_data: 从data.json加载的全局数据字典
            config: DisplayConfig显示配置对象
            parent: 父控件
        """
        super().__init__(parent)
        
        self.global_data = global_data
        self.config = config
        self.current_chart_data: Optional[ChartResult] = None
        
        # 初始化所有子控件
        self.info_labels = {}
        self.palace_widgets = {}
        self.annotation_labels = {}
        
        # 五行颜色映射
        self.wuxing_colors = {
            "木": "#00B400",      # 深绿色
            "火": "#FF0000",      # 红色  
            "土": "#8B4513",      # 棕色
            "金": "#FFD700",      # 金黄色
            "水": "#0000FF",      # 蓝色
        }
        
        self.init_ui()
        
        # Fix for inconsistent size bug on first tab creation
        # 设置固定尺寸确保所有新建的ChartWidget标签页大小一致
        self.setFixedSize(1000, 800)
        
    def init_ui(self):
        """初始化用户界面"""
        # 主布局：左右分割
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        
        # 左侧信息面板
        self.init_info_panel(main_layout)
        
        # 右侧主盘面区
        self.init_chart_panel(main_layout)
        
    def init_info_panel(self, parent_layout):
        """初始化左侧信息面板"""
        info_panel = QWidget()
        info_panel.setFixedWidth(250)
        info_panel.setStyleSheet(
            "background-color: #f8f8f8; "
            "border: 1px solid #ddd; "
            "border-radius: 5px; "
            "padding: 10px;"
        )
        
        info_layout = QVBoxLayout(info_panel)
        
        # 起局时间标题
        time_title = QLabel("起局信息")
        time_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        info_layout.addWidget(time_title)
        
        # 起局时间显示
        self.info_labels['time'] = QLabel("等待排盘...")
        self.info_labels['time'].setStyleSheet("font-size: 12px; color: #666; margin-bottom: 15px;")
        self.info_labels['time'].setWordWrap(True)
        info_layout.addWidget(self.info_labels['time'])
        
        # 四柱标题
        sizhu_title = QLabel("四柱")
        sizhu_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; margin-bottom: 5px;")
        info_layout.addWidget(sizhu_title)
        
        # 四柱显示 - 使用网格布局
        sizhu_widget = QWidget()
        sizhu_layout = QGridLayout(sizhu_widget)
        sizhu_layout.setSpacing(5)
        
        # 四柱标签
        headers = ["年", "月", "日", "时"]
        for i, header in enumerate(headers):
            label = QLabel(header)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-weight: bold; color: #666; font-size: 10px;")
            sizhu_layout.addWidget(label, 0, i)
        
        # 四柱内容
        for i in range(4):
            # 天干
            self.info_labels[f'sizhu_gan_{i}'] = QLabel("-")
            self.info_labels[f'sizhu_gan_{i}'].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.info_labels[f'sizhu_gan_{i}'].setStyleSheet("font-size: 14px; font-weight: bold;")
            sizhu_layout.addWidget(self.info_labels[f'sizhu_gan_{i}'], 1, i)
            
            # 地支
            self.info_labels[f'sizhu_zhi_{i}'] = QLabel("-")
            self.info_labels[f'sizhu_zhi_{i}'].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.info_labels[f'sizhu_zhi_{i}'].setStyleSheet("font-size: 14px; font-weight: bold;")
            sizhu_layout.addWidget(self.info_labels[f'sizhu_zhi_{i}'], 2, i)
        
        info_layout.addWidget(sizhu_widget)
        
        # 其他信息
        other_title = QLabel("盘面信息")
        other_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; margin: 15px 0 5px 0;")
        info_layout.addWidget(other_title)
        
        # 节气、局数、值符值使等
        info_items = [
            ('jieqi', '节气'),
            ('jushu', '局数'),
            ('zhifu', '值符'),
            ('zhishi', '值使'),
            ('maxing', '马星'),
            ('kongwang', '空亡')
        ]
        
        for key, label_text in info_items:
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            title_label = QLabel(f"{label_text}：")
            title_label.setStyleSheet("font-size: 11px; color: #666; font-weight: bold;")
            title_label.setFixedWidth(50)
            
            self.info_labels[key] = QLabel("-")
            self.info_labels[key].setStyleSheet("font-size: 11px; color: #333;")
            self.info_labels[key].setWordWrap(True)
            
            container_layout.addWidget(title_label)
            container_layout.addWidget(self.info_labels[key])
            container_layout.addStretch()
            
            info_layout.addWidget(container)
        
        info_layout.addStretch()
        parent_layout.addWidget(info_panel)
        
    def init_chart_panel(self, parent_layout):
        """初始化右侧主盘面区"""
        chart_panel = SquareWidget()
        chart_panel.setStyleSheet(
            "background-color: white; "
            "border: 1px solid #ddd; "
            "border-radius: 5px;"
        )
        
        # 设置较大的最小尺寸
        chart_panel.setMinimumSize(700, 700)
        
        # 使用5x5网格布局：外圈标注 + 中心3x3九宫格
        chart_layout = QGridLayout(chart_panel)
        chart_layout.setSpacing(2)  # 很小的间距
        
        # 十二地支位标注的位置映射
        # 根据正确的奇门遁甲布局：
        #     巳 午 未
        # 辰  4  9  2 申
        # 卯  3  5  7 酉
        # 寅  8  1  6 戌
        #     丑 子 亥
        annotation_positions = {
            "子": (4, 2),  # 正下方
            "丑": (4, 1),  # 左下角
            "寅": (3, 0),  # 左下
            "卯": (2, 0),  # 正左
            "辰": (1, 0),  # 左上
            "巳": (0, 1),  # 上左
            "午": (0, 2),  # 正上
            "未": (0, 3),  # 上右
            "申": (1, 4),  # 右上
            "酉": (2, 4),  # 正右
            "戌": (3, 4),  # 右下
            "亥": (4, 3),  # 右下角
        }
        
        # 创建标注QLabel，尺寸与相邻宫位一致
        for dizhi, (row, col) in annotation_positions.items():
            label = QLabel("")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # 判断标注类型：左右/上下
            if col == 0 or col == 4:
                # 左右标注，高度与宫位一致，宽度较窄
                label.setMinimumWidth(24)
                label.setMaximumWidth(36)
                label.setMinimumHeight(120)
                label.setMaximumHeight(16777215)
            elif row == 0 or row == 4:
                # 上下标注，宽度与宫位一致，高度较窄
                label.setMinimumHeight(24)
                label.setMaximumHeight(36)
                label.setMinimumWidth(120)
                label.setMaximumWidth(16777215)
            else:
                # 斜角标注，设置为正方形
                label.setMinimumSize(24, 24)
                label.setMaximumSize(36, 36)
            label.setStyleSheet(
                "font-size: 10px; color: red; font-weight: bold; "
                "border: 1px solid #eee; background-color: #fafafa; "
            )
            self.annotation_labels[dizhi] = label
            chart_layout.addWidget(label, row, col)
        
        # 九宫格位置映射（中心3x3区域）
        # 根据正确的奇门遁甲布局：
        #     巳 午 未
        # 辰  4  9  2 申
        # 卯  3  5  7 酉  
        # 寅  8  1  6 戌
        #     丑 子 亥
        # 在5x5网格中，中心3x3区域是(1,1)到(3,3)
        # 修正：宫1在正下方，宫8在左下角
        palace_positions = {
            1: (3, 2), 2: (1, 3), 3: (2, 1),  # 1在正下方, 2在右上, 3在左中
            4: (1, 1), 5: (2, 2), 6: (3, 3),  # 4在左上, 5在中央, 6在右下  
            7: (2, 3), 8: (3, 1), 9: (1, 2),  # 7在右中, 8在左下, 9在上中
        }
        
        # 创建九个PalaceWidget
        for palace_id, (row, col) in palace_positions.items():
            palace_widget = PalaceWidget(self.global_data)
            # 设置较大的最小尺寸
            palace_widget.setMinimumSize(120, 120)
            palace_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            palace_widget.setStyleSheet(
                "border: 2px solid #333; "
                "background-color: #fdfdfd; "
                "border-radius: 3px;"
            )
            self.palace_widgets[palace_id] = palace_widget
            chart_layout.addWidget(palace_widget, row, col)
        
        # 设置行和列的拉伸比例：边缘留白，九宫格居中
        for i in range(5):
            if i == 0 or i == 4:
                chart_layout.setRowStretch(i, 2)
                chart_layout.setColumnStretch(i, 2)
            else:
                chart_layout.setRowStretch(i, 7)
                chart_layout.setColumnStretch(i, 7)
        
        parent_layout.addWidget(chart_panel)
        
    def update_chart(self, chart_data: ChartResult):
        """
        更新完整盘面显示
        
        Args:
            chart_data: 包含所有排盘和分析结果的ChartResult对象
        """
        self.current_chart_data = chart_data
        
        # 更新信息面板
        self._update_info_panel(chart_data)
        
        # 更新九宫格
        self._update_palace_widgets(chart_data)
        
        # 更新侧方标注
        self._update_side_annotations(chart_data)
        
    def update_config(self, config: DisplayConfig):
        """
        更新显示配置并重绘
        
        Args:
            config: 包含所有显示选项的DisplayConfig对象
        """
        self.config = config
        
        # 如果有当前数据，则重新绘制
        if self.current_chart_data:
            self.update_chart(self.current_chart_data)
            
    def _update_info_panel(self, chart_data: ChartResult):
        """更新左侧信息面板"""
        # 更新起局时间信息（YYYY年MM月DD日 HH:MM格式）
        if hasattr(chart_data, 'qi_ju_time') and chart_data.qi_ju_time:
            time_text = f"起局时间：{chart_data.qi_ju_time}"
        else:
            # 如果没有起局时间信息，显示提示
            time_text = "起局时间：未知"
        
        self.info_labels['time'].setText(time_text)
        
        # 更新四柱显示（带五行颜色）
        sizhu_items = [
            (chart_data.si_zhu.get('年', ''), 0),
            (chart_data.si_zhu.get('月', ''), 1),
            (chart_data.si_zhu.get('日', ''), 2),
            (chart_data.si_zhu.get('时', ''), 3),
        ]
        
        for sizhu_str, index in sizhu_items:
            if len(sizhu_str) >= 2:
                gan = sizhu_str[0]
                zhi = sizhu_str[1]
                
                # 天干颜色
                gan_color = self._get_wuxing_color("tianGan", gan)
                gan_html = f'<font color="{gan_color}">{gan}</font>' if self.config.use_wuxing_colors else gan
                self.info_labels[f'sizhu_gan_{index}'].setText(gan_html)
                
                # 地支颜色
                zhi_color = self._get_wuxing_color("diZhi", zhi)
                zhi_html = f'<font color="{zhi_color}">{zhi}</font>' if self.config.use_wuxing_colors else zhi
                self.info_labels[f'sizhu_zhi_{index}'].setText(zhi_html)
        
        # 更新其他信息
        # 月令显示：如果在亥，显示为"亥月水旺"
        jieqi_text = self._format_jieqi_display(chart_data.jieqi)
        self.info_labels['jieqi'].setText(jieqi_text)
        
        jushu_text = f"{chart_data.ju_shu_info.get('遁', '')}{chart_data.ju_shu_info.get('局', '')}局"
        self.info_labels['jushu'].setText(jushu_text)
        
        self.info_labels['zhifu'].setText(chart_data.zhi_fu)
        self.info_labels['zhishi'].setText(chart_data.zhi_shi)
        
        # 马星显示：如果在寅，显示为"马星在寅"
        maxing_text = self._format_maxing_display(chart_data.ma_xing)
        self.info_labels['maxing'].setText(maxing_text)
        
        # 空亡信息：时空在子显示为"子空"，日空在丑显示为"丑空"
        kongwang_text = self._format_kongwang_display(chart_data.kong_wang)
        self.info_labels['kongwang'].setText(kongwang_text)
        
    def _update_palace_widgets(self, chart_data: ChartResult):
        """更新九宫格显示"""
        for palace_id, palace_widget in self.palace_widgets.items():
            palace_data = chart_data.palaces[palace_id]
            palace_widget.update_data(
                palace_data, 
                chart_data, 
                self.config, 
                self.global_data
            )
            
    def _update_side_annotations(self, chart_data: ChartResult):
        """
        更新宫侧方标注 - V2精密渲染引擎
        
        严格按照UI渲染业务规则附录实现的条件渲染引擎
        """
        # 纵向排布的地支位（左右两侧）
        vertical_dizhi = {"寅", "卯", "辰", "申", "酉", "戌"}
        
        # 获取马星冲动目标信息（用于样式应用）
        maxing_chongdong_targets = getattr(chart_data, 'maxing_chongdong_targets', [])
        
        # 遍历十二地支标注
        for dizhi, label in self.annotation_labels.items():
            annotations = chart_data.side_annotations.get(dizhi, [])
            
            # B.1 基础显示控制 - 筛选可见标注
            visible_annotations = []
            for anno in annotations:
                anno_type = anno.get('type', '')
                
                # 检查总开关
                if ((anno_type == 'liuji' and self.config.show_liu_ji) or
                    (anno_type == 'rumu' and self.config.show_ru_mu) or
                    (anno_type == 'rikong' and self.config.show_ri_kong) or
                    (anno_type == 'shikong' and self.config.show_shi_kong) or
                    (anno_type == 'shuangkong' and (self.config.show_ri_kong or self.config.show_shi_kong)) or
                    (anno_type == 'yueling' and self.config.show_yue_ling) or
                    (anno_type == 'maxing' and self.config.show_ma_xing)):
                    visible_annotations.append(anno)
            
            # B.2 格式化标注文本，应用精密样式控制
            formatted_annotations = []
            
            # 获取马星冲动目标信息（用于马星样式应用）
            maxing_chongdong_targets = getattr(chart_data, 'maxing_chongdong_targets', [])
            
            for anno in visible_annotations:
                # 获取基础格式化文本
                base_text = self._format_side_annotation(anno, dizhi)
                final_text = base_text
                
                # 1. 月令自动填空样式（使用现有的auto_yue_ling_chong_kong配置）
                if (self.config.auto_yue_ling_chong_kong and 
                    anno.get('strike', False)):
                    final_text = f"<s>{base_text}</s>"
                
                # 2. 马星自动冲墓、冲空样式（使用现有的auto_maxing_chong_mu_kong配置）
                elif (self.config.auto_maxing_chong_mu_kong and
                      maxing_chongdong_targets and
                      self._is_maxing_target_match(anno, maxing_chongdong_targets, dizhi)):
                    final_text = f"<s>{base_text}</s>"
                
                formatted_annotations.append(final_text)
            
            # B.3 最终渲染
            if formatted_annotations:
                # 检查是否包含富文本标记
                has_rich_text = any('<s>' in text or '<strike>' in text for text in formatted_annotations)
                
                # 判断是否是纵向地支位
                if dizhi in vertical_dizhi:
                    # 纵向地支采用换行格式
                    if has_rich_text:
                        # 富文本模式使用HTML换行标签
                        annotation_text = '<br>'.join(formatted_annotations)
                    else:
                        # 纯文本模式使用换行符
                        annotation_text = '\n'.join(formatted_annotations)
                else:
                    # 横向地支继续使用空格分隔（富文本和纯文本都一样）
                    annotation_text = ' '.join(formatted_annotations)
                
                # 设置文本内容和格式
                if has_rich_text:
                    # 启用富文本显示删除线
                    label.setText(annotation_text)
                    label.setTextFormat(Qt.TextFormat.RichText)
                else:
                    label.setText(annotation_text)
                    label.setTextFormat(Qt.TextFormat.PlainText)
            else:
                # 如果没有可见标注，清空QLabel
                label.setText("")
                label.setTextFormat(Qt.TextFormat.PlainText)
    
    def _is_maxing_target_match(self, anno: dict, maxing_targets: list, dizhi: str) -> bool:
        """
        检查标注是否匹配马星冲动目标列表中的任何一个目标
        
        Args:
            anno: 标注对象
            maxing_targets: 马星冲动目标列表
            dizhi: 地支位置
            
        Returns:
            是否匹配
        """
        if not maxing_targets:
            return False
            
        anno_type = anno.get('type', '')
        
        # 检查是否匹配目标列表中的任何一个
        for target in maxing_targets:
            # 首先检查位置是否匹配
            if dizhi != target.get('location_zhi'):
                continue
                
            target_type = target.get('type', '')
            
            # 直接类型匹配
            if anno_type == target_type:
                return True
            
            # 特殊类型映射：kongwang -> shikong/rikong
            if target_type == 'kongwang' and anno_type in ['shikong', 'rikong']:
                return True
        
        return False
                
    def _get_wuxing_color(self, param_type: str, param_name: str) -> str:
        """
        根据参数类型和名称查询五行颜色（返回HTML颜色代码）
        
        Args:
            param_type: 参数类型 (tianGan, diZhi等)
            param_name: 参数名称
            
        Returns:
            HTML颜色代码字符串
        """
        try:
            param_list = self.global_data.get(param_type, [])
            for item in param_list:
                if item.get("cn") == param_name:
                    wuxing = item.get("wuxing", "")
                    return self.wuxing_colors.get(wuxing, "#000000")
            return "#000000"
        except Exception:
            return "#000000"
    
    def _format_side_annotation(self, annotation: Dict[str, Union[str, bool]], dizhi: str) -> str:
        """
        格式化侧方标注显示内容（V2版本 - 纯文本格式化）
        
        Args:
            annotation: 包含type、text等字段的字典
            dizhi: 地支名称
            
        Returns:
            格式化后的纯文本（不包含样式标记）
        """
        annotation_type = annotation.get("type", "")
        text = annotation.get("text", "")
        
        # 格式化基础文本 - 支持英文和中文类型名称
        if annotation_type in ["空亡", "rikong", "shikong"]:
            return f"{dizhi}空"
        elif annotation_type == "shuangkong":
            # 双空类型直接使用text字段（引擎已经格式化好了）
            return text if text else f"双{dizhi}空"
        elif annotation_type in ["马星", "maxing"]:
            return f"马星在{dizhi}"
        elif annotation_type in ["月令", "yueling"]:
            # 根据地支确定五行
            dizhi_wuxing = {
                "子": "水", "亥": "水",
                "寅": "木", "卯": "木",
                "巳": "火", "午": "火",
                "申": "金", "酉": "金",
                "辰": "土", "戌": "土", "丑": "土", "未": "土"
            }
            wuxing = dizhi_wuxing.get(dizhi, "")
            return f"{dizhi}月{wuxing}旺"
        else:
            # 其他标注使用原文本或类型名称
            return text if text else annotation_type
    
    def _format_jieqi_display(self, jieqi):
        """
        格式化节气显示，如"亥月水旺"
        
        Args:
            jieqi: 原始节气信息
            
        Returns:
            格式化后的节气显示文本
        """
        if not jieqi:
            return ""
        
        # 如果节气信息包含地支，添加五行信息
        # 假设节气格式可能是"亥"、"立冬"等
        if len(jieqi) == 1 and jieqi in "子丑寅卯辰巳午未申酉戌亥":
            # 获取地支的五行
            wuxing = self._get_dizhi_wuxing(jieqi)
            if wuxing:
                return f"{jieqi}月{wuxing}旺"
        
        return jieqi
    
    def _format_maxing_display(self, maxing):
        """
        格式化马星显示（信息面板中只显示地支）
        
        Args:
            maxing: 原始马星信息
            
        Returns:
            格式化后的马星显示文本
        """
        if not maxing:
            return ""
        
        # 信息面板中只显示地支，不添加"马星在"前缀
        if len(maxing) == 1 and maxing in "子丑寅卯辰巳午未申酉戌亥":
            return maxing
        
        return maxing
    
    def _format_kongwang_display(self, kong_wang):
        """
        格式化空亡显示，如"日空(子，丑) 时空(寅，卯)"
        
        Args:
            kong_wang: 包含日空和时空信息的字典
            
        Returns:
            格式化后的空亡显示文本
        """
        if not kong_wang:
            return ""
        
        parts = []
        
        # 日空处理 - 格式：日空(X，X)
        ri_kong_list = kong_wang.get('日空', [])
        if ri_kong_list:
            ri_kong_text = '，'.join(ri_kong_list)  # 使用中文逗号分隔
            parts.append(f"日空({ri_kong_text})")
        
        # 时空处理 - 格式：时空(X，X)
        shi_kong_list = kong_wang.get('时空', [])
        if shi_kong_list:
            shi_kong_text = '，'.join(shi_kong_list)  # 使用中文逗号分隔
            parts.append(f"时空({shi_kong_text})")
        
        return ' '.join(parts)
    
    def _get_dizhi_wuxing(self, dizhi):
        """
        获取地支的五行属性
        
        Args:
            dizhi: 地支字符
            
        Returns:
            对应的五行属性
        """
        try:
            param_list = self.global_data.get("diZhi", [])
            for item in param_list:
                if item.get("cn") == dizhi:
                    return item.get("wuxing", "")
            return ""
        except Exception:
            return ""
    
    def resizeEvent(self, event):
        """重写大小调整事件，维持正方形比例"""
        super().resizeEvent(event)
        # 触发重绘以更新网格
        self.update()
    
    def paintEvent(self, event):
        """重写绘制事件，绘制九宫格边界"""
        super().paintEvent(event)
        
        # 只有当有盘面数据时才绘制网格
        if not self.current_chart_data or len(self.palace_widgets) < 9:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 收集所有宫位相对于ChartWidget的位置信息
        palace_info = {}
        for palace_id, widget in self.palace_widgets.items():
            if widget.isVisible():
                # 获取相对于当前widget(ChartWidget)的位置
                widget_pos = widget.mapTo(self, widget.rect().topLeft())
                widget_size = widget.size()
                palace_info[palace_id] = {
                    'x': widget_pos.x(), 
                    'y': widget_pos.y(), 
                    'width': widget_size.width(), 
                    'height': widget_size.height(),
                    'right': widget_pos.x() + widget_size.width(),
                    'bottom': widget_pos.y() + widget_size.height()
                }
        
        # 打印调试信息（可选）
        if False and len(palace_info) >= 9:  # 设置为False关闭调试输出
            print("\n=== 九宫格相对位置调试信息 ===")
            for palace_id in [4, 9, 2, 3, 5, 7, 8, 1, 6]:
                if palace_id in palace_info:
                    info = palace_info[palace_id]
                    print(f"宫{palace_id}: x={info['x']}, y={info['y']}, w={info['width']}, h={info['height']}")
            
            # 按Y坐标排序找出行
            y_positions = {}
            for palace_id, info in palace_info.items():
                y = info['y']
                if y not in y_positions:
                    y_positions[y] = []
                y_positions[y].append(palace_id)
            
            sorted_rows = sorted(y_positions.items())
            print("\n实际按行排列:")
            for i, (y, palaces) in enumerate(sorted_rows):
                palaces_by_x = sorted(palaces, key=lambda p: palace_info[p]['x'])
                print(f"第{i+1}行(y={y}): {' '.join(map(str, palaces_by_x))}")
        
        # 绘制九宫格 - 使用相对坐标
        if len(palace_info) >= 9:
            # 设置网格线样式
            pen = QPen(QColor("#000000"))  # 黑色
            pen.setWidth(2)
            painter.setPen(pen)
            
            # 根据宫位布局确定关键坐标
            # 4 9 2
            # 3 5 7
            # 8 1 6
            
            try:
                # 获取九宫格的边界
                left_edge = palace_info[4]['x']  # 宫4的左边
                right_edge = palace_info[2]['right']  # 宫2的右边
                top_edge = palace_info[4]['y']  # 宫4的上边
                bottom_edge = palace_info[8]['bottom']  # 宫8的下边
                
                # 获取分割线位置
                middle_x1 = palace_info[9]['x']  # 宫9的左边（第一条垂直分割线）
                middle_x2 = palace_info[2]['x']  # 宫2的左边（第二条垂直分割线）
                middle_y1 = palace_info[3]['y']  # 宫3的上边（第一条水平分割线）
                middle_y2 = palace_info[8]['y']  # 宫8的上边（第二条水平分割线）
                
                # 关闭调试输出，保持界面清洁
                # print(f"\n九宫格边界: left={left_edge}, right={right_edge}, top={top_edge}, bottom={bottom_edge}")
                # print(f"分割线: x1={middle_x1}, x2={middle_x2}, y1={middle_y1}, y2={middle_y2}")
                
                # 绘制九宫格边框和分割线
                # 外边框
                painter.drawRect(left_edge, top_edge, right_edge - left_edge, bottom_edge - top_edge)
                
                # 垂直分割线
                painter.drawLine(middle_x1, top_edge, middle_x1, bottom_edge)
                painter.drawLine(middle_x2, top_edge, middle_x2, bottom_edge)
                
                # 水平分割线
                painter.drawLine(left_edge, middle_y1, right_edge, middle_y1)
                painter.drawLine(left_edge, middle_y2, right_edge, middle_y2)
                
            except KeyError as e:
                print(f"绘制九宫格时缺少宫位信息: {e}")
            except Exception as e:
                print(f"绘制九宫格时出错: {e}")


def main():
    """
    测试脚本：验证ChartWidget的完整显示功能
    """
    app = QApplication(sys.argv)
    
    # 加载全局数据
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            global_data = json.load(f)
    except FileNotFoundError:
        print("未找到data.json文件，使用基础测试数据")
        global_data = {}
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("奇门遁甲完整盘面演示 - ChartWidget")
    main_window.setGeometry(100, 100, 1000, 700)
    
    # 创建控制面板
    control_panel = QWidget()
    control_layout = QVBoxLayout(control_panel)
    
    # 时间输入
    input_layout = QHBoxLayout()
    input_layout.addWidget(QLabel("时间(YYYYMMDDHHMM):"))
    time_input = QLineEdit("202412011530")
    input_layout.addWidget(time_input)
    
    # 配置控制
    config_layout = QHBoxLayout()
    
    # 创建显示配置
    config = DisplayConfig(use_wuxing_colors=True, show_zhi_fu_shi_bold=True)
    
    # 创建ChartWidget
    chart_widget = ChartWidget(global_data, config)
    
    def update_chart():
        """更新盘面"""
        time_str = time_input.text().strip()
        if len(time_str) >= 10:
            try:
                # 确保时间格式
                if len(time_str) == 10:
                    time_str += "00"
                if len(time_str) == 12:
                    time_str += "00"
                
                # 排盘
                engine = PaiPanEngine(data_file_path='data.json')
                chart_result = engine.paipan(time_str)
                
                # 更新显示
                chart_widget.update_chart(chart_result)
                
            except Exception as e:
                print(f"排盘出错: {e}")
    
    def toggle_colors():
        """切换五行颜色显示"""
        new_config = DisplayConfig(
            use_wuxing_colors=not config.use_wuxing_colors,
            show_zhi_fu_shi_bold=config.show_zhi_fu_shi_bold
        )
        chart_widget.update_config(new_config)
        config.use_wuxing_colors = new_config.use_wuxing_colors
    
    # 按钮
    update_btn = QPushButton("更新盘面")
    update_btn.clicked.connect(update_chart)
    input_layout.addWidget(update_btn)
    
    color_btn = QPushButton("切换五行颜色")
    color_btn.clicked.connect(toggle_colors)
    config_layout.addWidget(color_btn)
    
    control_layout.addLayout(input_layout)
    control_layout.addLayout(config_layout)
    control_layout.addWidget(chart_widget)
    
    main_window.setCentralWidget(control_panel)
    
    # 默认显示一个盘面
    update_chart()
    
    main_window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
