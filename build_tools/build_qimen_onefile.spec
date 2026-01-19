# -*- mode: python ; coding: utf-8 -*-
"""\
奇门遁甲工作台 PyInstaller配置文件
用于将Python应用程序打包为单文件可执行版本（推荐发布用）

生成产物：dist/奇门遁甲工作台_v1.2.5.exe
"""

import os

# 获取项目根目录 - 硬编码路径以避免路径问题
project_root = r'C:\Users\Crazy\OneDrive\github\Qimen'

app_version = 'v1.2.5'
app_release = 'RELEASE-20260119-001'
app_name = f'奇门遁甲工作台_{app_version}'

# 分析主脚本
a = Analysis(
    [os.path.join(project_root, 'run_gui.py')],
    pathex=[
        project_root,
        os.path.join(project_root, 'core'),
        os.path.join(project_root, 'ui'),
    ],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'data', 'core_parameters.json'), 'data'),
        (os.path.join(project_root, 'data', 'templates.json'), 'data'),
        (os.path.join(project_root, 'data', 'data.json'), 'data'),
        (os.path.join(project_root, 'core'), 'core'),
        (os.path.join(project_root, 'ui'), 'ui'),
        (os.path.join(project_root, 'qimen_cases.db'), '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtUiTools',

        'core.paipan_engine',
        'core.models',
        'core.data_manager',
        'core.calendar_utils',
        'core.config_manager',
        'core.workspace_manager',

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

        'sqlite3',
        'json',
        'datetime',
        'typing',
        'uuid',
        'calendar',
        're',

        # 节气天文历算
        'sxtwl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
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

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
