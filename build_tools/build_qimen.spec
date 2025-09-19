# -*- mode: python ; coding: utf-8 -*-
"""
奇门遁甲工作台 v1.0 alpha PyInstaller配置文件
用于将Python应用程序打包为独立的可执行文件
"""

import os
import sys

# 获取项目根目录 - 硬编码路径以避免路径问题
project_root = r'C:\Users\Crazy\OneDrive\github\Qimen'

# 分析主脚本
a = Analysis(
    [os.path.join(project_root, 'run_gui.py')],  # 主入口文件
    pathex=[
        project_root,  # 项目根目录
        os.path.join(project_root, 'core'),  # 核心模块目录
        os.path.join(project_root, 'ui'),    # UI模块目录
    ],
    binaries=[],
    datas=[
        # 数据文件
        (os.path.join(project_root, 'data', 'core_parameters.json'), 'data'),
        (os.path.join(project_root, 'data', 'templates.json'), 'data'),
        (os.path.join(project_root, 'data', 'data.json'), 'data'),  # 参数状态数据文件
        
        # 添加整个core包
        (os.path.join(project_root, 'core'), 'core'),
        
        # 添加整个ui包
        (os.path.join(project_root, 'ui'), 'ui'),
        
        # 如果有其他资源文件也需要包含
        (os.path.join(project_root, 'qimen_cases.db'), '.'),  # 示例数据库文件
    ],
    hiddenimports=[
        # PySide6相关模块
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.QtUiTools',
        
        # 项目核心模块
        'core.paipan_engine',
        'core.models',
        'core.data_manager',
        'core.calendar_utils',
        'core.config_manager',
        'core.workspace_manager',
        
        # UI模块
        'ui.app_integrated',
        'ui.windows.integrated_main_window',
        'ui.widgets.chart_widget',
        'ui.widgets.palace_widget',
        'ui.widgets.parameter_widget',
        'ui.widgets.query_widget',
        'ui.widgets.case_browser_widget',
        'ui.widgets.annotation_panel_widget',
        'ui.widgets.attribute_panel_widget',
        'ui.widgets.welcome_widget',
        'ui.widgets.central_widget',
        'ui.dialogs.preferences_dialog',
        'ui.dialogs.case_info_dialog',
        'ui.dialogs.template_manager_dialog',
        'ui.dialogs.about_dialog',
        
        # 标准库模块
        'sqlite3',
        'json',
        'datetime',
        'typing',
        'uuid',
        'calendar',
        're',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        'tkinter',
        'matplotlib',
        'pandas',
        'numpy',
        'scipy',
        'IPython',
        'jupyter',
        'pytest',
        'unittest',
    ],
    noarchive=False,
)

# 编译PYZ文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='奇门遁甲工作台',  # 可执行文件名称
    debug=False,  # 不包含调试信息
    bootloader_ignore_signals=False,
    strip=False,  # 不去除符号信息
    upx=True,  # 启用UPX压缩以减小文件大小
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='ui/assets/icons/app_icon.ico',  # 如果有图标文件的话
)

# 创建分发目录
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='奇门遁甲工作台'
)
