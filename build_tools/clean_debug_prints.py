#!/usr/bin/env python3
"""
代码清理脚本 - 移除调试用的print语句
用于v1.0 alpha发布前的代码清理
"""

import os
import re

def clean_debug_prints(file_path):
    """清理文件中的调试print语句"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 要清理的print语句模式
    patterns_to_clean = [
        r'print\(f?"模板已应用.*?\)\n',
        r'print\("图层状态已变化"\)\n',
        r'print\(f?"没有激活的案例.*?\)\n',
        r'print\(f?"案例对象为空.*?\)\n',
        r'print\(f?"模板文件不存在.*?\)\n',
        r'print\(f?"模板.*?不存在"\)\n',
        r'print\("没有激活的图层"\)\n',
        r'print\(f?"成功应用模板.*?\)\n',
        r'print\(f?"模板.*?没有找到匹配的参数"\)\n',
        r'print\(f?"查找特殊参数.*?\)\n',
        r'print\(f?"  找到位置.*?\)\n',
        r'print\(f?"首选项设置已.*?\)\n',
        r'print\(f?"所有配置已应用"\)\n',
        # 工作区管理器测试相关
        r'print\("=== 工作区管理器测试 ==="\)\n',
        r'print\(f?"测试目录:.*?\)\n',
        r'print\(f?"设置工作区:.*?\)\n',
        r'print\(f?"扫描到的.qmw文件:.*?\)\n',
        r'print\(f?"  .*?\)\n',
        r'print\(f?"工作区验证:.*?\)\n',
        r'print\("工作区管理器测试完成 ✓"\)\n',
    ]
    
    # 应用所有模式清理
    for pattern in patterns_to_clean:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # 清理空行
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """主函数"""
    files_to_clean = [
        'ui/windows/integrated_main_window.py',
        'core/workspace_manager.py',
    ]
    
    cleaned_files = []
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            if clean_debug_prints(file_path):
                cleaned_files.append(file_path)
                print(f"已清理: {file_path}")
            else:
                print(f"无需清理: {file_path}")
        else:
            print(f"文件不存在: {file_path}")
    
    print(f"\n清理完成，共处理了 {len(cleaned_files)} 个文件")

if __name__ == "__main__":
    main()
