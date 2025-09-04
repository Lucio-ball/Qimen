"""
奇门遁甲工作台 - 集成版本程序入口点
Task ID: UI-20250901-010

完整集成版本的程序入口，包含QueryWidget、ChartWidget和AttributePanelWidget
"""

import sys
from ui.app_integrated import run_integrated


def main():
    """程序主入口函数 - 集成版本"""
    return run_integrated()


if __name__ == "__main__":
    sys.exit(main())
