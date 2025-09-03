"""
九宫格布局验证程序
验证修正后的九宫格与十二地支位置是否正确
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel
from PySide6.QtCore import Qt
from ui.widgets.chart_widget import ChartWidget
from ui.config import DisplayConfig
from core.paipan_engine import PaiPanEngine
import json


def main():
    """主程序"""
    app = QApplication(sys.argv)
    
    # 加载数据
    with open("data.json", "r", encoding="utf-8") as f:
        global_data = json.load(f)
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("九宫格布局验证 - 修正版")
    main_window.setGeometry(100, 100, 800, 600)
    
    # 创建配置
    config = DisplayConfig(use_wuxing_colors=True)
    
    # 创建ChartWidget
    chart_widget = ChartWidget(global_data, config)
    
    # 排盘并显示
    engine = PaiPanEngine(data_file_path='data.json')
    chart_result = engine.paipan('20241201153000')
    chart_widget.update_chart(chart_result)
    
    main_window.setCentralWidget(chart_widget)
    main_window.show()
    
    print("九宫格布局验证:")
    print("    巳 午 未")
    print("辰  4  9  2 申")
    print("卯  3  5  7 酉")
    print("寅  8  1  6 戌")
    print("    丑 子 亥")
    print()
    print("请检查界面中的布局是否与上述图示一致")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
