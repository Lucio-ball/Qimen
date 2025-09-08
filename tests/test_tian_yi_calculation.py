#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天乙计算逻辑的单元测试
FEAT-20250901-016 - 专家级数据模型升级
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.paipan_engine import PaiPanEngine

class TestTianYiCalculation(unittest.TestCase):
    """测试天乙计算功能"""
    
    def setUp(self):
        """设置测试用例"""
        self.engine = PaiPanEngine()
    
    def test_calculate_tian_yi_basic(self):
        """测试基本天乙计算逻辑"""
        # 模拟直符星数据
        zhi_fu_star = {'cn': '蓬', 'guxiang': 1}  # 蓬星故乡在1宫
        
        # 模拟天盘星布局
        tian_pan_stars = [
            [],  # 0宫（不使用）
            ['任'],  # 1宫：任星
            ['芮'],  # 2宫：芮星
            ['冲'],  # 3宫：冲星
            ['辅'],  # 4宫：辅星
            ['禽'],  # 5宫：禽星
            ['心'],  # 6宫：心星
            ['柱'],  # 7宫：柱星
            ['英'],  # 8宫：英星
            ['蓬']   # 9宫：蓬星
        ]
        
        # 调用天乙计算方法
        tian_yi = self.engine._calculate_tian_yi(zhi_fu_star, tian_pan_stars)
        
        # 验证结果
        self.assertEqual(tian_yi, '任', f"期望天乙为'任'，但得到'{tian_yi}'")
    
    def test_calculate_tian_yi_qin_star(self):
        """测试禽星作为直符的天乙计算"""
        # 禽星故乡在5宫
        zhi_fu_star = {'cn': '禽', 'guxiang': 5}
        
        tian_pan_stars = [
            [],  # 0宫（不使用）
            ['蓬'],  # 1宫
            ['芮'],  # 2宫
            ['冲'],  # 3宫
            ['辅'],  # 4宫
            ['英'],  # 5宫：英星（禽星故乡的天盘星）
            ['心'],  # 6宫
            ['柱'],  # 7宫
            ['任'],  # 8宫
            ['蓬']   # 9宫
        ]
        
        tian_yi = self.engine._calculate_tian_yi(zhi_fu_star, tian_pan_stars)
        self.assertEqual(tian_yi, '英', f"期望天乙为'英'，但得到'{tian_yi}'")
    
    def test_calculate_tian_yi_empty_palace(self):
        """测试故乡宫为空的情况"""
        zhi_fu_star = {'cn': '蓬', 'guxiang': 1}
        
        # 1宫为空
        tian_pan_stars = [
            [],  # 0宫（不使用）
            [],  # 1宫：空
            ['芮'],  # 2宫
            ['冲'],  # 3宫
            ['辅'],  # 4宫
            ['禽'],  # 5宫
            ['心'],  # 6宫
            ['柱'],  # 7宫
            ['英'],  # 8宫
            ['任']   # 9宫
        ]
        
        tian_yi = self.engine._calculate_tian_yi(zhi_fu_star, tian_pan_stars)
        self.assertEqual(tian_yi, '', f"故乡宫为空时天乙应为空字符串，但得到'{tian_yi}'")
    
    def test_calculate_tian_yi_invalid_guxiang(self):
        """测试无效故乡宫的情况"""
        zhi_fu_star = {'cn': '蓬', 'guxiang': 10}  # 无效的故乡宫
        
        tian_pan_stars = [[] for _ in range(10)]
        
        tian_yi = self.engine._calculate_tian_yi(zhi_fu_star, tian_pan_stars)
        self.assertEqual(tian_yi, '', f"无效故乡宫时天乙应为空字符串，但得到'{tian_yi}'")
    
    def test_calculate_tian_yi_missing_guxiang(self):
        """测试缺少故乡宫字段的情况"""
        zhi_fu_star = {'cn': '蓬'}  # 缺少guxiang字段
        
        tian_pan_stars = [
            [],  # 0宫（不使用）
            ['任'],  # 1宫
            ['芮'],  # 2宫
            ['冲'],  # 3宫
            ['辅'],  # 4宫
            ['禽'],  # 5宫：默认宫位
            ['心'],  # 6宫
            ['柱'],  # 7宫
            ['英'],  # 8宫
            ['蓬']   # 9宫
        ]
        
        tian_yi = self.engine._calculate_tian_yi(zhi_fu_star, tian_pan_stars)
        self.assertEqual(tian_yi, '禽', f"缺少故乡宫时应使用默认5宫，期望'禽'，但得到'{tian_yi}'")
    
    def test_real_paipan_tian_yi(self):
        """测试真实排盘中的天乙计算"""
        # 使用多个不同时间进行测试
        test_times = [
            "20250901153000",  # 2025年9月1日15:30
            "20250902080000",  # 2025年9月2日08:00
            "20250903120000",  # 2025年9月3日12:00
        ]
        
        valid_stars = ["蓬", "任", "冲", "辅", "英", "芮", "柱", "心", "禽"]
        
        for time_str in test_times:
            with self.subTest(time=time_str):
                result = self.engine.paipan(time_str)
                
                # 天乙不应为空
                self.assertIsNotNone(result.tian_yi, f"时间{time_str}的天乙不应为None")
                self.assertNotEqual(result.tian_yi, '', f"时间{time_str}的天乙不应为空字符串")
                
                # 天乙应该是有效的九星
                self.assertIn(result.tian_yi, valid_stars, 
                            f"时间{time_str}的天乙'{result.tian_yi}'应该是九星之一")
                
                # 验证天乙在索引中
                if 'jiuXing' in result.index and result.tian_yi in result.index['jiuXing']:
                    tian_yi_locations = result.index['jiuXing'][result.tian_yi]
                    self.assertGreater(len(tian_yi_locations), 0, 
                                     f"天乙'{result.tian_yi}'应该在索引中有位置记录")

    def test_tian_yi_consistency(self):
        """测试天乙计算的一致性"""
        # 同一时间多次排盘，天乙应该一致
        time_str = "20250901153000"
        
        results = []
        for _ in range(5):
            result = self.engine.paipan(time_str)
            results.append(result.tian_yi)
        
        # 所有结果应该相同
        first_tian_yi = results[0]
        for i, tian_yi in enumerate(results[1:], 1):
            self.assertEqual(tian_yi, first_tian_yi, 
                           f"第{i+1}次排盘的天乙'{tian_yi}'与第1次'{first_tian_yi}'不一致")

if __name__ == '__main__':
    unittest.main(verbosity=2)
