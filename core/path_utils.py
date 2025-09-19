#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
路径工具模块 - path_utils.py
处理应用程序的资源路径和用户数据路径
"""

import os
import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> str:
    """
    获取应用程序资源文件的绝对路径，兼容开发环境和PyInstaller打包环境
    用于只读的资源文件（如JSON数据文件、图标等）
    
    Args:
        relative_path: 相对于项目根目录的路径
        
    Returns:
        str: 资源文件的绝对路径
    """
    if getattr(sys, 'frozen', False):
        # 如果是打包后的应用程序，使用内部资源路径
        base_path = sys._MEIPASS
    else:
        # 开发环境，从项目根目录开始
        base_path = Path(__file__).parent.parent
    
    return os.path.join(base_path, relative_path)


def get_user_data_path(relative_path: str = "") -> str:
    """
    获取用户数据文件的绝对路径，用于可写的用户配置和数据文件
    
    在Windows下使用 %APPDATA%\\QiMenWorkbench\\
    在macOS下使用 ~/Library/Application Support/QiMenWorkbench/
    在Linux下使用 ~/.config/QiMenWorkbench/
    
    Args:
        relative_path: 相对于用户数据目录的路径（可选）
        
    Returns:
        str: 用户数据文件的绝对路径
    """
    if sys.platform == "win32":
        # Windows: 使用APPDATA目录
        base_path = os.path.join(os.getenv('APPDATA', ''), 'QiMenWorkbench')
    elif sys.platform == "darwin":
        # macOS: 使用Application Support目录
        base_path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'QiMenWorkbench')
    else:
        # Linux和其他Unix系统：使用.config目录
        base_path = os.path.join(os.path.expanduser('~'), '.config', 'QiMenWorkbench')
    
    # 确保目录存在
    os.makedirs(base_path, exist_ok=True)
    
    if relative_path:
        full_path = os.path.join(base_path, relative_path)
        # 确保父目录存在
        parent_dir = os.path.dirname(full_path)
        if parent_dir and parent_dir != base_path:
            os.makedirs(parent_dir, exist_ok=True)
        return full_path
    else:
        return base_path


def get_templates_file_path() -> str:
    """
    获取用户标注模板文件的路径
    
    Returns:
        str: templates.json文件的绝对路径
    """
    return get_user_data_path("templates.json")


def ensure_default_templates():
    """
    确保默认模板文件存在，如果不存在则从资源目录复制
    """
    user_templates_path = get_templates_file_path()
    
    # 如果用户目录没有模板文件，尝试从资源目录复制默认模板
    if not os.path.exists(user_templates_path):
        try:
            resource_templates_path = get_resource_path("data/templates.json")
            if os.path.exists(resource_templates_path):
                # 复制默认模板文件到用户目录
                import shutil
                shutil.copy2(resource_templates_path, user_templates_path)
                print(f"已复制默认模板文件到: {user_templates_path}")
            else:
                # 创建空的模板文件
                import json
                with open(user_templates_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
                print(f"已创建空模板文件: {user_templates_path}")
        except Exception as e:
            print(f"创建默认模板文件失败: {e}")


def migrate_templates_if_needed():
    """
    如果需要，将模板从旧位置（资源目录）迁移到新位置（用户数据目录）
    """
    user_templates_path = get_templates_file_path()
    resource_templates_path = get_resource_path("data/templates.json")
    
    # 如果用户数据目录没有模板文件，但资源目录有，则进行迁移
    if not os.path.exists(user_templates_path) and os.path.exists(resource_templates_path):
        try:
            import shutil
            shutil.copy2(resource_templates_path, user_templates_path)
            print(f"已迁移模板文件至用户数据目录: {user_templates_path}")
        except Exception as e:
            print(f"模板文件迁移失败: {e}")


if __name__ == "__main__":
    # 测试代码
    print("资源路径测试:")
    print(f"  data/core_parameters.json -> {get_resource_path('data/core_parameters.json')}")
    
    print("\\n用户数据路径测试:")
    print(f"  用户数据根目录 -> {get_user_data_path()}")
    print(f"  templates.json -> {get_templates_file_path()}")
    print(f"  用户配置文件 -> {get_user_data_path('config.json')}")