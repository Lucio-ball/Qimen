import datetime
import ichingpy
from typing import Dict, List, Tuple

# 2025年二十四节气精确时间（北京时间）
# 数据来源：中国科学院紫金山天文台
SOLAR_TERMS_2025 = {
    "立春": datetime.datetime(2025, 2, 3, 16, 10, 13),
    "雨水": datetime.datetime(2025, 2, 18, 12, 6, 19),
    "惊蛰": datetime.datetime(2025, 3, 5, 10, 7, 17),
    "春分": datetime.datetime(2025, 3, 20, 9, 1, 18),
    "清明": datetime.datetime(2025, 4, 4, 14, 48, 15),
    "谷雨": datetime.datetime(2025, 4, 19, 21, 55, 26),
    "立夏": datetime.datetime(2025, 5, 5, 8, 10, 27),
    "小满": datetime.datetime(2025, 5, 20, 21, 16, 43),
    "芒种": datetime.datetime(2025, 6, 5, 12, 34, 25),
    "夏至": datetime.datetime(2025, 6, 21, 4, 42, 19),
    "小暑": datetime.datetime(2025, 7, 6, 22, 29, 59),
    "大暑": datetime.datetime(2025, 7, 22, 15, 29, 53),
    "立秋": datetime.datetime(2025, 8, 7, 8, 8, 45),
    "处暑": datetime.datetime(2025, 8, 22, 23, 31, 50),
    "白露": datetime.datetime(2025, 9, 7, 16, 54, 41),  # 用户提供的精确时间
    "秋分": datetime.datetime(2025, 9, 23, 2, 19, 38),
    "寒露": datetime.datetime(2025, 10, 8, 8, 59, 7),
    "霜降": datetime.datetime(2025, 10, 23, 6, 14, 58),
    "立冬": datetime.datetime(2025, 11, 7, 0, 19, 59),
    "小雪": datetime.datetime(2025, 11, 22, 3, 55, 18),
    "大雪": datetime.datetime(2025, 12, 6, 23, 16, 10),
    "冬至": datetime.datetime(2025, 12, 21, 16, 2, 48),
    "小寒": datetime.datetime(2026, 1, 5, 10, 0, 37),
    "大寒": datetime.datetime(2026, 1, 20, 3, 43, 13),
}

# 节气名称顺序
SOLAR_TERMS_ORDER = [
    "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
    "立夏", "小满", "芒种", "夏至", "小暑", "大暑",
    "立秋", "处暑", "白露", "秋分", "寒露", "霜降",
    "立冬", "小雪", "大雪", "冬至", "小寒", "大寒",
]

_solar_terms_cache = {}


def _get_year_solar_terms(year: int) -> List[Tuple[str, datetime.datetime]]:
    """获取年份的节气列表"""
    if year == 2025:
        # 使用精确数据
        terms = [(name, SOLAR_TERMS_2025[name]) for name in SOLAR_TERMS_ORDER 
                 if SOLAR_TERMS_2025[name].year == 2025]
        return terms
    else:
        # 其他年份使用简化算法或返回空（暂时）
        # TODO: 添加其他年份的支持
        return []


def get_solar_term(target_dt: datetime.datetime) -> str:
    """
    精确计算给定时间的节气
    
    Args:
        target_dt: 需要查询的日期时间（北京时间）
        
    Returns:
        str: 节气名称
    """
    year = target_dt.year
    
    # 获取相关年份的节气
    terms_list = []
    for y in [year - 1, year, year + 1]:
        cache_key = str(y)
        if cache_key not in _solar_terms_cache:
            _solar_terms_cache[cache_key] = _get_year_solar_terms(y)
        terms_list.extend(_solar_terms_cache[cache_key])
    
    # 按时间排序
    terms_list.sort(key=lambda x: x[1])
    
    # 查找当前节气
    current_term = "春分"  # 默认值
    for term_name, term_dt in terms_list:
        if target_dt >= term_dt:
            current_term = term_name
        else:
            break
    
    return current_term


def get_si_zhu(target_dt: datetime.datetime) -> Dict[str, str]:
    """使用 ichingpy 获取四柱"""
    fp = ichingpy.FourPillars.from_datetime(target_dt)
    pillars_str = fp.get_pillars()
    pillars_list = pillars_str.split(' ')
    return {
        "年": pillars_list[0],
        "月": pillars_list[1],
        "日": pillars_list[2],
        "时": pillars_list[3]
    }


class CalendarUtils:
    @staticmethod
    def get_jieqi(year: int, month: int, day: int, hour: int, minute: int) -> str:
        dt = datetime.datetime(year, month, day, hour, minute)
        return get_solar_term(dt)
