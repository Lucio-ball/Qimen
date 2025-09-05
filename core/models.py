from typing import List, Dict, Union

class Palace:
    """代表九宫格中的一个宫"""
    def __init__(self, index: int):
        self.index: int = index
        self.god: str = ""
        self.stars: List[str] = []
        self.gates: str = ""
        self.heaven_stems: List[str] = []
        self.earth_stems: List[str] = []
        self.original_star: str = ""
        self.original_gate: str = ""
        self.wuxing_color: str = "" # e.g., '金'
        self.analysis: dict = {}  # 为未来的高级分析功能预留扩展点

    def __repr__(self) -> str:
        return (
            f"--- 宫 {self.index} ---\n"
            f" 八神: {self.god}\n"
            f" 九星: {', '.join(self.stars)}\n"
            f" 八门: {self.gates}\n"
            f" 天盘干: {', '.join(self.heaven_stems)}\n"
            f" 地盘干: {', '.join(self.earth_stems)}\n"
        )

class ChartResult:
    """封装完整的排盘结果"""
    def __init__(self):
        self.si_zhu: Dict[str, str] = {}
        self.jieqi: str = ""
        self.ju_shu_info: Dict[str, Union[str, int]] = {}
        self.shi_chen_xun: Dict[str, str] = {}
        self.zhi_fu: str = ""
        self.zhi_shi: str = ""
        self.ma_xing: str = ""
        self.kong_wang: Dict[str, List[str]] = {}
        self.palaces: List[Palace] = [Palace(i) for i in range(10)] # Index 0 is unused
        # 新的结构化标注数据，每个标注携带类型信息
        self.side_annotations: Dict[str, List[Dict[str, Union[str, bool]]]] = {}
        # 马星冲动目标分析结果 - 修正为复数形式
        self.maxing_chongdong_targets: List[Dict[str, str]] = []
        # 起局时间（用于显示）
        self.qi_ju_time: str = ""

    def __repr__(self) -> str:
        info_str = (
            f"四柱: {self.si_zhu['年']} {self.si_zhu['月']} {self.si_zhu['日']} {self.si_zhu['时']}\n"
            f"节气: {self.jieqi}\n"
            f"局数: {self.ju_shu_info['遁']}{self.ju_shu_info['局']}局\n"
            f"旬首: 甲{self.shi_chen_xun.get('zhi', '')}{self.shi_chen_xun.get('jun', '')}\n"
            f"值符: {self.zhi_fu}\n"
            f"值使: {self.zhi_shi}\n"
            f"马星: {self.ma_xing}\n"
            f"空亡: 日空({','.join(self.kong_wang.get('日空', []))}), 时空({','.join(self.kong_wang.get('时空', []))})\n"
        )
        palace_str = "".join([repr(p) for p in self.palaces if p.index != 0 and p.index != 5])
        palace_5_str = repr(self.palaces[5])
        return info_str + "\n" + palace_str + "\n" + palace_5_str
