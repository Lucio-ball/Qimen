#!/usr/bin/env python3
"""
属性调节面板控件
用于实时控制盘面元素的显示与隐藏
"""

import sys
import os
from typing import Dict
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QCheckBox, 
                               QApplication, QMainWindow)
from PySide6.QtCore import Signal

# 确保能导入配置类
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)
from ui.config import DisplayConfig


class AttributePanelWidget(QWidget):
    """
    属性调节面板控件
    
    提供一个用户友好的界面来控制各种显示选项，
    当用户修改任何设置时会发出配置变更信号。
    """
    
    # 自定义信号：配置变更时发出，携带更新后的DisplayConfig对象
    config_changed = Signal(DisplayConfig)
    
    def __init__(self, initial_config: DisplayConfig, parent=None):
        """
        初始化属性调节面板
        
        Args:
            initial_config: 初始的显示配置对象
            parent: 父控件
        """
        super().__init__(parent)
        
        self.initial_config = initial_config
        self.checkboxes: Dict[str, QCheckBox] = {}
        
        self._setup_ui()
        self._setup_connections()
        self._apply_initial_config()
    
    def _setup_ui(self):
        """设置用户界面"""
        main_layout = QVBoxLayout(self)
        
        # 样式设置分组
        style_group = QGroupBox("样式设置")
        style_layout = QVBoxLayout(style_group)
        
        # 创建样式相关的复选框
        self.checkboxes['use_wuxing_colors'] = QCheckBox("按五行颜色显示参数")
        self.checkboxes['show_zhi_fu_shi_bold'] = QCheckBox("加粗显示值符/值使")
        self.checkboxes['auto_yue_ling_chong_kong'] = QCheckBox("月令自动填空")
        self.checkboxes['auto_maxing_chong_mu_kong'] = QCheckBox("马星自动冲墓、冲空")
        
        # 添加样式复选框到布局
        style_layout.addWidget(self.checkboxes['use_wuxing_colors'])
        style_layout.addWidget(self.checkboxes['show_zhi_fu_shi_bold'])
        style_layout.addWidget(self.checkboxes['auto_yue_ling_chong_kong'])
        style_layout.addWidget(self.checkboxes['auto_maxing_chong_mu_kong'])
        
        # 参数显示分组
        param_group = QGroupBox("参数显示")
        param_layout = QVBoxLayout(param_group)
        
        # 创建参数显示相关的复选框
        self.checkboxes['show_ri_kong'] = QCheckBox("显示日空")
        self.checkboxes['show_shi_kong'] = QCheckBox("显示时空")
        self.checkboxes['show_liu_ji'] = QCheckBox("显示六仪击刑")
        self.checkboxes['show_ru_mu'] = QCheckBox("显示入墓")
        self.checkboxes['show_ma_xing'] = QCheckBox("显示马星")
        self.checkboxes['show_yue_ling'] = QCheckBox("显示月令")
        
        # 添加参数复选框到布局
        param_layout.addWidget(self.checkboxes['show_ri_kong'])
        param_layout.addWidget(self.checkboxes['show_shi_kong'])
        param_layout.addWidget(self.checkboxes['show_liu_ji'])
        param_layout.addWidget(self.checkboxes['show_ru_mu'])
        param_layout.addWidget(self.checkboxes['show_ma_xing'])
        param_layout.addWidget(self.checkboxes['show_yue_ling'])
        
        # 添加分组到主布局
        main_layout.addWidget(style_group)
        main_layout.addWidget(param_group)
        
        # 设置布局的stretch，让内容紧凑显示
        main_layout.addStretch()
    
    def _setup_connections(self):
        """设置信号连接"""
        for checkbox in self.checkboxes.values():
            checkbox.stateChanged.connect(self._on_checkbox_changed)
    
    def _apply_initial_config(self):
        """根据初始配置设置复选框状态"""
        # 样式设置
        self.checkboxes['use_wuxing_colors'].setChecked(self.initial_config.use_wuxing_colors)
        self.checkboxes['show_zhi_fu_shi_bold'].setChecked(self.initial_config.show_zhi_fu_shi_bold)
        self.checkboxes['auto_yue_ling_chong_kong'].setChecked(self.initial_config.auto_yue_ling_chong_kong)
        self.checkboxes['auto_maxing_chong_mu_kong'].setChecked(self.initial_config.auto_maxing_chong_mu_kong)
        
        # 参数显示
        self.checkboxes['show_ri_kong'].setChecked(self.initial_config.show_ri_kong)
        self.checkboxes['show_shi_kong'].setChecked(self.initial_config.show_shi_kong)
        self.checkboxes['show_liu_ji'].setChecked(self.initial_config.show_liu_ji)
        self.checkboxes['show_ru_mu'].setChecked(self.initial_config.show_ru_mu)
        self.checkboxes['show_ma_xing'].setChecked(self.initial_config.show_ma_xing)
        self.checkboxes['show_yue_ling'].setChecked(self.initial_config.show_yue_ling)
    
    def _on_checkbox_changed(self):
        """
        复选框状态变更的槽函数
        
        当任何复选框状态改变时，获取当前配置并发出信号
        """
        current_config = self.get_current_config()
        self.config_changed.emit(current_config)
    
    def get_current_config(self) -> DisplayConfig:
        """
        从当前复选框状态构建DisplayConfig对象
        
        Returns:
            基于当前UI状态的DisplayConfig对象
        """
        return DisplayConfig(
            # 样式设置
            use_wuxing_colors=self.checkboxes['use_wuxing_colors'].isChecked(),
            show_zhi_fu_shi_bold=self.checkboxes['show_zhi_fu_shi_bold'].isChecked(),
            auto_yue_ling_chong_kong=self.checkboxes['auto_yue_ling_chong_kong'].isChecked(),
            auto_maxing_chong_mu_kong=self.checkboxes['auto_maxing_chong_mu_kong'].isChecked(),
            
            # 参数显示
            show_ri_kong=self.checkboxes['show_ri_kong'].isChecked(),
            show_shi_kong=self.checkboxes['show_shi_kong'].isChecked(),
            show_liu_ji=self.checkboxes['show_liu_ji'].isChecked(),
            show_ru_mu=self.checkboxes['show_ru_mu'].isChecked(),
            show_ma_xing=self.checkboxes['show_ma_xing'].isChecked(),
            show_yue_ling=self.checkboxes['show_yue_ling'].isChecked(),
            
            # 保持原有的数值配置
            annotation_background_alpha=self.initial_config.annotation_background_alpha,
            selected_border_width=self.initial_config.selected_border_width,
            annotation_circle_radius=self.initial_config.annotation_circle_radius
        )


