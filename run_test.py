from core.paipan_engine import PaiPanEngine

# 主程序入口
if __name__ == "__main__":
    # 创建引擎实例，它会自动加载 'data.json'
    # 确保这个脚本和 'data.json' 以及 'core' 文件夹在同一目录下
    try:
        engine = PaiPanEngine(data_file_path='data.json')

        # 定义一个要排盘的时间 (格式: YYYYMMDDHHMMSS)
        # 例如: 2024年6月21日 15点30分00秒
        test_time_str = input("input:")
        test_time_str += "00"
        # 调用排盘方法
        chart_result = engine.paipan(test_time_str)

        # 打印完整的排盘结果 (ChartResult的__repr__方法会被自动调用)
        print(f"====== 时间: {test_time_str} 的奇门遁甲盘 ======")
        print(chart_result)

    except Exception as e:
        print(f"程序发生错误: {e}")

