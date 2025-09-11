# 奇门遁甲工作台 - 项目文件结构

## 📁 项目根目录结构

```
Qimen/
├── 📁 build_tools/          # 构建工具和配置
│   ├── build_qimen.spec     # PyInstaller 打包配置
│   └── clean_debug_prints.py # 调试信息清理工具
├── 📁 core/                 # 核心业务逻辑
│   ├── __init__.py
│   ├── calendar_utils.py    # 日历工具
│   ├── config_manager.py    # 配置管理
│   ├── data_manager.py      # 数据管理
│   ├── models.py            # 数据模型
│   ├── paipan_engine.py     # 排盘引擎
│   └── workspace_manager.py # 工作区管理
├── 📁 data/                 # 数据文件
│   ├── core_parameters.json # 核心参数配置
│   └── templates.json       # 模板数据
├── 📁 dist/                 # 打包输出目录
│   ├── 奇门遁甲工作台/       # 文件夹版本
│   └── 奇门遁甲工作台.exe    # 单文件版本
├── 📁 docs/                 # 项目文档
│   ├── 📁 architecture/     # 架构设计文档
│   ├── 📁 bugfixes/         # 问题修复报告
│   ├── 📁 features/         # 功能开发报告
│   ├── 📁 guides/           # 使用指南
│   ├── 📁 releases/         # 发布说明
│   ├── CHART_WIDGET_README.md
│   ├── PALACE_WIDGET_README.md
│   ├── PARAMETER_WIDGET_README.md
│   ├── README.md
│   └── VIEW_MENU_功能说明.md
├── 📁 ui/                   # 用户界面
│   ├── __init__.py
│   ├── app_integrated.py    # 应用程序入口
│   ├── config.py            # UI配置
│   ├── 📁 assets/           # 资源文件
│   ├── 📁 dialogs/          # 对话框
│   ├── 📁 generated/        # 自动生成的UI文件
│   ├── 📁 views/            # 视图文件
│   ├── 📁 widgets/          # 自定义控件
│   └── 📁 windows/          # 窗口
├── .gitignore               # Git忽略规则
├── qimen_cases.db          # 案例数据库
├── README.md               # 项目说明
├── requirements.txt        # Python依赖
└── run_gui.py             # 主程序启动器
```

## 📊 文件分类说明

### 🔧 核心模块 (core/)
- **paipan_engine.py**: 奇门遁甲排盘核心算法
- **models.py**: 数据模型定义
- **data_manager.py**: 数据持久化管理
- **calendar_utils.py**: 农历日历工具
- **config_manager.py**: 应用配置管理
- **workspace_manager.py**: 工作区文件管理

### 🎨 用户界面 (ui/)
- **windows/**: 主窗口和子窗口
- **widgets/**: 自定义控件（排盘图、宫位、参数面板等）
- **dialogs/**: 对话框（首选项、模板管理、关于等）
- **views/**: Qt Designer设计的UI文件
- **assets/**: 样式表、图标等资源

### 📚 文档系统 (docs/)
- **architecture/**: 系统架构设计文档
- **features/**: 功能开发完成报告
- **bugfixes/**: 问题修复报告
- **guides/**: 用户使用指南
- **releases/**: 版本发布说明

### 🛠️ 构建工具 (build_tools/)
- **build_qimen.spec**: PyInstaller打包配置
- **clean_debug_prints.py**: 代码清理工具

### 📦 输出目录 (dist/)
- **奇门遁甲工作台.exe**: 单文件可执行程序
- **奇门遁甲工作台/**: 文件夹形式的分发版本

## 🚀 快速开始

### 开发环境运行
```bash
python run_gui.py
```

### 打包应用程序
```bash
cd build_tools
python -m PyInstaller build_qimen.spec
```

### 清理构建文件
```bash
python build_tools/clean_debug_prints.py
```

## 📝 版本信息

- **当前版本**: v1.0 alpha
- **Python版本**: 3.12.6
- **UI框架**: PySide6
- **打包工具**: PyInstaller 6.15.0

## 🔄 文件维护

### 自动清理的文件
- `__pycache__/` - Python缓存目录
- `build/` - 构建临时文件
- `*.pyc` - Python编译文件

### 版本控制忽略
参见 `.gitignore` 文件配置

---

**最后更新**: 2025年9月10日  
**整理人**: GitHub Copilot
