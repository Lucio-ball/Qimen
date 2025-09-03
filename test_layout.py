"""
九宫格布局测试程序
运行ChartWidget让用户验证布局是否正确
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QLabel
from ui.widgets.chart_widget import ChartWidget
from ui.config import DisplayConfig
from core.paipan_engine import PaiPanEngine
import json


def main():
    """主程序"""
    app = QApplication(sys.argv)
    
    # 加载数据
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            global_data = json.load(f)
        print("✓ 成功加载data.json")
    except FileNotFoundError:
        print("✗ 未找到data.json文件")
        return 1
    
    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("奇门遁甲盘面布局测试")
    main_window.setGeometry(100, 100, 1200, 800)
    
    # 创建中央控件
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # 控制面板
    control_panel = QWidget()
    control_layout = QHBoxLayout(control_panel)
    
    # 时间输入
    control_layout.addWidget(QLabel("时间:"))
    time_input = QLineEdit("202412011530")
    time_input.setPlaceholderText("YYYYMMDDHHMM格式")
    control_layout.addWidget(time_input)
    
    # 创建配置
    config = DisplayConfig(use_wuxing_colors=True, show_zhi_fu_shi_bold=True)
    
    # 创建ChartWidget
    chart_widget = ChartWidget(global_data, config)
    
    def update_chart():
        """更新盘面显示"""
        time_str = time_input.text().strip()
        if len(time_str) < 10:
            print("✗ 时间格式错误，需要至少10位数字")
            return
        
        try:
            # 标准化时间格式
            if len(time_str) == 10:
                time_str += "00"
            if len(time_str) == 12:
                time_str += "00"
            
            print(f"排盘时间: {time_str}")
            
            # 解析时间为易读格式
            year = time_str[:4]
            month = time_str[4:6] 
            day = time_str[6:8]
            hour = time_str[8:10]
            minute = time_str[10:12]
            formatted_time = f"{year}年{month}月{day}日 {hour}:{minute}"
            
            # 创建排盘引擎并排盘
            engine = PaiPanEngine(data_file_path='data.json')
            chart_result = engine.paipan(time_str)
            
            # 在chart_result中添加格式化时间信息
            chart_result.qi_ju_time = formatted_time
            
            # 更新ChartWidget显示
            chart_widget.update_chart(chart_result)
            print("✓ 盘面更新成功")
            
            # 打印宫位信息供验证
            print("\n=== 宫位信息 ===")
            for i in range(9):
                palace_data = chart_result.palaces[i]
                palace_id = i + 1
                print(f"宫{palace_id}: 九星={palace_data.stars}, 八门={palace_data.gates}, 八神={palace_data.god}")
            
        except Exception as e:
            print(f"✗ 排盘失败: {e}")
    
    # 按钮
    update_btn = QPushButton("排盘")
    update_btn.clicked.connect(update_chart)
    control_layout.addWidget(update_btn)
    
    control_layout.addStretch()
    
    # 布局
    layout.addWidget(control_panel)
    layout.addWidget(chart_widget)
    
    main_window.setCentralWidget(central_widget)
    
    # 默认加载一个盘面
    print("正确的九宫格布局应该是:")
    print("    巳 午 未")
    print("辰  4  9  2 申")
    print("卯  3  5  7 酉")
    print("寅  8  1  6 戌")
    print("    丑 子 亥")
    print("\n加载默认盘面...")
    update_chart()
    
    main_window.show()
    
    print("\n=== 请检查界面中的布局 ===")
    print("1. 观察九宫格中的数字标识是否对应正确位置")
    print("2. 观察外圈地支标注是否在正确位置")
    print("3. 如有问题请告知具体哪个宫位不对")
    print("================================\n")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