def test_config_changed(config: DisplayConfig):
    """测试配置变更的槽函数"""
    print("=" * 50)
    print("配置已更新:")
    print(f"样式设置:")
    print(f"  按五行颜色显示参数: {config.use_wuxing_colors}")
    print(f"  加粗显示值符/值使: {config.show_zhi_fu_shi_bold}")
    print(f"  月令自动填空: {config.auto_yue_ling_chong_kong}")
    print(f"  马星自动冲墓、冲空: {config.auto_maxing_chong_mu_kong}")
    print(f"参数显示:")
    print(f"  显示日空: {config.show_ri_kong}")
    print(f"  显示时空: {config.show_shi_kong}")
    print(f"  显示六仪击刑: {config.show_liu_ji}")
    print(f"  显示入墓: {config.show_ru_mu}")
    print(f"  显示马星: {config.show_ma_xing}")
    print(f"  显示月令: {config.show_yue_ling}")
    print("=" * 50)


if __name__ == "__main__":
    """
    独立测试脚本
    
    创建一个测试窗口来验证AttributePanelWidget的功能：
    1. 创建初始配置
    2. 显示属性面板
    3. 监听配置变更并打印结果
    """
    app = QApplication(sys.argv)
    
    # 创建初始配置
    initial_config = DisplayConfig(
        use_wuxing_colors=True,
        show_zhi_fu_shi_bold=False,
        auto_yue_ling_chong_kong=True,
        auto_maxing_chong_mu_kong=True,
        show_ri_kong=True,
        show_shi_kong=True,
        show_liu_ji=False,
        show_ru_mu=True,
        show_ma_xing=True,
        show_yue_ling=False
    )
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("属性调节面板测试")
    main_window.resize(400, 500)
    
    # 创建属性面板控件
    attribute_panel = AttributePanelWidget(initial_config)
    main_window.setCentralWidget(attribute_panel)
    
    # 连接配置变更信号到测试函数
    attribute_panel.config_changed.connect(test_config_changed)
    
    # 显示窗口
    main_window.show()
    
    print("属性调节面板测试")
    print("请点击界面上的复选框，观察终端输出是否正确显示配置变更")
    print("初始配置:")
    test_config_changed(initial_config)
    
    sys.exit(app.exec())
