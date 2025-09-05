import json
import datetime
from typing import Dict, List, Any, Union
from .models import Palace, ChartResult
from .calendar_utils import get_solar_term, get_si_zhu

# 定义九宫飞布路径，用于排盘旋转
LUO_SHU_PATH = [1, 8, 3, 4, 9, 2, 7, 6]


class PaiPanEngine:
    """奇门遁甲排盘引擎"""

    def __init__(self, data_file_path='data.json'):
        """
        构造函数，加载数据文件
        """
        try:
            with open(data_file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            raise Exception(f"错误: 数据文件 '{data_file_path}' 未找到。")
        except json.JSONDecodeError:
            raise Exception(f"错误: 数据文件 '{data_file_path}' 格式不正确。")

    def paipan(self, time_str: str) -> ChartResult:
        """
        公共排盘方法
        :param time_str: "yyyymmddhhmmss" 格式的14位时间字符串
        """
        if len(time_str) != 14 or not time_str.isdigit():
            raise ValueError("时间字符串格式错误，应为 'yyyymmddhhmmss'")

        target_dt = datetime.datetime.strptime(time_str, '%Y%m%d%H%M%S')
        return self._internal_paipan(target_dt)

    def _internal_paipan(self, target_dt: datetime.datetime) -> ChartResult:
        """
        内部排盘主流程
        """
        result = ChartResult()
        
        # 设置起局时间（用于界面显示）
        result.qi_ju_time = target_dt.strftime("%Y年%m月%d日 %H:%M")

        # 步骤 1 & 2: 计算节气与四柱
        result.jieqi = get_solar_term(target_dt)
        result.si_zhu = get_si_zhu(target_dt)
        ri_zhu = result.si_zhu['日']
        shi_zhu = result.si_zhu['时']

        # 步骤 3: 获得局数
        yuan = self._find_yuan(ri_zhu[0], ri_zhu[1])
        result.ju_shu_info = self._find_ju_shu(result.jieqi, yuan)

        # 步骤 4: 排地盘天干
        di_pan_stems = self._layout_di_pan(result.ju_shu_info)

        # 步骤 5: 确定值符值使
        result.shi_chen_xun = self._find_shi_chen_xun(shi_zhu[0], shi_zhu[1])
        zhi_fu_star, result.zhi_shi, fu_tou_palace = self._find_zhi_fu_zhi_shi(result.shi_chen_xun, di_pan_stems)
        result.zhi_fu = zhi_fu_star['cn']

        # 步骤 6: 排八神
        ba_shen_layout = self._layout_ba_shen(shi_zhu[0], di_pan_stems, result.ju_shu_info, result.shi_chen_xun)

        # 步骤 7: 排天盘干与九星
        tian_pan_stems, tian_pan_stars = self._layout_tian_pan_and_stars(shi_zhu[0], di_pan_stems, zhi_fu_star,
                                                                         result.shi_chen_xun)

        # 步骤 8: 排八门
        ba_men_layout = self._layout_ba_men(shi_zhu[1], result.shi_chen_xun['zhi'], result.zhi_shi, result.ju_shu_info)

        # 步骤 9: 整合结果
        result.ma_xing = self._find_ma_xing(shi_zhu[1])
        result.kong_wang = self._find_kong_wang(ri_zhu, shi_zhu)

        # 填充九宫信息
        palace_wuxing = {1: '水', 2: '土', 3: '木', 4: '木', 6: '金', 7: '金', 8: '土', 9: '火', 5: '土'}
        original_stars = {p['guxiang']: p['cn'] for p in self.data['jiuXing']}
        original_gates = {p['guxiang']: p['cn'] for p in self.data['baMen']}

        for i in range(1, 10):
            p = result.palaces[i]
            p.earth_stems = di_pan_stems[i]
            p.heaven_stems = tian_pan_stems[i]
            p.stars = tian_pan_stars[i]
            p.gates = ba_men_layout[i]
            p.god = ba_shen_layout[i]
            p.wuxing_color = palace_wuxing[i]
            p.original_star = original_stars.get(i, "禽")
            p.original_gate = original_gates.get(i, "")

        # 步骤 10: 计算宫侧方自动标注
        result.side_annotations = self._calculate_annotations(result, di_pan_stems, tian_pan_stems)
        
        # 步骤 11: 分析马星冲动
        result.maxing_chongdong_targets = self._analyze_maxing_chongdong(result)

        return result

    def _find_yuan(self, ri_gan: str, ri_zhi: str) -> str:
        for jiazi in self.data['liuShiJiaZi']:
            if jiazi['gan'] == ri_gan and jiazi['zhi'] == ri_zhi:
                return jiazi['yuan']
        raise ValueError("未找到日柱对应的元")

    def _find_ju_shu(self, jieqi: str, yuan: str) -> Dict[str, Any]:
        info = self.data['jieQiJuShu'][jieqi]
        return {"遁": info['yinyang'], "局": info['jv'][yuan]}

    def _layout_di_pan(self, ju_shu_info: Dict) -> List[List[str]]:
        stems_order = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]
        di_pan = [[] for _ in range(10)]
        start_pos = ju_shu_info['局']

        if ju_shu_info['遁'] == '阳遁':
            for i, stem in enumerate(stems_order):
                palace_index = (start_pos + i - 1) % 9 + 1
                di_pan[palace_index].append(stem)
        else:  # 阴遁
            for i, stem in enumerate(stems_order):
                palace_index = (start_pos - i - 1 + 9) % 9 + 1
                di_pan[palace_index].append(stem)

        if di_pan[5]:
            di_pan[2].extend(di_pan[5])

        return di_pan

    def _find_shi_chen_xun(self, shi_gan: str, shi_zhi: str) -> Dict[str, str]:
        for jiazi in self.data['liuShiJiaZi']:
            if jiazi['gan'] == shi_gan and jiazi['zhi'] == shi_zhi:
                return jiazi['xun']
        raise ValueError("未找到时柱对应的旬")

    def _find_stem_palace(self, stem: str, di_pan_stems: List[List[str]], shi_chen_xun: Dict[str, str]) -> int:
        target_stem = stem
        if stem == "甲":
            target_stem = shi_chen_xun['jun']

        for i in range(1, 10):
            if target_stem in di_pan_stems[i]:
                return i

        return -1

    def _find_zhi_fu_zhi_shi(self, shi_chen_xun: Dict, di_pan_stems: List[List[str]]) -> tuple[Dict, str, int]:
        jun_gan = shi_chen_xun['jun']
        fu_tou_palace = -1
        for i in range(1, 10):
            if jun_gan in di_pan_stems[i]:
                fu_tou_palace = i
                break

        original_star = next((s for s in self.data['jiuXing'] if s['guxiang'] == fu_tou_palace), None)
        original_gate = next((g for g in self.data['baMen'] if g['guxiang'] == fu_tou_palace), None)

        if fu_tou_palace == 5:
            zhi_fu_star = next(s for s in self.data['jiuXing'] if s['cn'] == '禽')
            zhi_shi_gate_cn = next(g for g in self.data['baMen'] if g['guxiang'] == 2)['cn']
        else:
            zhi_fu_star = original_star
            zhi_shi_gate_cn = original_gate['cn']

        return zhi_fu_star, zhi_shi_gate_cn, fu_tou_palace

    def _layout_ba_shen(self, shi_gan: str, di_pan_stems: List[List[str]], ju_shu_info: Dict, shi_chen_xun: Dict) -> \
    List[str]:
        gods_order = ["符", "蛇", "阴", "合", "虎", "武", "地", "天"]
        layout = [""] * 10

        shi_gan_palace = self._find_stem_palace(shi_gan, di_pan_stems, shi_chen_xun)

        if shi_gan_palace == -1:
            raise ValueError(f"无法在地盘上找到时干 '{shi_gan}' 或其遁藏位置")

        layout[shi_gan_palace] = "符"

        path_index = LUO_SHU_PATH.index(shi_gan_palace)

        if ju_shu_info['遁'] == '阳遁':
            for i in range(1, 8):
                current_palace = LUO_SHU_PATH[(path_index + i) % 8]
                layout[current_palace] = gods_order[i]
        else:
            for i in range(1, 8):
                current_palace = LUO_SHU_PATH[(path_index - i + 8) % 8]
                layout[current_palace] = gods_order[i]

        return layout

    def _layout_tian_pan_and_stars(self, shi_gan: str, di_pan_stems: List[List[str]], zhi_fu_star: Dict,
                                   shi_chen_xun: Dict) -> tuple[List[List[str]], List[List[str]]]:
        tian_pan_stems = [[] for _ in range(10)]
        tian_pan_stars = [[] for _ in range(10)]

        zhi_fu_palace = self._find_stem_palace(shi_gan, di_pan_stems, shi_chen_xun)

        if zhi_fu_palace == -1:
            raise ValueError(f"无法在地盘上找到时干(值符) '{shi_gan}' 或其遁藏位置")

        stars_order_cn = ["蓬", "任", "冲", "辅", "英", "芮", "柱", "心"]
        qin_star = next(s for s in self.data['jiuXing'] if s['cn'] == '禽')

        start_star_index = stars_order_cn.index(zhi_fu_star['cn']) if zhi_fu_star[
                                                                          'cn'] != '禽' else stars_order_cn.index('芮')
        path_start_index = LUO_SHU_PATH.index(zhi_fu_palace)

        for i in range(8):
            current_star_cn = stars_order_cn[(start_star_index + i) % 8]
            current_star_obj = next(s for s in self.data['jiuXing'] if s['cn'] == current_star_cn)
            current_path_palace = LUO_SHU_PATH[(path_start_index + i) % 8]

            tian_pan_stars[current_path_palace].append(current_star_cn)
            tian_pan_stems[current_path_palace].extend(di_pan_stems[current_star_obj['guxiang']])

        rui_palace = -1
        for i, stars in enumerate(tian_pan_stars):
            if "芮" in stars:
                rui_palace = i
                break

        if rui_palace != -1:
            tian_pan_stars[rui_palace].append("禽")

        tian_pan_stems[5].extend(di_pan_stems[qin_star['guxiang']])
        tian_pan_stars[5].append("禽")

        return tian_pan_stems, tian_pan_stars

    def _layout_ba_men(self, shi_zhi: str, xun_zhi: str, zhi_shi_cn: str, ju_shu_info: Dict) -> List[str]:
        layout = [""] * 10
        di_zhi_order = [d['cn'] for d in self.data['diZhi']]
        offset = (di_zhi_order.index(shi_zhi) - di_zhi_order.index(xun_zhi) + 12) % 12
        zhi_shi_obj = next(g for g in self.data['baMen'] if g['cn'] == zhi_shi_cn)
        start_palace = zhi_shi_obj['guxiang']

        if ju_shu_info['遁'] == '阳遁':
            zhi_shi_luo_gong = (start_palace + offset - 1) % 9 + 1
        else:
            zhi_shi_luo_gong = (start_palace - offset - 1 + 9) % 9 + 1

        if zhi_shi_luo_gong == 5:
            zhi_shi_luo_gong = 2

        men_order_cn = ["休", "生", "伤", "杜", "景", "死", "惊", "开"]
        men_start_index = men_order_cn.index(zhi_shi_cn)
        luo_gong_path_index = LUO_SHU_PATH.index(zhi_shi_luo_gong)

        for i in range(8):
            current_men_cn = men_order_cn[(men_start_index + i) % 8]
            current_palace = LUO_SHU_PATH[(luo_gong_path_index + i) % 8]
            layout[current_palace] = current_men_cn

        return layout

    # --- 【补全的函数】 ---
    def _find_ma_xing(self, shi_zhi: str) -> str:
        ma_xing_map = {
            "寅": "申", "午": "申", "戌": "申",
            "亥": "巳", "卯": "巳", "未": "巳",
            "申": "寅", "子": "寅", "辰": "寅",
            "巳": "亥", "酉": "亥", "丑": "亥"
        }
        return ma_xing_map.get(shi_zhi, "")

    def _find_kong_wang(self, ri_zhu: str, shi_zhu: str) -> Dict[str, List[str]]:
        ri_xun = self._find_shi_chen_xun(ri_zhu[0], ri_zhu[1])
        shi_xun = self._find_shi_chen_xun(shi_zhu[0], shi_zhu[1])

        ri_kong = next(j['kong'] for j in self.data['liuShiJiaZi'] if j['xun']['zhi'] == ri_xun['zhi'])
        shi_kong = next(j['kong'] for j in self.data['liuShiJiaZi'] if j['xun']['zhi'] == shi_xun['zhi'])

        return {"日空": ri_kong, "时空": shi_kong}

    def _calculate_annotations(self, result: ChartResult, di_pan_stems: List[List[str]], 
                             tian_pan_stems: List[List[str]]) -> Dict[str, List[Dict[str, Union[str, bool]]]]:
        """
        计算宫侧方自动标注 - 结构化版本
        返回格式: {"子": [{"type": "liuji", "text": "戊击刑", "strike": False}], ...}
        """
        # 初始化标注字典
        annotations = {zhi: [] for zhi in ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]}
        
        # 分析各种标注
        self._analyze_liu_ji_structured(annotations, di_pan_stems, tian_pan_stems)
        self._analyze_ru_mu_structured(annotations, di_pan_stems, tian_pan_stems)
        self._analyze_kong_wang_structured(annotations, result)
        self._analyze_yue_wang_ma_xing_structured(annotations, result)
        
        # 处理双标注
        self._process_double_annotations_structured(annotations)
        
        return annotations
    
    def _analyze_liu_ji_structured(self, annotations: Dict[str, List[Dict[str, Union[str, bool]]]], 
                                 di_pan_stems: List[List[str]], tian_pan_stems: List[List[str]]):
        """
        分析击刑情况 - 结构化版本
        精确映射: 戊→卯, 己→未, 庚→寅, 辛→午, 壬→辰, 癸→巳
        """
        ji_xing_rules = {
            "戊": (3, "卯"),  # 震3宫 -> 卯位
            "己": (2, "未"),  # 坤2宫 -> 未位
            "庚": (8, "寅"),  # 艮8宫 -> 寅位
            "辛": (9, "午"),  # 离9宫 -> 午位
            "壬": (4, "辰"),  # 巽4宫 -> 辰位
            "癸": (4, "巳"),  # 巽4宫 -> 巳位
        }
        
        # 检查天盘干和地盘干是否击刑
        for gan, (gong, target_zhi) in ji_xing_rules.items():
            # 合并天盘干和地盘干
            all_gan_list = tian_pan_stems[gong] + di_pan_stems[gong]
            
            if gan in all_gan_list:
                annotations[target_zhi].append({
                    "type": "liuji",
                    "text": f"{gan}击刑",
                    "strike": False
                })
    
    def _analyze_ru_mu_structured(self, annotations: Dict[str, List[Dict[str, Union[str, bool]]]], 
                                di_pan_stems: List[List[str]], tian_pan_stems: List[List[str]]):
        """
        分析入墓情况 - 结构化版本
        精确映射: 艮8→丑, 巽4→辰, 坤2→未, 乾6→戌
        """
        ru_mu_rules = {
            8: (["丁", "己", "庚"], "丑"),  # 艮8宫 -> 丑位
            4: (["辛", "壬"], "辰"),        # 巽4宫 -> 辰位
            2: (["乙", "癸"], "未"),        # 坤2宫 -> 未位
            6: (["丙", "戊"], "戌"),        # 乾6宫 -> 戌位
        }
        
        # 检查天盘干和地盘干是否入墓
        for gong, (gan_list, target_zhi) in ru_mu_rules.items():
            # 合并天盘干和地盘干
            all_gan_list = tian_pan_stems[gong] + di_pan_stems[gong]
            
            for gan in all_gan_list:
                if gan in gan_list:
                    annotations[target_zhi].append({
                        "type": "rumu",
                        "text": f"{gan}入墓",
                        "strike": False
                    })
    
    def _analyze_kong_wang_structured(self, annotations: Dict[str, List[Dict[str, Union[str, bool]]]], 
                                    result: ChartResult):
        """
        分析空亡情况 - 结构化版本
        月令空亡用strike标识
        """
        yue_zhi = result.si_zhu['月'][1]  # 获取月支
        
        # 检查日空
        for kong_zhi in result.kong_wang.get('日空', []):
            is_strike = kong_zhi == yue_zhi
            annotations[kong_zhi].append({
                "type": "rikong",
                "text": "日空",
                "strike": is_strike
            })
        
        # 检查时空
        for kong_zhi in result.kong_wang.get('时空', []):
            is_strike = kong_zhi == yue_zhi
            annotations[kong_zhi].append({
                "type": "shikong", 
                "text": "时空",
                "strike": is_strike
            })
    
    def _analyze_yue_wang_ma_xing_structured(self, annotations: Dict[str, List[Dict[str, Union[str, bool]]]], 
                                           result: ChartResult):
        """
        分析月旺与马星 - 结构化版本
        """
        # 月令旺气 - 只标注月支本身
        yue_zhi = result.si_zhu['月'][1]
        annotations[yue_zhi].append({
            "type": "yueling",
            "text": "月令",
            "strike": False
        })
        
        # 马星 - 只标注马星地支本身
        if result.ma_xing:
            annotations[result.ma_xing].append({
                "type": "maxing",
                "text": "马星",
                "strike": False
            })
    
    def _process_double_annotations_structured(self, annotations: Dict[str, List[Dict[str, Union[str, bool]]]]):
        """
        处理双标注，将重复的标注合并为"双X..."格式 - 结构化版本
        特别处理日空+时空的情况，合并为"双X空"格式（包含地支名）
        """
        for di_zhi in annotations:
            annotation_list = annotations[di_zhi]
            if len(annotation_list) <= 1:
                continue
                
            # 统计每种类型的标注
            type_count = {}
            for annotation in annotation_list:
                ann_type = annotation["type"]
                type_count[ann_type] = type_count.get(ann_type, 0) + 1
            
            # 特殊处理日空+时空的情况
            has_ri_kong = any(ann["type"] == "rikong" for ann in annotation_list)
            has_shi_kong = any(ann["type"] == "shikong" for ann in annotation_list)
            
            # 重新构建标注列表
            new_annotations = []
            processed_kong = False
            processed_rumu = False
            
            for annotation in annotation_list:
                ann_type = annotation["type"]
                
                # 处理空亡的双标注
                if ann_type in ["rikong", "shikong"] and not processed_kong:
                    if has_ri_kong and has_shi_kong:
                        # 检查是否有删除线标注
                        has_strike = any(ann["strike"] for ann in annotation_list 
                                       if ann["type"] in ["rikong", "shikong"])
                        new_annotations.append({
                            "type": "shuangkong",  # 可以定义新类型或选择其一
                            "text": f"双{di_zhi}空",
                            "strike": has_strike
                        })
                        processed_kong = True
                    else:
                        new_annotations.append(annotation)
                # 处理入墓的双标注 - 特殊逻辑
                elif ann_type == "rumu" and type_count[ann_type] >= 2 and not processed_rumu:
                    # 收集所有入墓标注，按干支分组
                    rumu_annotations = [ann for ann in annotation_list if ann["type"] == "rumu"]
                    gan_count = {}
                    
                    # 统计每个干的出现次数
                    for rumu_ann in rumu_annotations:
                        gan = rumu_ann["text"].replace("入墓", "")
                        gan_count[gan] = gan_count.get(gan, 0) + 1
                    
                    # 根据每个干的出现次数生成标注
                    for gan, count in gan_count.items():
                        if count >= 2:
                            # 同一个干出现多次，用"双X入墓"
                            text = f"双{gan}入墓"
                        else:
                            # 单个干，用"X入墓"
                            text = f"{gan}入墓"
                        
                        # 检查是否有删除线（继承原标注的strike状态）
                        has_strike = any(ann["strike"] for ann in rumu_annotations 
                                       if ann["text"] == f"{gan}入墓")
                        
                        new_annotations.append({
                            "type": ann_type,
                            "text": text,
                            "strike": has_strike
                        })
                    
                    processed_rumu = True
                # 处理其他标注的双标注
                elif type_count[ann_type] >= 2 and ann_type != "rumu":
                    # 找到同类型的第一个标注
                    if annotation == next(ann for ann in annotation_list if ann["type"] == ann_type):
                        new_annotations.append({
                            "type": ann_type,
                            "text": f"双{annotation['text']}",
                            "strike": annotation["strike"]
                        })
                elif ann_type not in ["rikong", "shikong", "rumu"] or (not processed_kong and not processed_rumu):
                    new_annotations.append(annotation)
            
            annotations[di_zhi] = new_annotations
    
    def _analyze_maxing_chongdong(self, result: ChartResult) -> List[Dict[str, str]]:
        """
        分析马星冲动逻辑 - V2版本
        严格按照优先级顺序：本宫入墓 > 对宫入墓 > 本宫空亡 > 对宫空亡
        一旦在某个步骤找到任何目标，就收集该宫位内所有同类型目标，然后立即返回
        
        Returns:
            List[Dict[str, str]]: 所有被冲动的标注对象列表
        """
        if not result.ma_xing:
            return []
            
        # A. 核心数据与映射关系
        dui_gong_map = {1: 9, 9: 1, 2: 8, 8: 2, 3: 7, 7: 3, 4: 6, 6: 4}
        zhi_to_gong_map = {
            "子": 1, "丑": 8, "寅": 8, "卯": 3, "辰": 4, "巳": 4,
            "午": 9, "未": 2, "申": 2, "酉": 7, "戌": 6, "亥": 6
        }
        gong_to_zhi_list_map = {
            1: ["子"], 2: ["未", "申"], 3: ["卯"], 4: ["辰", "巳"], 5: [], 
            6: ["戌", "亥"], 7: ["酉"], 8: ["丑", "寅"], 9: ["午"]
        }
        
        # 初始化
        ma_xing_zhi = result.ma_xing
        ben_gong_index = zhi_to_gong_map[ma_xing_zhi]
        dui_gong_index = dui_gong_map.get(ben_gong_index)
        
        # Step 1: 检查本宫入墓
        targets = self._find_targets_in_gong(ben_gong_index, "rumu", result.side_annotations, gong_to_zhi_list_map)
        if targets:
            return targets
            
        # Step 2: 检查对宫入墓
        if dui_gong_index is not None:
            targets = self._find_targets_in_gong(dui_gong_index, "rumu", result.side_annotations, gong_to_zhi_list_map)
            if targets:
                return targets
                
        # Step 3: 检查本宫空亡
        targets = self._find_targets_in_gong(ben_gong_index, ["rikong", "shikong"], result.side_annotations, gong_to_zhi_list_map)
        if targets:
            return targets
            
        # Step 4: 检查对宫空亡
        if dui_gong_index is not None:
            targets = self._find_targets_in_gong(dui_gong_index, ["rikong", "shikong"], result.side_annotations, gong_to_zhi_list_map)
            if targets:
                return targets
                
        # Step 5: 无目标
        return []
        
    def _find_targets_in_gong(self, gong_index: int, target_types: Union[str, List[str]], 
                             all_annotations: Dict[str, List[Dict[str, Union[str, bool]]]], 
                             gong_to_zhi_list_map: Dict[int, List[str]]) -> List[Dict[str, str]]:
        """
        在指定宫位中查找匹配类型的所有标注目标
        
        Args:
            gong_index: 目标宫位 (1-9)
            target_types: 目标类型 (字符串或字符串列表)
            all_annotations: 所有标注数据
            gong_to_zhi_list_map: 宫位到地支列表的映射
            
        Returns:
            List[Dict[str, str]]: 找到的所有目标对象列表
        """
        found_targets = []
        
        # 标准化target_types为列表
        if isinstance(target_types, str):
            target_types = [target_types]
            
        # 获取该宫位对应的所有地支列表
        zhi_list = gong_to_zhi_list_map.get(gong_index, [])
        
        # 遍历该宫位的所有地支
        for zhi in zhi_list:
            annotations = all_annotations.get(zhi, [])
            
            # 遍历该地支位置的所有标注
            for anno in annotations:
                if anno.get('type') in target_types:
                    found_targets.append({
                        "type": anno.get('type'),
                        "location_zhi": zhi,
                        "text": anno.get('text', anno.get('type', ''))
                    })
                    
        return found_targets
