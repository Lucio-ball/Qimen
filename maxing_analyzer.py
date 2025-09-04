#!/usr/bin/env python3
"""
马星信息分析工具 - 简化版本，专注显示马星详细信息
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.paipan_engine import PaiPanEngine
from ui.config import DisplayConfig
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QPushButton, QLineEdit, QLabel, QCheckBox
from PySide6.QtCore import Qt
import json

class MaxingInfoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("马星信息分析工具")
        self.setGeometry(200, 200, 900, 700)
        
        self.engine = PaiPanEngine()
        self.config = DisplayConfig()
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 控制区域
        control_layout = QHBoxLayout()
        
        # 时间输入
        control_layout.addWidget(QLabel("时间:"))
        self.time_input = QLineEdit("20220101060000")
        control_layout.addWidget(self.time_input)
        
        # 控制选项
        self.auto_maxing_check = QCheckBox("马星冲墓空")
        self.auto_maxing_check.setChecked(True)
        control_layout.addWidget(self.auto_maxing_check)
        
        # 排盘按钮
        paipan_btn = QPushButton("分析马星")
        paipan_btn.clicked.connect(self.analyze_maxing)
        control_layout.addWidget(paipan_btn)
        
        # 快速测试按钮
        test_btn = QPushButton("测试已知案例")
        test_btn.clicked.connect(self.test_known_cases)
        control_layout.addWidget(test_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 信息显示区域
        self.info_display = QTextEdit()
        self.info_display.setFont(self.get_monospace_font())
        layout.addWidget(self.info_display)
        
        # 初始分析
        self.analyze_maxing()
        
    def get_monospace_font(self):
        """获取等宽字体"""
        from PySide6.QtGui import QFont
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        return font
        
    def analyze_maxing(self):
        """分析马星信息"""
        time_str = self.time_input.text()
        
        # 更新配置
        self.config.auto_maxing_chong_mu_kong = self.auto_maxing_check.isChecked()
        
        try:
            # 排盘
            result = self.engine.paipan(time_str)
            
            # 生成详细分析报告
            report = self.generate_analysis_report(result, time_str)
            self.info_display.setText(report)
            
        except Exception as e:
            self.info_display.setText(f"分析错误: {e}")
            
    def test_known_cases(self):
        """测试已知的马星案例"""
        known_cases = [
            "20220101030000",  # 己入墓
            "20220101060000",  # 时空 (kongwang -> shikong)
            "20220101090000",  # 辛入墓
            "20230301140000",  # 戊入墓
            "20240515120000",  # 随机测试
        ]
        
        reports = []
        reports.append("🧪 已知马星案例批量测试")
        reports.append("=" * 80)
        
        for time_str in known_cases:
            try:
                result = self.engine.paipan(time_str)
                year = time_str[:4]
                month = time_str[4:6]
                day = time_str[6:8]
                hour = time_str[8:10]
                
                reports.append(f"\n📅 {year}-{month}-{day} {hour}:00")
                reports.append("-" * 40)
                
                maxing_targets = getattr(result, 'maxing_chongdong_targets', [])
                if maxing_targets:
                    reports.append(f"⚡ 马星冲动: 找到 {len(maxing_targets)} 个目标")
                    
                    # 显示所有目标
                    for i, target in enumerate(maxing_targets, 1):
                        target_zhi = target.get('location_zhi')
                        target_type = target.get('type')
                        target_text = target.get('text', '')
                        reports.append(f"   {i}. {target_type} 在 {target_zhi}: {target_text}")
                    
                    # 检查第一个目标的标注匹配（示例）
                    first_target = maxing_targets[0]
                    target_zhi = first_target.get('location_zhi')
                    annotations = result.side_annotations.get(target_zhi, [])
                    styled_annotations = []
                    
                    for anno in annotations:
                        is_match = self._test_maxing_match(anno, maxing_targets, target_zhi)
                        anno_text = anno.get('text', anno.get('type'))
                        if is_match:
                            styled_annotations.append(f"<{anno_text}>")
                        else:
                            styled_annotations.append(anno_text)
                    
                    reports.append(f"📍 {target_zhi}位标注: {' '.join(styled_annotations)}")
                    
                else:
                    reports.append("❌ 无马星冲动")
                    
            except Exception as e:
                reports.append(f"❌ 错误: {e}")
        
        self.info_display.setText("\n".join(reports))
        
    def generate_analysis_report(self, result, time_str):
        """生成详细的分析报告"""
        lines = []
        
        # 标题
        lines.append("🐎 马星冲动详细分析报告")
        lines.append("=" * 80)
        
        # 基本信息
        year = time_str[:4]
        month = time_str[4:6]
        day = time_str[6:8]
        hour = time_str[8:10]
        minute = time_str[10:12] if len(time_str) > 10 else "00"
        
        lines.append(f"📅 排盘时间: {year}-{month}-{day} {hour}:{minute}")
        lines.append(f"🕐 时辰: {getattr(result, 'shichen', '未知')}")
        lines.append(f"⚙️  马星冲墓空功能: {'开启' if self.config.auto_maxing_chong_mu_kong else '关闭'}")
        lines.append("")
        
        # 马星冲动分析
        maxing_targets = getattr(result, 'maxing_chongdong_targets', [])
        if maxing_targets:
            lines.append("⚡ 马星冲动信息:")
            lines.append(f"   找到目标数量: {len(maxing_targets)}")
            
            for i, target in enumerate(maxing_targets, 1):
                lines.append(f"   目标 {i}:")
                lines.append(f"     目标地支: {target.get('location_zhi', '未知')}")
                lines.append(f"     冲动类型: {target.get('type', '未知')}")
                lines.append(f"     标注文本: {target.get('text', '无')}")
            
            lines.append("")
            
            # 按地支分组分析所有目标位置的标注
            target_zhis = set(target.get('location_zhi') for target in maxing_targets)
            for target_zhi in sorted(target_zhis):
                # 找到该地支的所有目标
                zhi_targets = [t for t in maxing_targets if t.get('location_zhi') == target_zhi]
                
                lines.append(f"📍 {target_zhi}位标注分析 (有 {len(zhi_targets)} 个目标):")
                
                annotations = result.side_annotations.get(target_zhi, [])
                if annotations:
                    for i, anno in enumerate(annotations, 1):
                        anno_type = anno.get('type', '')
                        anno_text = anno.get('text', anno_type)
                        
                        # 测试匹配逻辑
                        is_match = self._test_maxing_match(anno, maxing_targets, target_zhi)
                        match_result = "✅ 匹配" if is_match else "❌ 不匹配"
                        style_effect = f"→ <s>{anno_text}</s>" if is_match else f"→ {anno_text}"
                        
                        lines.append(f"   {i}. {anno_type}: {anno_text}")
                        lines.append(f"      {match_result} {style_effect}")
                        
                        # 详细匹配分析
                        if is_match:
                            # 找出匹配的目标
                            matched_targets = []
                            for target in zhi_targets:
                                target_type = target.get('type', '')
                                if anno_type == target_type:
                                    matched_targets.append(f"直接匹配 {target_type}")
                                elif target_type == 'kongwang' and anno_type in ['shikong', 'rikong']:
                                    matched_targets.append(f"特殊映射 kongwang → {anno_type}")
                            lines.append(f"      匹配原因: {'; '.join(matched_targets)}")
                        else:
                            target_types = [t.get('type', '') for t in zhi_targets]
                            lines.append(f"      不匹配原因: {anno_type} 不在目标类型 {target_types} 中")
                        lines.append("")
                else:
                    lines.append("   ❌ 该位置无标注")
                    lines.append("")
                
        else:
            lines.append("❌ 本局无马星冲动")
            lines.append("")
        
        # 全盘标注概览
        lines.append("🗺️  全盘标注概览:")
        side_annotations = getattr(result, 'side_annotations', {})
        
        if side_annotations:
            dizhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
            for zhi in dizhi_order:
                if zhi in side_annotations:
                    annotations = side_annotations[zhi]
                    anno_texts = [anno.get('text', anno.get('type', '')) for anno in annotations]
                    
                    # 标记马星目标位置
                    target_zhis = set(t.get('location_zhi') for t in maxing_targets)
                    marker = " 🎯" if zhi in target_zhis else ""
                    lines.append(f"   {zhi}: {' '.join(anno_texts)}{marker}")
        else:
            lines.append("   ❌ 无侧方标注")
            
        lines.append("")
        
        # 配置信息
        lines.append("⚙️  当前配置:")
        lines.append(f"   月令自动填空: {getattr(self.config, 'auto_yue_ling_chong_kong', False)}")
        lines.append(f"   马星冲墓空: {self.config.auto_maxing_chong_mu_kong}")
        
        return "\n".join(lines)
        
    def _test_maxing_match(self, anno: dict, maxing_targets: list, dizhi: str) -> bool:
        """测试马星匹配逻辑 - 与ChartWidget中的逻辑保持一致，支持目标列表"""
        if not self.config.auto_maxing_chong_mu_kong:
            return False
            
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

def main():
    app = QApplication(sys.argv)
    
    window = MaxingInfoWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
