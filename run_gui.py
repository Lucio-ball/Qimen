"""
快速启动脚本 - 用于开发阶段快速启动应用
调用最新的集成版本 (IntegratedMainWindow)
"""
import sys
import os


def _reexec_with_venv_if_available() -> None:
    """如果存在项目本地虚拟环境(.venv)，且当前解释器不是它，则用它重启。

    目的：避免用户用 `py run_gui.py` 触发系统 Python 缺包（例如 sxtwl）。
    """
    if getattr(sys, 'frozen', False):
        return

    project_root = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_root, ".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        return

    try:
        current = os.path.normcase(os.path.abspath(sys.executable))
        target = os.path.normcase(os.path.abspath(venv_python))
        if current == target:
            return
        os.execv(venv_python, [venv_python, *sys.argv])
    except Exception:
        # 如果重启失败，继续用当前解释器运行，让后续 import 抛出更明确的错误
        return

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
    _reexec_with_venv_if_available()
    from ui.app_integrated import run_integrated  # 调用集成版本
    sys.exit(run_integrated())
