#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChartResult._build_index 方法的单元测试
FEAT-20250901-016 - 专家级数据模型升级
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import ChartResult, Palace

class TestChartResultIndex(unittest.TestCase):
    """测试ChartResult的索引构建功能"""
    
    def setUp(self):
        """设置测试用例"""
        self.result = ChartResult()
        
        # 模拟填充测试数据
        # 1宫：直符，天蓬星，开门，甲，戊
        self.result.palaces[1].zhi_fu = "直符"
        self.result.palaces[1].tian_pan_stars = ["蓬"]
        self.result.palaces[1].tian_pan_gates = ["开"]
        self.result.palaces[1].tian_pan_stems = ["甲"]
        self.result.palaces[1].di_pan_stems = ["戊"]
        self.result.palaces[1].di_pan_star = "蓬"
        self.result.palaces[1].di_pan_gate = "休"
        
        # 2宫：螣蛇，天任星，休门，乙，己
        self.result.palaces[2].zhi_fu = "螣蛇"
        self.result.palaces[2].tian_pan_stars = ["任"]
        self.result.palaces[2].tian_pan_gates = ["休"]
        self.result.palaces[2].tian_pan_stems = ["乙"]
        self.result.palaces[2].di_pan_stems = ["己"]
        self.result.palaces[2].di_pan_star = "芮"
        self.result.palaces[2].di_pan_gate = "生"
        
        # 3宫：太阴，多个天盘星，多个天盘干
        self.result.palaces[3].zhi_fu = "太阴"
        self.result.palaces[3].tian_pan_stars = ["冲", "辅"]
        self.result.palaces[3].tian_pan_gates = ["伤", "杜"]
        self.result.palaces[3].tian_pan_stems = ["丙", "丁"]
        self.result.palaces[3].di_pan_stems = ["庚"]
        self.result.palaces[3].di_pan_star = "冲"
        self.result.palaces[3].di_pan_gate = "伤"

    def test_index_structure(self):
        """测试索引的基本结构"""
        index = self.result._build_index()
        
        # 检查顶级键
        expected_keys = ['baShen', 'jiuXing', 'baMen', 'tianGan']
        for key in expected_keys:
            self.assertIn(key, index, f"索引应包含键'{key}'")
    
    def test_ba_shen_index(self):
        """测试八神索引"""
        index = self.result._build_index()
        ba_shen = index['baShen']
        
        # 检查直符
        self.assertIn('直符', ba_shen, "应包含直符")
        zhifu_locations = ba_shen['直符']
        self.assertEqual(len(zhifu_locations), 1, "直符应该只出现一次")
        self.assertEqual(zhifu_locations[0]['palace_index'], 1, "直符应在1宫")
        self.assertEqual(zhifu_locations[0]['param_type'], 'baShen', "参数类型应为baShen")
        self.assertEqual(zhifu_locations[0]['text'], '直符', "文本应为'直符'")
        self.assertEqual(zhifu_locations[0]['id'], 'palace_1_zhi_fu', "ID应正确")
        
        # 检查螣蛇
        self.assertIn('螣蛇', ba_shen, "应包含螣蛇")
        she_locations = ba_shen['螣蛇']
        self.assertEqual(len(she_locations), 1, "螣蛇应该只出现一次")
        self.assertEqual(she_locations[0]['palace_index'], 2, "螣蛇应在2宫")
        
        # 检查太阴
        self.assertIn('太阴', ba_shen, "应包含太阴")
        yin_locations = ba_shen['太阴']
        self.assertEqual(len(yin_locations), 1, "太阴应该只出现一次")
        self.assertEqual(yin_locations[0]['palace_index'], 3, "太阴应在3宫")

    def test_jiu_xing_index(self):
        """测试九星索引"""
        index = self.result._build_index()
        jiu_xing = index['jiuXing']
        
        # 检查蓬星（应该出现在天盘和地盘）
        self.assertIn('蓬', jiu_xing, "应包含蓬星")
        peng_locations = jiu_xing['蓬']
        self.assertEqual(len(peng_locations), 2, "蓬星应该出现2次（天盘+地盘）")
        
        # 找到天盘蓬和地盘蓬
        tian_pan_peng = next((loc for loc in peng_locations if loc['attribute_name'] == 'tian_pan_stars'), None)
        di_pan_peng = next((loc for loc in peng_locations if loc['attribute_name'] == 'di_pan_star'), None)
        
        self.assertIsNotNone(tian_pan_peng, "应有天盘蓬星")
        self.assertIsNotNone(di_pan_peng, "应有地盘蓬星")
        self.assertEqual(tian_pan_peng['palace_index'], 1, "天盘蓬星在1宫")
        self.assertEqual(di_pan_peng['palace_index'], 1, "地盘蓬星在1宫")
        
        # 检查任星
        self.assertIn('任', jiu_xing, "应包含任星")
        ren_locations = jiu_xing['任']
        self.assertEqual(len(ren_locations), 1, "任星应该出现1次")
        self.assertEqual(ren_locations[0]['palace_index'], 2, "任星应在2宫")

    def test_ba_men_index(self):
        """测试八门索引"""
        index = self.result._build_index()
        ba_men = index['baMen']
        
        # 检查开门
        self.assertIn('开', ba_men, "应包含开门")
        kai_locations = ba_men['开']
        self.assertEqual(len(kai_locations), 1, "开门应该出现1次")
        self.assertEqual(kai_locations[0]['palace_index'], 1, "开门应在1宫")
        
        # 检查休门
        self.assertIn('休', ba_men, "应包含休门")
        xiu_locations = ba_men['休']
        # 休门可能在天盘门和地盘门都出现
        self.assertGreaterEqual(len(xiu_locations), 1, "休门至少出现1次")

    def test_tian_gan_index(self):
        """测试天干索引"""
        index = self.result._build_index()
        tian_gan = index['tianGan']
        
        # 检查甲
        self.assertIn('甲', tian_gan, "应包含甲")
        jia_locations = tian_gan['甲']
        self.assertEqual(len(jia_locations), 1, "甲应该出现1次")
        self.assertEqual(jia_locations[0]['palace_index'], 1, "甲应在1宫")
        self.assertEqual(jia_locations[0]['attribute_name'], 'tian_pan_stems', "甲应为天盘干")
        
        # 检查戊
        self.assertIn('戊', tian_gan, "应包含戊")
        wu_locations = tian_gan['戊']
        self.assertEqual(len(wu_locations), 1, "戊应该出现1次")
        self.assertEqual(wu_locations[0]['palace_index'], 1, "戊应在1宫")
        self.assertEqual(wu_locations[0]['attribute_name'], 'di_pan_stems', "戊应为地盘干")

    def test_multiple_items_index(self):
        """测试多个项目的索引"""
        index = self.result._build_index()
        
        # 检查3宫的多个天盘星
        jiu_xing = index['jiuXing']
        
        # 冲星
        self.assertIn('冲', jiu_xing, "应包含冲星")
        chong_locations = jiu_xing['冲']
        # 冲星可能在天盘和地盘都出现
        chong_tian_pan = next((loc for loc in chong_locations if loc['attribute_name'] == 'tian_pan_stars'), None)
        self.assertIsNotNone(chong_tian_pan, "应有天盘冲星")
        self.assertEqual(chong_tian_pan['palace_index'], 3, "天盘冲星在3宫")
        self.assertIn('sub_index', chong_tian_pan, "多项目应有sub_index")
        
        # 辅星
        self.assertIn('辅', jiu_xing, "应包含辅星")
        fu_locations = jiu_xing['辅']
        fu_tian_pan = next((loc for loc in fu_locations if loc['attribute_name'] == 'tian_pan_stars'), None)
        self.assertIsNotNone(fu_tian_pan, "应有天盘辅星")
        self.assertEqual(fu_tian_pan['palace_index'], 3, "天盘辅星在3宫")

    def test_unique_ids(self):
        """测试ID的唯一性"""
        index = self.result._build_index()
        
        all_ids = []
        for param_type in index.values():
            for param_name in param_type.values():
                for location in param_name:
                    all_ids.append(location['id'])
        
        # 检查ID唯一性
        unique_ids = set(all_ids)
        self.assertEqual(len(all_ids), len(unique_ids), "所有ID应该是唯一的")
        
        # 检查ID格式
        for id_str in all_ids:
            self.assertTrue(id_str.startswith('palace_'), f"ID '{id_str}' 应以'palace_'开头")
            parts = id_str.split('_')
            self.assertGreaterEqual(len(parts), 3, f"ID '{id_str}' 格式不正确")

    def test_empty_palace(self):
        """测试空宫位的处理"""
        # 创建一个基本上空的ChartResult
        empty_result = ChartResult()
        index = empty_result._build_index()
        
        # 应该有空的索引结构
        self.assertIsInstance(index, dict, "索引应该是字典")
        
        # 所有参数类型的值应该是空的或很少
        for param_type, params in index.items():
            for param_name, locations in params.items():
                self.assertIsInstance(locations, list, f"{param_type}.{param_name} 应该是列表")

if __name__ == '__main__':
    unittest.main(verbosity=2)
