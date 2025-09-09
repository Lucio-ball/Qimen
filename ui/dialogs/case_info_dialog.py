"""
案例信息编辑对话框
Project: QMW-Persistence (Qi Men Workbench - Persistence Layer)
Task ID: FEAT-20250901-019-V2

用于编辑案例元信息（名称、问测人、事由详情）的对话框
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QLabel, QFileDialog,
    QMessageBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Optional


class CaseInfoDialog(QDialog):
    """案例信息编辑对话框"""
    
    def __init__(self, parent=None, mode="save_as", default_directory=None):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            mode: 对话框模式，"save_as"表示另存为模式，"edit"表示编辑模式
            default_directory: 默认目录路径（用于文件保存对话框）
        """
        super().__init__(parent)
        self.mode = mode
        self.default_directory = default_directory
        self.selected_filepath: Optional[str] = None
        
        self._init_ui()
        self._setup_connections()
        
    def _init_ui(self):
        """初始化用户界面"""
        if self.mode == "save_as":
            self.setWindowTitle("案例另存为")
        else:
            self.setWindowTitle("编辑案例信息")
            
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        # 主布局
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("案例信息")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 表单布局
        form_layout = QFormLayout()
        
        # 案例名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入案例名称...")
        form_layout.addRow("案例名称:", self.name_edit)
        
        # 问测人
        self.querent_edit = QLineEdit()
        self.querent_edit.setPlaceholderText("请输入问测人姓名...")
        form_layout.addRow("问测人:", self.querent_edit)
        
        # 事由详情
        self.details_edit = QTextEdit()
        self.details_edit.setPlaceholderText("请输入事由详情、背景信息等...")
        self.details_edit.setMaximumHeight(120)
        form_layout.addRow("事由详情:", self.details_edit)
        
        layout.addLayout(form_layout)
        
        # 文件路径显示（仅在另存为模式下显示）
        if self.mode == "save_as":
            self.filepath_layout = QHBoxLayout()
            
            # 根据是否有默认目录设置不同的提示
            if self.default_directory:
                self.filepath_label = QLabel("保存路径: 将自动保存到当前工作区")
                self.browse_button = QPushButton("更改保存位置...")
            else:
                self.filepath_label = QLabel("保存路径: 未选择")
                self.browse_button = QPushButton("选择保存位置...")
                
            self.filepath_label.setWordWrap(True)
            self.filepath_label.setStyleSheet("color: gray; font-style: italic;")
            
            self.browse_button.clicked.connect(self._browse_save_location)
            
            self.filepath_layout.addWidget(self.filepath_label, 1)
            self.filepath_layout.addWidget(self.browse_button)
            layout.addLayout(self.filepath_layout)
            
            # 如果有默认目录，自动设置默认保存路径
            if self.default_directory:
                self._set_default_save_path()
        
        # 按钮区域
        button_box = QDialogButtonBox()
        
        if self.mode == "save_as":
            self.save_button = button_box.addButton("保存", QDialogButtonBox.AcceptRole)
            self.save_button.setEnabled(False)  # 初始禁用，直到选择文件路径
        else:
            self.save_button = button_box.addButton("确定", QDialogButtonBox.AcceptRole)
        
        cancel_button = button_box.addButton("取消", QDialogButtonBox.RejectRole)
        
        layout.addWidget(button_box)
        
        # 连接按钮信号
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
    def _setup_connections(self):
        """设置信号连接"""
        # 名称输入变化时的验证和路径更新
        self.name_edit.textChanged.connect(self._validate_input)
        
        # 在另存为模式下，案例名称变化时更新默认路径
        if self.mode == "save_as" and self.default_directory:
            self.name_edit.textChanged.connect(self._update_default_path)
        
    def _set_default_save_path(self):
        """设置默认保存路径（当有工作区时自动生成）"""
        if not self.default_directory:
            return
            
        default_name = self.name_edit.text().strip() or "新案例"
        safe_name = self._make_filename_safe(default_name)
        
        # 生成默认保存路径
        default_filepath = os.path.join(self.default_directory, f"{safe_name}.qmw")
        
        # 如果文件已存在，添加序号
        counter = 1
        while os.path.exists(default_filepath):
            name_with_counter = f"{safe_name}_{counter}"
            default_filepath = os.path.join(self.default_directory, f"{name_with_counter}.qmw")
            counter += 1
        
        self.selected_filepath = default_filepath
        self.filepath_label.setText(f"保存路径: {default_filepath}")
        self.filepath_label.setStyleSheet("color: black;")
        
        # 启用保存按钮
        if hasattr(self, 'save_button'):
            self.save_button.setEnabled(True)
    
    def _update_default_path(self):
        """当案例名称变化时更新默认路径"""
        if self.default_directory and not self._manual_path_selected():
            self._set_default_save_path()
    
    def _manual_path_selected(self) -> bool:
        """检查用户是否手动选择了路径"""
        # 如果当前路径不在默认目录下，说明用户手动选择了路径
        if not self.selected_filepath or not self.default_directory:
            return False
        
        return not self.selected_filepath.startswith(self.default_directory)
    
    def _validate_input(self):
        """验证输入"""
        # 这里可以添加名称验证逻辑
        pass
    
    def _browse_save_location(self):
        """浏览保存位置"""
        default_name = self.name_edit.text().strip() or "新案例"
        
        # 确保文件名安全
        safe_name = self._make_filename_safe(default_name)
        
        # 构建默认路径
        if self.default_directory:
            default_path = os.path.join(self.default_directory, f"{safe_name}.qmw")
        else:
            default_path = f"{safe_name}.qmw"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "保存案例文件",
            default_path,
            "奇门遁甲案例文件 (*.qmw);;所有文件 (*)"
        )
        
        if filepath:
            # 确保文件扩展名为.qmw
            if not filepath.lower().endswith('.qmw'):
                filepath += '.qmw'
                
            self.selected_filepath = filepath
            self.filepath_label.setText(f"保存路径: {filepath}")
            self.filepath_label.setStyleSheet("color: black;")
            
            # 启用保存按钮
            self.save_button.setEnabled(True)
            
            # 如果案例名称为空，从文件名提取
            if not self.name_edit.text().strip():
                filename = os.path.splitext(os.path.basename(filepath))[0]
                self.name_edit.setText(filename)
                
    def _make_filename_safe(self, filename: str) -> str:
        """将字符串转换为安全的文件名"""
        # 移除或替换不安全的字符
        unsafe_chars = '<>:"/\\|?*'
        safe_filename = filename
        for char in unsafe_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # 移除前后空格并限制长度
        safe_filename = safe_filename.strip()[:50]
        
        return safe_filename or "新案例"
        
    def _validate_input(self):
        """验证输入内容"""
        name_valid = bool(self.name_edit.text().strip())
        
        if self.mode == "save_as":
            # 另存为模式需要同时有名称和文件路径
            self.save_button.setEnabled(name_valid and self.selected_filepath is not None)
        else:
            # 编辑模式只需要名称
            self.save_button.setEnabled(name_valid)
            
    def set_case_info(self, name: str, querent: str = "", details: str = ""):
        """
        设置案例信息
        
        Args:
            name: 案例名称
            querent: 问测人
            details: 事由详情
        """
        self.name_edit.setText(name)
        self.querent_edit.setText(querent)
        self.details_edit.setPlainText(details)
        
        # 触发验证
        self._validate_input()
        
    def get_case_info(self) -> dict:
        """
        获取用户输入的案例信息
        
        Returns:
            dict: 包含案例信息的字典
        """
        return {
            'name': self.name_edit.text().strip(),
            'querent': self.querent_edit.text().strip(),
            'details': self.details_edit.toPlainText().strip(),
            'filepath': self.selected_filepath
        }
        
    def get_filepath(self) -> Optional[str]:
        """获取选择的文件路径"""
        return self.selected_filepath
        
    def accept(self):
        """重写accept方法，添加验证"""
        case_info = self.get_case_info()
        
        if not case_info['name']:
            QMessageBox.warning(self, "警告", "请输入案例名称")
            self.name_edit.setFocus()
            return
        
        # 在另存为模式下验证保存路径
        if self.mode == "save_as":
            if not case_info['filepath']:
                # 如果有默认目录但没有设置路径，尝试设置默认路径
                if self.default_directory:
                    self._set_default_save_path()
                    case_info['filepath'] = self.selected_filepath
                
                # 如果仍然没有路径，提示用户
                if not case_info['filepath']:
                    QMessageBox.warning(self, "警告", "请选择保存位置")
                    return
            
        super().accept()


def test_dialog():
    """测试对话框"""
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 测试另存为模式
    dialog = CaseInfoDialog(mode="save_as")
    dialog.set_case_info("测试案例", "张三", "这是一个测试案例的详细描述...")
    
    if dialog.exec() == QDialog.Accepted:
        info = dialog.get_case_info()
        print("用户输入的信息:")
        print(f"  名称: {info['name']}")
        print(f"  问测人: {info['querent']}")
        print(f"  详情: {info['details']}")
        print(f"  路径: {info['filepath']}")
    else:
        print("用户取消了操作")
        
    sys.exit()


if __name__ == "__main__":
    test_dialog()
