import datetime
import ichingpy
from bisect import bisect_right
from typing import Dict, List, Tuple

try:
    import sxtwl
except ModuleNotFoundError as e:  # pragma: no cover
    raise ModuleNotFoundError(
        "缺少依赖包 'sxtwl'（节气必须使用天文历算）。请先安装 requirements.txt，"
        "或使用项目本地虚拟环境 .venv 的解释器运行。"
    ) from e

_solar_terms_cache = {}


# sxtwl.jqIndex -> 节气名称（与 sxtwl 的 24 节气索引一致）
_JIEQI_NAMES_BY_INDEX = {
    0: "冬至",
    1: "小寒",
    2: "大寒",
    3: "立春",
    4: "雨水",
    5: "惊蛰",
    6: "春分",
    7: "清明",
    8: "谷雨",
    9: "立夏",
    10: "小满",
    11: "芒种",
    12: "夏至",
    13: "小暑",
    14: "大暑",
    15: "立秋",
    16: "处暑",
    17: "白露",
    18: "秋分",
    19: "寒露",
    20: "霜降",
    21: "立冬",
    22: "小雪",
    23: "大雪",
}


def _jd_to_beijing_datetime(jd: float) -> datetime.datetime:
    """将 sxtwl 的儒略日(JD)转换为北京时间 datetime（四舍五入到秒）。"""
    t = sxtwl.JD2DD(jd)

    sec_float = float(t.getSec())
    sec_int = int(sec_float)
    micro = int(round((sec_float - sec_int) * 1_000_000))
    if micro >= 1_000_000:
        # 处理四舍五入导致的进位
        sec_int += 1
        micro -= 1_000_000

    base = datetime.datetime(
        int(t.getYear()),
        int(t.getMonth()),
        int(t.getDay()),
        int(t.getHour()),
        int(t.getMin()),
        sec_int,
        micro,
    )
    # 秒级口径：按最近秒取整（满足“到秒”的命理边界要求）
    base = base + datetime.timedelta(microseconds=500_000)
    base = base.replace(microsecond=0)

    # sxtwl 输出的 Time 为北京时间口径（UTC+8）
    return base


def _get_year_solar_terms(year: int) -> List[Tuple[str, datetime.datetime]]:
    """获取年份的节气列表"""
    # 使用 sxtwl（天文历算）获取交节时刻；不使用近似公式/固定表。
    # 注意：sxtwl.getJieQiByYear(year) 返回从当年立春起到次年立春(含)的交节序列（长度通常为25）。
    terms: List[Tuple[str, datetime.datetime]] = []
    for info in sxtwl.getJieQiByYear(year):
        idx = int(info.jqIndex)
        name = _JIEQI_NAMES_BY_INDEX.get(idx)
        if not name:
            # 理论上不会发生；保底避免 KeyError
            name = f"JQ{idx}"
        dt = _jd_to_beijing_datetime(float(info.jd))
        terms.append((name, dt))
    return terms


def get_solar_term(target_dt: datetime.datetime) -> str:
    """
    精确计算给定时间的节气
    
    Args:
        target_dt: 需要查询的日期时间（北京时间）
        
    Returns:
        str: 节气名称
    """
    year = target_dt.year
    
    # 获取相关年份的交节序列（包含跨年边界）
    terms_list: List[Tuple[str, datetime.datetime]] = []
    for y in (year - 1, year, year + 1):
        cache_key = str(y)
        if cache_key not in _solar_terms_cache:
            _solar_terms_cache[cache_key] = _get_year_solar_terms(y)
        terms_list.extend(_solar_terms_cache[cache_key])

    # 去重（跨年份列表会包含同一交节点）
    seen = set()
    uniq_terms: List[Tuple[str, datetime.datetime]] = []
    for name, dt in terms_list:
        key = (name, dt)
        if key in seen:
            continue
        seen.add(key)
        uniq_terms.append((name, dt))

    uniq_terms.sort(key=lambda x: x[1])
    if not uniq_terms:
        # 理论上不会发生；保底返回与旧逻辑一致的默认值
        return "春分"

    # 节气判定基于时间区间：上一个交节时刻 ≤ 当前时间 < 下一个交节时刻
    # 用 bisect_right 确保“交节瞬间”归属新节气。
    boundaries = [dt for _, dt in uniq_terms]
    pos = bisect_right(boundaries, target_dt) - 1
    if pos < 0:
        # 目标时间早于已加载边界（极少见）；回退到最早边界对应节气
        pos = 0

    return uniq_terms[pos][0]


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
