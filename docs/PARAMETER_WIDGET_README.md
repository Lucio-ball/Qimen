# ParameterWidget 组件说明

## 概述

ParameterWidget 是奇门遁甲工作台的核心显示组件，用于绘制单个奇门参数及其所有附加状态。

## 文件结构

```
ui/
├── config.py                          # DisplayConfig配置类
└── widgets/
    ├── parameter_widget.py             # ParameterWidget主体实现
    └── demo_parameter_widget.py        # 九宫格演示程序
```

## 核心特性

### 1. 自定义绘制
- 通过重写 `paintEvent` 方法实现完全自定义绘制
- 支持抗锯齿渲染，确保显示效果平滑
- 不依赖子控件，性能优化

### 2. 高度可配置
- 通过 `DisplayConfig` 类控制所有显示选项
- 支持五行颜色开关
- 可配置选中边框样式
- 可调整标注显示效果

### 3. 交互功能
- 鼠标点击切换选中状态
- 选中状态通过红色边框视觉反馈
- 支持未来扩展更多交互功能

### 4. 标注系统
- 支持覆盖式标注显示
- 半透明圆圈背景 + 小字标注
- 预留扩展空间，支持多种标注类型

## API 接口

### DisplayConfig 类

```python
@dataclass
class DisplayConfig:
    use_wuxing_colors: bool = True          # 是否使用五行颜色
    show_zhi_fu_shi_bold: bool = True       # 是否对值符使显示加粗
    annotation_background_alpha: int = 128   # 标注背景透明度 (0-255)
    selected_border_width: int = 2          # 选中边框宽度
    annotation_circle_radius: int = 8       # 标注圆圈半径
```

### ParameterWidget 类

#### 核心方法

```python
def set_data(self, text: str, config: DisplayConfig, color: QColor, 
             is_bold: bool, annotation_text: Optional[str] = None):
    """
    设置控件的显示数据和配置
    
    Args:
        text: 要显示的主要文本 (e.g., "庚", "休门")
        config: DisplayConfig 对象，用于控制显示逻辑
        color: QColor 对象，代表参数的五行颜色
        is_bold: 布尔值，决定文本是否加粗
        annotation_text: 字符串，代表要覆盖显示的标注小字
    """
```

#### 绘制流程

1. **背景和边框绘制**
   - 检查选中状态
   - 绘制红色选中边框

2. **主文本绘制**
   - 根据配置设置字体（加粗/普通）
   - 根据文本长度调整字体大小
   - 应用五行颜色或默认颜色
   - 居中绘制文本

3. **标注绘制**
   - 绘制半透明圆圈背景
   - 绘制红色边框圆圈
   - 居中绘制标注文字

## 使用示例

### 基础使用

```python
from ui.widgets.parameter_widget import ParameterWidget
from ui.config import DisplayConfig
from PySide6.QtGui import QColor

# 创建配置
config = DisplayConfig(use_wuxing_colors=True)

# 创建组件
widget = ParameterWidget()

# 设置数据 - 显示一个绿色的"乙"字
widget.set_data(
    text="乙",
    config=config,
    color=QColor(0, 255, 0),  # 绿色
    is_bold=False
)
```

### 带标注使用

```python
# 显示一个带"旺"标注的红色加粗"丙"字
widget.set_data(
    text="丙",
    config=config,
    color=QColor(255, 0, 0),  # 红色
    is_bold=True,             # 加粗
    annotation_text="旺"       # 标注
)
```

## 测试和验证

### 运行基础测试

```bash
# 基础功能测试
python ui/widgets/parameter_widget.py
```

### 运行九宫格演示

```bash
# 完整九宫格演示
python ui/widgets/demo_parameter_widget.py
```

### 测试覆盖场景

1. **正常显示** - 不同颜色的文字正常显示
2. **加粗显示** - 值符、值使等重要元素加粗
3. **选中状态** - 点击后出现/消失红色边框
4. **标注显示** - 覆盖式圆圈标注
5. **颜色关闭** - 关闭五行颜色后显示黑色文字
6. **字体大小** - 根据文字长度自动调整

## 性能特性

- **高效绘制** - 直接使用QPainter，无子控件开销
- **按需更新** - 只在数据变化时触发重绘
- **内存优化** - 最小化对象创建，复用画笔和字体
- **渲染优化** - 启用抗锯齿，确保最佳显示效果

## 扩展性设计

### 预留扩展点

1. **绘制层次** - 代码结构支持添加更多绘制层
2. **标注类型** - 可扩展支持多种标注样式
3. **交互事件** - 可添加更多鼠标和键盘事件
4. **配置选项** - DisplayConfig 支持添加新配置项

### 未来功能

- 角标显示（如"门迫"标识）
- 多重标注叠加
- 动画效果支持
- 主题切换支持

## 代码质量

- **PEP 8 规范** - 严格遵循Python代码规范
- **类型提示** - 完整的类型注解
- **文档字符串** - 详细的方法和类文档
- **错误处理** - 参数验证和异常处理
