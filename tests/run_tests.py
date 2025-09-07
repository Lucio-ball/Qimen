#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奇门遁甲工作台测试运行器
运行所有测试用例
"""

import os
import sys
import subprocess
from pathlib import Path

def run_all_tests():
    """运行所有测试"""
    tests_dir = Path(__file__).parent
    test_files = [
        "test_expert_model_upgrade.py",
        "test_chart_result_index.py", 
        "test_tian_yi_calculation.py",
        "test_final_acceptance.py"
    ]
    
    print("🧪 开始运行奇门遁甲工作台测试套件")
    print("=" * 60)
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        test_path = tests_dir / test_file
        if test_path.exists():
            print(f"\n🔍 运行测试: {test_file}")
            print("-" * 40)
            
            try:
                # 运行测试
                result = subprocess.run([
                    sys.executable, str(test_path)
                ], capture_output=True, text=True, cwd=tests_dir.parent)
                
                if result.returncode == 0:
                    print("✅ 测试通过")
                    passed += 1
                else:
                    print("❌ 测试失败")
                    print("错误输出:")
                    print(result.stderr)
                    
            except Exception as e:
                print(f"❌ 测试执行异常: {e}")
        else:
            print(f"⚠️ 测试文件不存在: {test_file}")
    
    print("\n" + "=" * 60)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
