import datetime
import pyplanets
import ichingpy
import math  # 导入math库用于弧度到度数的转换
from typing import Dict

from pyplanets.core.epoch import Epoch
from pyplanets.planets.earth import Earth

# 定义二十四节气及其对应的黄经角度
SOLAR_TERMS = [
    (0, "春分"), (15, "清明"), (30, "谷雨"),
    (45, "立夏"), (60, "小满"), (75, "芒种"),
    (90, "夏至"), (105, "小暑"), (120, "大暑"),
    (135, "立秋"), (150, "处暑"), (165, "白露"),
    (180, "秋分"), (195, "寒露"), (210, "霜降"),
    (225, "立冬"), (240, "小雪"), (255, "大雪"),
    (270, "冬至"), (285, "小寒"), (300, "大寒"),
    (315, "立春"), (330, "雨水"), (345, "惊蛰")
]


def get_solar_term(target_dt: datetime.datetime) -> str:
    """
    【源码验证版】
    根据给定的时间，通过计算地球的日心经度来推导太阳的地心经度，
    从而精确计算出当前的节气。

    Args:
        target_dt (datetime.datetime): 需要查询的日期和时间对象。

    Returns:
        str: 节气的中文名称。
    """
    # 1. 将 Python datetime 转换为 PyPlanets 的 Epoch 对象。
    epoch = Epoch(target_dt.year, target_dt.month, target_dt.day,
                            target_dt.hour, target_dt.minute, target_dt.second)

    # 2. 创建该时刻的地球对象。
    earth = Earth(epoch)

    # 3. 获取地球的日心坐标，返回的是 (Angle, Angle, float) 对象。
    l_angle, b_angle, r = earth.geometric_heliocentric_position()

    # 4. 【核心修正】根据源码，调用 .rad() 获取弧度值，再用 math.degrees() 转换为度数。
    earth_heliocentric_lon_rad = l_angle.rad()
    earth_heliocentric_lon_deg = math.degrees(earth_heliocentric_lon_rad)

    # 5. 太阳的地心经度 = 地球的日心经度 + 180°。
    sun_geocentric_lon_deg = (earth_heliocentric_lon_deg + 180.0) % 360.0

    # 6. 查找节气
    current_term_name = None
    for angle, name in reversed(SOLAR_TERMS):
        if sun_geocentric_lon_deg >= angle:
            current_term_name = name
            break

    if current_term_name is None:
        current_term_name = "春分"

    return current_term_name


def get_si_zhu(target_dt: datetime.datetime) -> Dict[str, str]:
    """
    使用 ichingpy 获取四柱。
    """
    fp = ichingpy.FourPillars.from_datetime(target_dt)
    pillars_str = fp.get_pillars()
    pillars_list = pillars_str.split(' ')
    return {
        "年": pillars_list[0],
        "月": pillars_list[1],
        "日": pillars_list[2],
        "时": pillars_list[3]
    }