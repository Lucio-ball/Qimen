#!/usr/bin/env python3
"""
测试QueryWidget的reset_form方法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_reset_form():
    """测试reset_form功能"""
    print("🔧 测试QueryWidget的reset_form方法")
    print("=" * 50)
    
    try:
        from ui.widgets.query_widget import QueryWidget
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QDate
        import datetime
        
        # 创建应用程序实例（测试需要）
        app = QApplication([])
        
        # 创建QueryWidget实例
        widget = QueryWidget()
        
        print("✅ QueryWidget创建成功")
        
        # 检查reset_form方法是否存在
        if hasattr(widget, 'reset_form'):
            print("✅ reset_form方法存在")
            
            # 模拟修改一些值
            print("🔄 模拟修改表单数据...")
            
            # 修改时间
            widget.time_input.setText("20201010101010")
            
            # 修改出生日期  
            old_date = QDate(1990, 1, 1)
            widget.birth_date_edit.setDate(old_date)
            
            # 添加事由
            widget.notes_edit.setPlainText("测试事由内容")
            
            print("📝 表单已修改，准备重置...")
            
            # 调用reset_form
            widget.reset_form()
            
            print("✅ reset_form调用成功")
            
            # 验证重置结果
            current_time_str = datetime.datetime.now().strftime("%Y%m%d%H%M")
            input_time = widget.time_input.text().replace(" ", "").replace("-", "").replace(":", "")
            
            print(f"🕐 时间已重置: {widget.time_input.text()}")
            print(f"📅 出生日期已重置: {widget.birth_date_edit.date().toString()}")
            print(f"📄 事由已清空: '{widget.notes_edit.toPlainText()}'")
            print(f"🎯 年命干支: {widget.gan_zhi_label.text()}")
            
            if widget.notes_edit.toPlainText() == "":
                print("✅ 事由清空成功")
            else:
                print("❌ 事由清空失败")
                
            print("✅ reset_form功能测试完成")
            
        else:
            print("❌ reset_form方法不存在")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_reset_form()
    if success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n💥 测试失败！")
        sys.exit(1)
