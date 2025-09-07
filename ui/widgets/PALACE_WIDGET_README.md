# PalaceWidget 组件文档

## 项目信息

- **项目代号**: QMW-CoreUI (Qi Men Workbench - Core UI)
- **任务ID**: UI-20250901-006
- **组件名称**: PalaceWidget
- **依赖组件**: ParameterWidget, DisplayConfig

## 概述

PalaceWidget 是奇门遁甲工作台的核心复合组件，基于已完成的ParameterWidget构建，用于显示完整的单个宫位信息。它内部管理9个ParameterWidget的布局和数据分发，能够根据传入的Palace数据对象自动将正确的信息分发给对应的ParameterWidget进行渲染。

## 文件结构

```
ui/widgets/
├── palace_widget.py                   # PalaceWidget主体实现
├── demo_palace_integration.py         # 完整九宫格集成演示
├── parameter_widget.py                # 基础依赖组件（已完成）
└── PALACE_WIDGET_README.md           # 本文档
```

## 核心特性

### 1. 容器组件架构
- 继承自 QWidget，内部使用 QGridLayout 管理 3x3 布局
- 包含9个 ParameterWidget 实例，按九宫格位置放置
- 纯容器职责，所有绘制委托给子组件

### 2. 智能数据分发
- 通过 `update_data` 方法接收 Palace、ChartResult 等数据
- 自动分析数据类型和宫位特性
- 将正确信息分发到对应的 ParameterWidget 位置

### 3. 中宫特殊处理
- 检测 `palace_data.index == 5` 识别中宫
- 中宫显示局数信息和地盘干
- 普通宫位显示完整的八神、九星、八门、天盘干、地盘干

### 4. 五行颜色管理
- 内置五行颜色映射系统
- 从 global_data 查询参数五行属性
- 安全的颜色查询机制，防止数据缺失崩溃

### 5. 值符值使识别
- 自动识别值符、值使并设置加粗显示
- **值符星**（九星）加粗：检查 `chart_data.zhi_fu in palace_data.stars`
- **值使门**（八门）加粗：检查 `palace_data.gates == chart_data.zhi_shi`  
- **注意**：八神中的"值符"本身不加粗，只有对应的九星加粗

## API 接口设计

### 类定义

```python
class PalaceWidget(QWidget):
    def __init__(self, global_data: dict, parent=None)
    def update_data(self, palace_data: Palace, chart_data: ChartResult, 
                    config: DisplayConfig, global_data: dict)
```

### 核心方法

#### `__init__(self, global_data: dict, parent=None)`

**功能**: 初始化PalaceWidget组件

**参数**:
- `global_data`: 从data/core_parameters.json加载的全局数据字典，用于五行颜色查询
- `parent`: 父控件

**实现逻辑**:
1. 创建3x3 QGridLayout
2. 实例化9个ParameterWidget，按九宫格位置放置
3. 初始化五行颜色映射表
4. 存储global_data引用供后续查询使用

#### `update_data(self, palace_data, chart_data, config, global_data)`

**功能**: 更新宫位显示数据，核心数据分发方法

**参数**:
- `palace_data`: Palace对象，包含宫位基础信息
- `chart_data`: ChartResult对象，包含全局信息（值符、值使、局数等）
- `config`: DisplayConfig对象，控制显示逻辑
- `global_data`: 全局数据字典，用于五行查询

**数据分发逻辑**:

1. **清空阶段**: 清空所有ParameterWidget数据
2. **宫位判断**: 检查是否为中宫 (index == 5)
3. **中宫处理**:
   - 格子5: 显示局数 `f"{遁}{局}局"`，土行颜色
   - 格子9: 显示中宫地盘干，对应五行颜色
4. **普通宫位处理**:
   - 格子2: 八神，查询五行颜色，八神本身不加粗
   - 格子5: 九星，处理双星合并，检查是否包含值符星（值符星加粗）
   - 格子8: 八门，查询五行颜色，检查是否为值使门（值使门加粗）
   - 格子6: 天盘干（主要），对应五行颜色
   - 格子9: 地盘干（主要），对应五行颜色
   - 格子4/7: 寄宫天干（如果有多个天盘干）
   - 格子1/3: 寄宫地盘干（如果有多个地盘干）

### 九宫格位置映射

```
格子位置编号:    网格坐标:
7  8  9         (0,0) (0,1) (0,2)
4  5  6    →    (1,0) (1,1) (1,2)  
1  2  3         (2,0) (2,1) (2,2)
```

