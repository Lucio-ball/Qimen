"""
快速启动脚本 - 用于开发阶段快速启动应用
调用最新的集成版本 (IntegratedMainWindow)
"""
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 检查是否在PyInstaller环境中
if getattr(sys, 'frozen', False):
    # 如果是打包后的应用程序
    application_path = os.path.dirname(sys.executable)
    # 在PyInstaller环境中，模块已经打包，不需要添加路径
else:
    # 开发环境
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    from main_integrated import main  # 调用集成版本
    main()
