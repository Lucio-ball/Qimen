"""
起局信息对话框 - QueryDialog
Project: QMW-CoreUI (Qi Men Workbench - Core UI)
Task ID: ARCH-20250901-012
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..widgets.query_widget import QueryWidget


class QueryDialog(QDialog):
    """
    起局信息对话框
    
    封装QueryWidget，通过模态对话框的形式收集起局信息
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.query_widget = None
        self._query_data = None  # 存储查询数据
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("新建案例 - 起局信息")
        self.setModal(True)
        self.setMinimumSize(400, 500)
        self.resize(500, 600)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题区域
        title_layout = QVBoxLayout()
        
        # 主标题
        title_label = QLabel("起局信息设置")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        title_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("请填写下方信息以创建新的奇门遁甲案例")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; font-size: 11px; margin-bottom: 15px;")
        title_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(title_layout)
        
        # QueryWidget区域（不显示内部按钮）
        self.query_widget = QueryWidget(self, show_query_button=False)
        
        main_layout.addWidget(self.query_widget)
        
        # 按钮区域
        button_box = QDialogButtonBox()
        
        # 确定按钮
        ok_button = button_box.addButton("立即起局", QDialogButtonBox.AcceptRole)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        
        # 取消按钮
        cancel_button = button_box.addButton("取消", QDialogButtonBox.RejectRole)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        
        main_layout.addWidget(button_box)
        
        self.button_box = button_box
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
    
    def _connect_signals(self):
        """连接信号槽"""
        self.button_box.accepted.connect(self._handle_accept)
        self.button_box.rejected.connect(self.reject)
        
        # 连接QueryWidget的query_requested信号
        if self.query_widget:
            self.query_widget.query_requested.connect(self._on_query_requested)
    
    def _on_query_requested(self, query_data):
        """
        处理QueryWidget的query_requested信号
        
        Args:
            query_data: QueryWidget发出的查询数据
        """
        # 存储数据并接受对话框
        self._query_data = query_data
        self.accept()
    
    def _handle_accept(self):
        """处理确定按钮点击"""
        # 手动触发QueryWidget的数据收集和验证逻辑
        if self.query_widget and hasattr(self.query_widget, '_emit_query_request'):
            # 调用QueryWidget的内部方法来收集数据
            self.query_widget._emit_query_request()
            # 注意：_emit_query_request会发出query_requested信号，
            # 我们的_on_query_requested方法会处理这个信号并调用self.accept()
        else:
            # 兜底处理：直接接受
            self.accept()
    
    def get_data(self):
        """
        获取起局数据
        
        Returns:
            dict: 包含起局信息的字典
        """
        if self._query_data:
            return self._query_data
        
        # 兜底处理：如果没有存储的数据，尝试从QueryWidget直接获取
        if self.query_widget:
            try:
                import datetime
                
                # 尝试获取时间信息
                time_text = self.query_widget.time_input.text() if hasattr(self.query_widget, 'time_input') else ""
                
                # 解析时间（假设格式为YYYYMMDDHHMM）
                if len(time_text) >= 10:
                    year = int(time_text[:4])
                    month = int(time_text[4:6])
                    day = int(time_text[6:8])
                    hour = int(time_text[8:10])
                    minute = int(time_text[10:12]) if len(time_text) >= 12 else 0
                    
                    query_time = datetime.datetime(year, month, day, hour, minute)
                    
                    return {
                        'query_time': query_time,
                        'nian_ming': getattr(self.query_widget, 'gan_zhi_label', QLabel()).text() if hasattr(self.query_widget, 'gan_zhi_label') else '',
                        'notes': self.query_widget.notes_edit.toPlainText() if hasattr(self.query_widget, 'notes_edit') else ''
                    }
            except:
                pass
        
        # 最终兜底：返回当前时间
        import datetime
        return {
            'query_time': datetime.datetime.now(),
            'nian_ming': '',
            'notes': ''
        }
    
    def exec(self):
        """重写exec方法，确保在显示前设置合适的位置"""
        if self.parent():
            # 如果有父窗口，居中显示
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        
        return super().exec()
