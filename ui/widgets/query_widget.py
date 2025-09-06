"""
QueryWidget - 奇门遁甲起局页面控件

这是一个独立的、可复用的起局控件，用于收集起局所需的时间、年命和事由信息。
当用户完成输入并点击"立即起局"按钮时，控件会发出query_requested信号携带用户数据。
"""

import datetime
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QDateTimeEdit, QPushButton, QLineEdit, QTextEdit
)
from PySide6.QtCore import Signal, QDateTime, QDate, QEvent, Qt
from PySide6.QtGui import QFont, QFocusEvent, QMouseEvent


class SmartTimeLineEdit(QLineEdit):
    """
    智能时间输入框，支持友好显示和原始编辑格式切换
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._editing = False
        self._parent_widget = None
        
    def set_parent_widget(self, parent_widget):
        """设置父控件引用，用于回调"""
        self._parent_widget = parent_widget
        
    def focusInEvent(self, event: QFocusEvent):
        """焦点进入事件"""
        super().focusInEvent(event)
        self._editing = True
        if self._parent_widget:
            self._parent_widget._convert_to_raw_format()
            
    def focusOutEvent(self, event: QFocusEvent):
        """焦点离开事件"""
        super().focusOutEvent(event)
        self._editing = False
        if self._parent_widget:
            self._parent_widget._format_time_display()
            
    def keyPressEvent(self, event):
        """按键事件处理"""
        if event.key() in (16777220, 16777221):  # Enter 或 Return
            # 按下回车键时失去焦点
            self.clearFocus()
        super().keyPressEvent(event)
        
    def is_editing(self):
        """返回当前是否在编辑模式"""
        return self._editing


class QueryWidget(QWidget):
    """
    奇门遁甲起局输入控件
    
    这个控件提供一个完整的起局输入界面，包括：
    - 时间选择器（QDateTimeEdit）
    - 年命输入和自动计算显示
    - 事由输入区域
    - 起局触发按钮
    
    Signals:
        query_requested(dict): 当用户点击"立即起局"时发出的信号
            信号携带的字典包含：
            {
                "query_time": datetime.datetime,  # 起局时间
                "nian_ming": str,                # 年命干支，如"庚午"
                "notes": str                     # 所问之事
            }
    """
    
    # 定义自定义信号
    query_requested = Signal(dict)
    
    def __init__(self, parent=None, show_query_button=True):
        """
        初始化QueryWidget控件
        
        Args:
            parent: 父组件
            show_query_button: 是否显示内部的"立即起局"按钮，默认为True
        """
        super().__init__(parent)
        # 设置控件可以接收焦点
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.show_query_button = show_query_button
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """初始化用户界面"""
        # 设置控件最小尺寸
        self.setMinimumSize(400, 300)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. 起局时间区域
        self._create_time_section(main_layout)
        
        # 2. 年命输入区域
        self._create_nian_ming_section(main_layout)
        
        # 3. 事由输入区域
        self._create_notes_section(main_layout)
        
        # 4. 起局按钮（可选）
        if self.show_query_button:
            self._create_action_button(main_layout)
        
    def _create_time_section(self, parent_layout):
        """创建时间输入区域"""
        # 时间标签
        time_label = QLabel("起局时间")
        time_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        parent_layout.addWidget(time_label)
        
        # 时间输入行布局
        time_layout = QHBoxLayout()
        
        # 时间输入框（使用自定义的SmartTimeLineEdit）
        self.time_input = SmartTimeLineEdit()
        self.time_input.set_parent_widget(self)
        self.time_input.setPlaceholderText("请输入时间，格式：年月日时分 如 202409011430")
        self.time_input.setMaximumWidth(300)
        
        # 设置默认值为当前时间
        current_time = datetime.datetime.now()
        default_time_str = current_time.strftime("%Y%m%d%H%M")
        self.time_input.setText(default_time_str)
        
        # 初始显示为友好格式
        self._format_time_display()
        
        time_layout.addWidget(self.time_input, 1)
        
        # 当前时间按钮
        self.current_time_btn = QPushButton("当前")
        self.current_time_btn.setMaximumWidth(60)
        time_layout.addWidget(self.current_time_btn)
        
        parent_layout.addLayout(time_layout)
        
    def _create_nian_ming_section(self, parent_layout):
        """创建年命输入区域"""
        # 年命标签
        nian_ming_label = QLabel("求测人年命")
        nian_ming_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        parent_layout.addWidget(nian_ming_label)
        
        # 年命输入行布局
        nian_ming_layout = QHBoxLayout()
        
        # 出生日期选择器
        self.birth_date_edit = QDateTimeEdit()
        self.birth_date_edit.setDate(QDate.currentDate().addYears(-25))  # 默认25年前
        self.birth_date_edit.setDisplayFormat("yyyy年MM月dd日")
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setMaximumWidth(200)
        nian_ming_layout.addWidget(self.birth_date_edit)
        
        # 干支显示标签
        self.gan_zhi_label = QLabel("")
        self.gan_zhi_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #0066cc;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: #f8f8f8;
                min-width: 40px;
            }
        """)
        nian_ming_layout.addWidget(self.gan_zhi_label)
        
        # 添加弹性空间
        nian_ming_layout.addStretch()
        
        parent_layout.addLayout(nian_ming_layout)
        
        # 初始计算一次年命
        self._calculate_gan_zhi()
        
    def _create_notes_section(self, parent_layout):
        """创建事由输入区域"""
        # 事由标签
        notes_label = QLabel("所问何事 (选填)")
        notes_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        parent_layout.addWidget(notes_label)
        
        # 事由输入框
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("记录所问之事...")
        self.notes_edit.setMaximumHeight(80)
        parent_layout.addWidget(self.notes_edit)
        
    def _create_action_button(self, parent_layout):
        """创建操作按钮区域"""
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 左侧弹性空间
        
        # 起局按钮
        self.query_btn = QPushButton("立即起局")
        self.query_btn.setMinimumSize(120, 40)
        self.query_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
        """)
        button_layout.addWidget(self.query_btn)
        
        parent_layout.addLayout(button_layout)
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 当前时间按钮
        self.current_time_btn.clicked.connect(self._reset_to_current_time)
        
        # 时间输入框 - 文本改变信号
        self.time_input.textChanged.connect(self._on_time_input_text_changed)
        
        # 出生日期选择器 - 日期改变时重新计算年命
        self.birth_date_edit.dateChanged.connect(self._calculate_gan_zhi)
        
        # 起局按钮（只有在按钮存在时才连接信号）
        if hasattr(self, 'query_btn'):
            self.query_btn.clicked.connect(self._emit_query_request)
        
    def _reset_to_current_time(self):
        """重置时间为当前时间"""
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime("%Y%m%d%H%M")
        self.time_input.setText(current_time_str)
        self._format_time_display()
        
    def _on_time_input_text_changed(self):
        """时间输入框文本改变时的处理"""
        if self.time_input.is_editing():
            # 编辑模式下进行格式验证
            self._validate_time_format()
            
    def _convert_to_raw_format(self):
        """将友好显示格式转换为原始编辑格式"""
        current_text = self.time_input.text().strip()
        
        # 如果已经是原始格式，则不需要转换
        if re.match(r'^\d{12}$', current_text):
            return
            
        # 尝试从友好格式解析
        try:
            # 解析友好格式：2024年9月1日 14:30
            # 匹配模式：YYYY年M月D日 HH:MM 或 YYYY年MM月DD日 HH:MM
            pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{1,2}):(\d{2})'
            match = re.match(pattern, current_text)
            
            if match:
                year, month, day, hour, minute = match.groups()
                # 确保格式为两位数
                month = month.zfill(2)
                day = day.zfill(2)
                hour = hour.zfill(2)
                
                raw_format = f"{year}{month}{day}{hour}{minute}"
                self.time_input.setText(raw_format)
            else:
                # 如果无法解析，保持原文本
                pass
                
        except Exception:
            # 解析失败，保持原文本
            pass
            
    def _format_time_display(self):
        """将原始格式转换为友好显示格式"""
        if self.time_input.is_editing():
            return  # 编辑模式下不转换
            
        time_text = self.time_input.text().strip()
        
        # 验证是否为12位数字格式
        if not re.match(r'^\d{12}$', time_text):
            return  # 不是有效格式，不转换
            
        try:
            year = time_text[:4]
            month = time_text[4:6]
            day = time_text[6:8]
            hour = time_text[8:10]
            minute = time_text[10:12]
            
            # 验证日期有效性
            datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
            
            # 转换为友好格式：去掉前导零但保持合理格式
            month_display = str(int(month))
            day_display = str(int(day))
            hour_display = hour  # 小时保持两位
            
            friendly_format = f"{year}年{month_display}月{day_display}日 {hour_display}:{minute}"
            self.time_input.setText(friendly_format)
            
            # 设置正常样式
            self.time_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 2px;
                    background-color: #f9f9f9;
                }
            """)
            
        except (ValueError, OverflowError):
            # 日期无效，不转换
            pass
        
    def _validate_time_format(self):
        """验证时间输入格式并提供视觉反馈（仅在编辑模式下）"""
        if not self.time_input.is_editing():
            return  # 非编辑模式不验证
            
        time_text = self.time_input.text().strip()
        
        # 正则表达式匹配YYYYMMDDHHMM格式
        pattern = r'^\d{12}$'
        
        if not time_text:
            # 空输入，使用默认样式
            self.time_input.setStyleSheet("")
            return
            
        if re.match(pattern, time_text):
            # 进一步验证日期时间的有效性
            try:
                year = int(time_text[:4])
                month = int(time_text[4:6])
                day = int(time_text[6:8])
                hour = int(time_text[8:10])
                minute = int(time_text[10:12])
                
                # 验证范围
                if (1900 <= year <= 2100 and 
                    1 <= month <= 12 and 
                    1 <= day <= 31 and 
                    0 <= hour <= 23 and 
                    0 <= minute <= 59):
                    
                    # 尝试创建datetime对象验证日期有效性
                    datetime.datetime(year, month, day, hour, minute)
                    
                    # 格式正确，使用绿色边框
                    self.time_input.setStyleSheet("""
                        QLineEdit {
                            border: 2px solid #00aa00;
                            border-radius: 3px;
                            padding: 2px;
                        }
                    """)
                else:
                    raise ValueError("日期时间超出有效范围")
                    
            except (ValueError, OverflowError):
                # 格式错误，使用红色边框
                self.time_input.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid #cc0000;
                        border-radius: 3px;
                        padding: 2px;
                    }
                """)
        else:
            # 格式错误，使用红色边框
            self.time_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #cc0000;
                    border-radius: 3px;
                    padding: 2px;
                }
            """)
        
    def _calculate_gan_zhi(self):
        """计算并显示年命干支"""
        try:
            # 获取选择的出生日期
            birth_date = self.birth_date_edit.date().toPython()
            birth_datetime = datetime.datetime.combine(birth_date, datetime.time.min)
            
            # 动态导入年命计算功能
            try:
                from core.calendar_utils import get_si_zhu
            except ImportError:
                # 如果导入失败，使用备用计算方法
                self.gan_zhi_label.setText("功能不可用")
                self.gan_zhi_label.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        color: #cc6600;
                        font-weight: bold;
                        padding: 5px;
                        border: 1px solid #cccccc;
                        border-radius: 3px;
                        background-color: #fff8e6;
                        min-width: 40px;
                    }
                """)
                return
                
            # 计算四柱
            si_zhu = get_si_zhu(birth_datetime)
            nian_zhu = si_zhu['年']
            
            # 显示结果
            self.gan_zhi_label.setText(nian_zhu)
            self.gan_zhi_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #0066cc;
                    font-weight: bold;
                    padding: 5px;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    background-color: #f8f8f8;
                    min-width: 40px;
                }
            """)
            
        except Exception as e:
            # 处理计算错误
            self.gan_zhi_label.setText("计算错误")
            self.gan_zhi_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #cc0000;
                    font-weight: bold;
                    padding: 5px;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    background-color: #ffe6e6;
                    min-width: 40px;
                }
            """)
            print(f"年命计算错误: {e}")
            
    def _emit_query_request(self):
        """发射起局请求信号"""
        # 确保获取原始格式的时间
        self._convert_to_raw_format()
        time_text = self.time_input.text().strip()
        
        # 验证时间格式
        pattern = r'^\d{12}$'
        if not re.match(pattern, time_text):
            # 时间格式错误，不发射信号
            print("时间格式错误，无法起局")
            return
            
        try:
            # 解析时间字符串
            year = int(time_text[:4])
            month = int(time_text[4:6])
            day = int(time_text[6:8])
            hour = int(time_text[8:10])
            minute = int(time_text[10:12])
            
            # 创建datetime对象
            query_time = datetime.datetime(year, month, day, hour, minute)
            
        except (ValueError, OverflowError):
            print("时间格式错误，无法起局")
            return
        
        # 获取年命干支
        nian_ming = self.gan_zhi_label.text()
        if nian_ming in ["", "无效年份", "计算错误", "功能不可用"]:
            nian_ming = ""
            
        # 获取事由
        notes = self.notes_edit.toPlainText().strip()
        
        # 构建数据字典
        query_data = {
            "query_time": query_time,
            "nian_ming": nian_ming,
            "notes": notes
        }
        
        # 发射信号
        self.query_requested.emit(query_data)
        
        # 发射后恢复友好显示格式
        self._format_time_display()
        
    def reset_form(self):
        """
        重置表单到默认状态
        
        重置内容包括：
        - 时间输入框重置为当前时间
        - 出生日期重置为25年前
        - 事由输入框清空
        - 重新计算年命干支
        """
        # 1. 重置时间为当前时间
        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime("%Y%m%d%H%M")
        self.time_input.setText(current_time_str)
        self._format_time_display()
        
        # 2. 重置出生日期为25年前
        default_birth_date = QDate.currentDate().addYears(-25)
        self.birth_date_edit.setDate(default_birth_date)
        
        # 3. 清空事由输入框
        self.notes_edit.clear()
        
        # 4. 重新计算年命干支
        self._calculate_gan_zhi()
        
        # 5. 清除所有控件的焦点状态
        if hasattr(self, 'time_input') and self.time_input.is_editing():
            self.time_input.clearFocus()
        self.setFocus()
        
    def focusInEvent(self, event: QFocusEvent):
        """QueryWidget获得焦点时的处理"""
        super().focusInEvent(event)
        # 如果时间输入框正在编辑，让它失去焦点
        if hasattr(self, 'time_input') and self.time_input.is_editing():
            self.time_input.clearFocus()
            
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标点击事件处理 - 点击空白区域时清除焦点"""
        # 调用父类的鼠标事件
        super().mousePressEvent(event)
        
        # 检查点击位置是否在任何子控件上（使用position()代替deprecated的pos()）
        try:
            pos = event.position().toPoint()
        except AttributeError:
            # 兼容旧版本PySide6
            pos = event.pos()
            
        child_widget = self.childAt(pos)
        
        if child_widget is None:
            # 点击在空白区域，清除所有控件的焦点
            self.setFocus()
            # 特别处理时间输入框
            if hasattr(self, 'time_input') and self.time_input.is_editing():
                self.time_input.clearFocus()


# 独立测试脚本
if __name__ == "__main__":
    import sys
    import os
    
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)
    
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    
    def on_query_requested(data):
        """处理起局请求的测试函数"""
        print("=" * 50)
        print("收到起局请求:")
        print(f"起局时间: {data['query_time']}")
        print(f"年命干支: {data['nian_ming']}")
        print(f"所问之事: {data['notes']}")
        print("=" * 50)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = QMainWindow()
    window.setWindowTitle("QueryWidget 测试")
    window.setGeometry(100, 100, 500, 400)
    
    # 创建中央控件
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # 创建布局
    layout = QVBoxLayout(central_widget)
    
    # 创建QueryWidget实例
    query_widget = QueryWidget()
    layout.addWidget(query_widget)
    
    # 连接信号到测试函数
    query_widget.query_requested.connect(on_query_requested)
    
    # 显示窗口
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())