### 辅助方法

#### `_get_wuxing_color(self, param_type: str, param_name: str) -> QColor`

**功能**: 安全查询五行颜色

**参数**:
- `param_type`: 参数类型 ("tianGan", "baMen", "jiuXing", "baShen")
- `param_name`: 参数名称（中文）

**返回**: QColor对象，找不到时返回黑色

#### `_format_stars(self, stars: List[str]) -> str`

**功能**: 格式化星宿显示文本

**逻辑**:
- 单星: 直接返回
- 双星: 连接为"禽芮"格式
- 多星: 逗号分隔

## 使用示例

### 基础使用

```python
from ui.widgets.palace_widget import PalaceWidget
from ui.config import DisplayConfig
from core.models import Palace, ChartResult
import json

# 加载全局数据
with open('data/core_parameters.json', 'r', encoding='utf-8') as f:
    global_data = json.load(f)

# 创建组件
palace_widget = PalaceWidget(global_data)

# 创建配置
config = DisplayConfig(use_wuxing_colors=True, show_zhi_fu_shi_bold=True)

# 更新显示数据
palace_widget.update_data(palace_data, chart_data, config, global_data)
```

### 集成到九宫格

```python
# 创建9个宫位组件
palace_widgets = {}
for i in range(1, 10):
    palace_widgets[i] = PalaceWidget(global_data)
    
# 排盘后更新所有宫位
chart_result = engine.paipan(time_str)
for i in range(1, 10):
    palace_data = chart_result.palaces[i]
    palace_widgets[i].update_data(palace_data, chart_result, config, global_data)
```

## 测试和验证

### 运行基础测试

```bash
# 基础功能测试（单宫位）
python ui/widgets/palace_widget.py
```

### 运行完整演示

```bash
# 完整九宫格集成演示
python ui/widgets/demo_palace_integration.py
```

### 测试覆盖场景

1. **普通宫位显示** - 八神、九星、八门、天盘干、地盘干的正确分发
2. **中宫特殊显示** - 局数信息和地盘干的特殊布局
3. **值符值使识别** - 值符、值使的加粗显示
4. **五行颜色应用** - 各类参数的五行颜色正确显示
5. **寄宫天干处理** - 多个天干的额外位置显示
6. **双星格式化** - 如"禽芮"的正确合并显示
7. **数据安全性** - 缺失数据时的健壮性处理

## 性能特性

### 响应性优化
- `update_data` 方法执行迅速，适合频繁调用
- 直接操作子组件，无额外绘制开销
- 数据验证和查询优化，减少计算时间

### 健壮性保证
- 五行颜色查询异常处理
- 数据缺失时的默认值处理
- try-catch保护防止程序崩溃

## 架构设计原则

### 单一职责
- PalaceWidget 专注于容器和数据分发
- 所有绘制逻辑委托给 ParameterWidget
- 清晰的职责边界，易于维护

### 数据驱动
- 完全基于传入数据进行显示
- 无内部状态依赖，便于测试
- 配置分离，支持不同显示需求

### 组合优于继承
- 通过组合ParameterWidget实现功能
- 避免复杂的继承层次
- 更好的代码复用和扩展性

## 扩展性设计

### 预留扩展点

1. **标注系统**: 预留annotation_text参数传递
2. **布局扩展**: 可支持不同的宫位布局方案
3. **样式主题**: 通过DisplayConfig扩展主题支持
4. **交互增强**: 可添加宫位选择、拖拽等交互

### 未来功能

- 宫位选中状态管理
- 自定义布局模式
- 动画效果支持
- 标注数据的完整集成

## 完成标准验证

### ✅ 功能要求
- [x] 继承自QWidget
- [x] 内部包含3x3 QGridLayout
- [x] 实例化9个ParameterWidget
- [x] update_data公共方法实现
- [x] 中宫特殊显示逻辑
- [x] 正确的数据分发和渲染

### ✅ 质量要求
- [x] PEP 8 代码规范
- [x] 完整的文档字符串
- [x] 独立运行测试脚本
- [x] 普通宫位和中宫测试验证
- [x] 核心数据分发功能验证

### ✅ 性能要求
- [x] update_data方法高效执行
- [x] 健壮的数据查询机制
- [x] 异常情况安全处理

PalaceWidget组件开发完成，满足所有验收标准！
