"""
快速启动脚本 - 用于开发阶段快速启动应用
"""
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    from main import main
    main()
