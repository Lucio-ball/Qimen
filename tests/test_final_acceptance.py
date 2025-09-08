#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FEAT-20250901-016 专家级数据模型升级 - 最终验收测试
验证所有需求是否已完全实现
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.paipan_engine import PaiPanEngine
from core.models import ChartResult, Palace

def acceptance_test_1_zhifu_rename():
    """验收标准1: data.json中的"值符"已更名为"直符" """
    print("🔍 验收测试1: 直符重命名")
    
    with open('data/core_parameters.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 检查八神中的直符
    zhifu_found = False
    zhifu_value = None
    for item in data['baShen']:
        if item['name'] == 'fu':
            zhifu_found = True
            zhifu_value = item['cn']
            break
    
    assert zhifu_found, "❌ 八神中未找到符头条目"
    assert zhifu_value == '直符', f"❌ 八神中符头的中文名应为'直符'，但是'{zhifu_value}'"
    
    # 确保没有"值符"残留
    for item in data['baShen']:
        assert item['cn'] != '值符', f"❌ 八神中不应包含'值符'，发现: {item}"
    
    print("✅ 通过: data.json中的'值符'已更名为'直符'")
    return True

def acceptance_test_2_palace_model():
    """验收标准2: core/models.py中的Palace类已按新结构更新"""
    print("\n🔍 验收测试2: Palace数据模型重构")
    
    palace = Palace(1)
    
    # 验证新属性存在
    required_new_attrs = [
        'zhi_fu', 'tian_pan_stars', 'tian_pan_gates', 'tian_pan_stems',
        'di_pan_stems', 'di_pan_star', 'di_pan_gate'
    ]
    
    for attr in required_new_attrs:
        assert hasattr(palace, attr), f"❌ Palace类缺少新属性: {attr}"
    
    # 验证向后兼容属性仍存在
    legacy_attrs = ['god', 'stars', 'gates', 'heaven_stems', 'earth_stems', 'original_star', 'original_gate']
    for attr in legacy_attrs:
        assert hasattr(palace, attr), f"❌ Palace类缺少向后兼容属性: {attr}"
    
    # 验证属性类型
    assert isinstance(palace.zhi_fu, str), "❌ zhi_fu应为字符串"
    assert isinstance(palace.tian_pan_stars, list), "❌ tian_pan_stars应为列表"
    assert isinstance(palace.tian_pan_gates, list), "❌ tian_pan_gates应为列表"
    assert isinstance(palace.tian_pan_stems, list), "❌ tian_pan_stems应为列表"
    assert isinstance(palace.di_pan_stems, list), "❌ di_pan_stems应为列表"
    assert isinstance(palace.di_pan_star, str), "❌ di_pan_star应为字符串"
    assert isinstance(palace.di_pan_gate, str), "❌ di_pan_gate应为字符串"
    
    print("✅ 通过: Palace类已按新结构更新，包含所需的新属性和向后兼容性")
    return True

def acceptance_test_3_chart_result_model():
    """验收标准3: ChartResult已扩展以存储"天乙"信息和索引"""
    print("\n🔍 验收测试3: ChartResult数据模型扩展")
    
    result = ChartResult()
    
    # 验证新属性
    assert hasattr(result, 'tian_yi'), "❌ ChartResult缺少tian_yi属性"
    assert hasattr(result, 'index'), "❌ ChartResult缺少index属性"
    assert hasattr(result, '_build_index'), "❌ ChartResult缺少_build_index方法"
    
    # 验证属性类型
    assert isinstance(result.tian_yi, str), "❌ tian_yi应为字符串"
    assert isinstance(result.index, dict), "❌ index应为字典"
    
    # 验证_build_index方法功能
    # 添加一些测试数据
    result.palaces[1].zhi_fu = "直符"
    result.palaces[1].tian_pan_stars = ["蓬"]
    result.palaces[1].di_pan_star = "蓬"
    
    # 调用索引构建
    index = result._build_index()
    assert isinstance(index, dict), "❌ _build_index应返回字典"
    assert 'baShen' in index, "❌ 索引应包含baShen"
    assert 'jiuXing' in index, "❌ 索引应包含jiuXing"
    
    print("✅ 通过: ChartResult已扩展，包含天乙信息和反向查询索引")
    return True

def acceptance_test_4_paipan_engine():
    """验收标准4: PaiPanEngine能计算并填充所有新数据字段"""
    print("\n🔍 验收测试4: PaiPanEngine升级验证")
    
    engine = PaiPanEngine()
    
    # 进行排盘测试
    test_time = "20250901153000"
    result = engine.paipan(test_time)
    
    # 验证基本结构
    assert isinstance(result, ChartResult), "❌ 排盘应返回ChartResult对象"
    
    # 验证天乙计算
    assert result.tian_yi != "", "❌ 天乙不应为空"
    valid_stars = ["蓬", "任", "冲", "辅", "英", "芮", "柱", "心", "禽"]
    assert result.tian_yi in valid_stars, f"❌ 天乙'{result.tian_yi}'应为九星之一"
    
    # 验证新数据字段填充
    for i in range(1, 10):
        palace = result.palaces[i]
        
        # 检查新属性是否被填充
        assert isinstance(palace.zhi_fu, str), f"❌ 宫{i}的zhi_fu应为字符串"
        assert isinstance(palace.tian_pan_stars, list), f"❌ 宫{i}的tian_pan_stars应为列表"
        assert isinstance(palace.tian_pan_gates, list), f"❌ 宫{i}的tian_pan_gates应为列表"
        assert isinstance(palace.di_pan_star, str), f"❌ 宫{i}的di_pan_star应为字符串"
        assert isinstance(palace.di_pan_gate, str), f"❌ 宫{i}的di_pan_gate应为字符串"
        
        # 检查向后兼容属性是否同步
        assert palace.god == palace.zhi_fu, f"❌ 宫{i}的god应与zhi_fu同步"
        assert palace.original_star == palace.di_pan_star, f"❌ 宫{i}的original_star应与di_pan_star同步"
    
    # 验证直符而非值符
    assert "值符" not in result.zhi_fu, f"❌ 直符字段不应包含'值符'，但得到'{result.zhi_fu}'"
    
    print("✅ 通过: PaiPanEngine能成功排盘并填充所有新数据字段")
    return True

def acceptance_test_5_index_content():
    """验收标准5: ChartResult.index包含正确的参数位置信息"""
    print("\n🔍 验收测试5: 反向查询索引内容验证")
    
    engine = PaiPanEngine()
    result = engine.paipan("20250901153000")
    
    # 验证索引结构
    assert isinstance(result.index, dict), "❌ 索引应为字典"
    
    expected_param_types = ['baShen', 'jiuXing', 'baMen', 'tianGan']
    for param_type in expected_param_types:
        assert param_type in result.index, f"❌ 索引应包含参数类型: {param_type}"
        assert isinstance(result.index[param_type], dict), f"❌ {param_type}应为字典"
    
    # 验证索引内容的完整性
    all_location_objects = []
    for param_type, params in result.index.items():
        for param_name, locations in params.items():
            assert isinstance(locations, list), f"❌ {param_type}.{param_name}应为列表"
            for location in locations:
                # 验证location对象结构
                required_fields = ['palace_index', 'param_type', 'text', 'id']
                for field in required_fields:
                    assert field in location, f"❌ location对象缺少字段: {field}"
                
                # 验证palace_index范围
                assert 1 <= location['palace_index'] <= 9, f"❌ palace_index应在1-9范围内: {location['palace_index']}"
                
                # 验证ID唯一性
                assert location['id'] not in [obj['id'] for obj in all_location_objects], f"❌ ID重复: {location['id']}"
                all_location_objects.append(location)
    
    # 验证索引数量合理性（应该有足够的参数）
    total_locations = len(all_location_objects)
    assert total_locations >= 36, f"❌ 索引位置数量过少: {total_locations}，期望至少36个"  # 9宫 * 4类参数最少
    
    print(f"✅ 通过: 反向查询索引包含{total_locations}个正确的参数位置信息")
    return True

def main():
    """执行完整的验收测试"""
    print("开始FEAT-20250901-016专家级数据模型升级验收测试")
    print("=" * 70)
    
    tests = [
        acceptance_test_1_zhifu_rename,
        acceptance_test_2_palace_model,
        acceptance_test_3_chart_result_model,
        acceptance_test_4_paipan_engine,
        acceptance_test_5_index_content
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
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"验收测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有验收标准通过！FEAT-20250901-016专家级数据模型升级完成！")
        print("\n✨ 完成功能总结:")
        print("   ✅ 直符重命名：data.json中'值符'已更名为'直符'")
        print("   ✅ Palace重构：明确区分天地盘的星、门、干")
        print("   ✅ ChartResult扩展：新增天乙信息和反向查询索引")
        print("   ✅ PaiPanEngine升级：计算并填充所有新数据字段")
        print("   ✅ 索引系统：_build_index方法生成完整的参数位置索引")
        print("   ✅ 向后兼容：保留原有属性名，确保现有代码正常工作")
        return True
    else:
        print("❌ 部分验收标准未通过，需要修复问题")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
