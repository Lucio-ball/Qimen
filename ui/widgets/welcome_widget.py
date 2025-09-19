"""
欢迎页面组件 - WelcomeWidget
Project: QMW-CoreUI (Qi Men Workbench - Core UI)
Task ID: ARCH-20250901-012
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap


class WelcomeWidget(QWidget):
    """
    欢迎页面组件
    
    显示欢迎信息和新建案例按钮，用于在没有任何案例打开时显示
    """
    
    # 信号：新建案例按钮被点击
    new_case_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        
        # 顶部空白区域
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        title_layout.setSpacing(15)
        
        # 主标题
        title_label = QLabel("欢迎使用奇门遁甲工作台")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 20px;")
        title_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("QMW-CoreUI 多案例管理工作台")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        title_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(title_layout)
        
        # 描述文本区域
        description_layout = QVBoxLayout()
        description_layout.setAlignment(Qt.AlignCenter)
        description_layout.setSpacing(10)
        
        # 功能描述
        features = [
            "• 支持多案例同时管理",
            "• 专业级奇门遁甲排盘",
            "• 直观的标签页界面",
            "• 完整的分析功能"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setAlignment(Qt.AlignCenter)
            feature_label.setStyleSheet("color: #34495e; font-size: 11px; margin: 2px;")
            description_layout.addWidget(feature_label)
        
        main_layout.addLayout(description_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        # 新建案例按钮
        self.new_case_button = QPushButton("+ 新建案例")
        self.new_case_button.setMinimumSize(200, 50)
        self.new_case_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        button_layout.addWidget(self.new_case_button)
        
        main_layout.addLayout(button_layout)
        
        # 底部空白区域
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # 版本信息
        version_label = QLabel("版本 v1.1 | RELEASE-20250919-001")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #bdc3c7; font-size: 9px; margin: 10px;")
        main_layout.addWidget(version_label)
        
        # 设置整体背景
        self.setStyleSheet("""
            WelcomeWidget {
                background-color: #ecf0f1;
            }
        """)
    
    def _connect_signals(self):
        """连接信号槽"""
        self.new_case_button.clicked.connect(self.new_case_requested.emit)
