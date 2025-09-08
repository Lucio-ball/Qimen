#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FEAT-20250901-016 - 专家级数据模型升级测试
测试新的Palace和ChartResult数据模型
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.paipan_engine import PaiPanEngine
from core.models import ChartResult, Palace

def test_zhifu_rename():
    """测试直符重命名"""
    print("=== 测试1：直符重命名 ===")
    
    # 测试data.json中的直符
    with open('data/core_parameters.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    zhifu_entry = next((item for item in data['baShen'] if item['name'] == 'fu'), None)
    if zhifu_entry:
        print(f"✅ 八神中的直符：{zhifu_entry['cn']}")
        assert zhifu_entry['cn'] == '直符', f"期望'直符'，但得到'{zhifu_entry['cn']}'"
    else:
        print("❌ 未找到直符条目")
        return False
    
    return True

def test_palace_model():
    """测试Palace新数据模型"""
    print("\n=== 测试2：Palace数据模型 ===")
    
    palace = Palace(1)
    
    # 测试新属性
    palace.zhi_fu = "直符"
    palace.tian_pan_stars = ["蓬", "任"]
    palace.tian_pan_gates = ["开"]
    palace.tian_pan_stems = ["甲", "乙"]
    palace.di_pan_stems = ["戊"]
    palace.di_pan_star = "蓬"
    palace.di_pan_gate = "休"
    
    # 检查新属性
    assert palace.zhi_fu == "直符", f"期望'直符'，但得到'{palace.zhi_fu}'"
    assert palace.tian_pan_stars == ["蓬", "任"], f"期望['蓬', '任']，但得到{palace.tian_pan_stars}"
    assert palace.di_pan_star == "蓬", f"期望'蓬'，但得到'{palace.di_pan_star}'"
    
    print("✅ Palace新属性测试通过")
    
    # 测试向后兼容属性
    print(f"   向后兼容 - god: {palace.god}")
    print(f"   向后兼容 - stars: {palace.stars}")
    print(f"   向后兼容 - original_star: {palace.original_star}")
    
    return True

def test_chart_result_index():
    """测试ChartResult的索引功能"""
    print("\n=== 测试3：ChartResult索引功能 ===")
    
    result = ChartResult()
    
    # 模拟填充数据
    result.palaces[1].zhi_fu = "直符"
    result.palaces[1].tian_pan_stars = ["蓬"]
    result.palaces[1].tian_pan_gates = ["开"]
    result.palaces[1].tian_pan_stems = ["甲"]
    result.palaces[1].di_pan_stems = ["戊"]
    result.palaces[1].di_pan_star = "蓬"
    result.palaces[1].di_pan_gate = "休"
    
    result.palaces[2].zhi_fu = "螣蛇"
    result.palaces[2].tian_pan_stars = ["任"]
    result.palaces[2].di_pan_star = "芮"
    
    # 构建索引
    index = result._build_index()
    
    print("✅ 索引构建完成")
    print(f"   索引键: {list(index.keys())}")
    
    # 测试索引内容
    if 'baShen' in index and '直符' in index['baShen']:
        zhifu_locations = index['baShen']['直符']
        print(f"   直符位置: 宫{zhifu_locations[0]['palace_index']}")
        assert zhifu_locations[0]['palace_index'] == 1, "直符应该在1宫"
    
    if 'jiuXing' in index and '蓬' in index['jiuXing']:
        peng_locations = index['jiuXing']['蓬']
        print(f"   蓬星出现次数: {len(peng_locations)}")
        print(f"   蓬星位置: {[loc['palace_index'] for loc in peng_locations]}")
    
    return True

def test_paipan_engine():
    """测试排盘引擎升级"""
    print("\n=== 测试4：排盘引擎升级 ===")
    
    try:
        engine = PaiPanEngine()
        
        # 排盘测试
        test_time = "20250901153000"  # 2025年9月1日15:30:00
        result = engine.paipan(test_time)
        
        print("✅ 排盘执行成功")
        print(f"   直符: {result.zhi_fu}")
        print(f"   值使: {result.zhi_shi}")
        print(f"   天乙: {result.tian_yi}")
        
        # 检查新数据模型
        palace_1 = result.palaces[1]
        print(f"   1宫 - 八神: {palace_1.zhi_fu}")
        print(f"   1宫 - 天盘星: {palace_1.tian_pan_stars}")
        print(f"   1宫 - 地盘星: {palace_1.di_pan_star}")
        
        # 检查索引
        print(f"   索引键数量: {len(result.index)}")
        print(f"   索引包含的参数类型: {list(result.index.keys())}")
        
        # 验证直符不再是"值符"
        assert "值符" not in result.zhi_fu, f"直符字段不应包含'值符'，但得到'{result.zhi_fu}'"
        
        return True
        
    except Exception as e:
        print(f"❌ 排盘引擎测试失败: {e}")
        return False

def test_tian_yi_calculation():
    """测试天乙计算"""
    print("\n=== 测试5：天乙计算 ===")
    
    try:
        engine = PaiPanEngine()
        result = engine.paipan("20250901153000")
        
        if result.tian_yi:
            print(f"✅ 天乙计算成功: {result.tian_yi}")
            
            # 验证天乙是九星之一
            valid_stars = ["蓬", "任", "冲", "辅", "英", "芮", "柱", "心", "禽"]
            assert result.tian_yi in valid_stars, f"天乙'{result.tian_yi}'应该是九星之一"
            
            return True
        else:
            print("⚠️ 天乙为空，可能是计算逻辑问题")
            return False
            
    except Exception as e:
        print(f"❌ 天乙计算测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始FEAT-20250901-016专家级数据模型升级测试")
    print("=" * 60)
    
    tests = [
        test_zhifu_rename,
        test_palace_model, 
        test_chart_result_index,
        test_paipan_engine,
        test_tian_yi_calculation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} 失败")
        except Exception as e:
            print(f"❌ {test.__name__} 出现异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！专家级数据模型升级成功！")
        return True
    else:
        print("❌ 部分测试失败，需要修复问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
