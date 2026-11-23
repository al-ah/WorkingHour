"""تبدیل تاریخ شمسی (جلالی) و میلادی، بدون هیچ وابستگی خارجی."""

import datetime as _dt

MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]

# datetime.weekday(): Monday == 0
WEEKDAYS = ["دوشنبه", "سه شنبه", "چهارشنبه", "پنج شنبه", "جمعه", "شنبه", "یکشنبه"]


def _g2j(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1
    g_day_no = 365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400
    g_day_no += g_d_m[gm2]
    if gm > 2 and ((gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0):
        g_day_no += 1
    g_day_no += gd2
    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365
    if j_day_no < 186:
        jm = 1 + j_day_no // 31
        jd = 1 + j_day_no % 31
    else:
        jm = 7 + (j_day_no - 186) // 30
        jd = 1 + (j_day_no - 186) % 30
    return jy, jm, jd


def _j2g(jy, jm, jd):
    jy += 1595
    days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
    if jm < 7:
        days += (jm - 1) * 31
    else:
        days += ((jm - 7) * 30) + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0
    sal_a = [0, 31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    while gm < 13 and gd > sal_a[gm]:
        gd -= sal_a[gm]
        gm += 1
    return gy, gm, gd


def from_date(d):
    """Gregorian date -> (jy, jm, jd)."""
    return _g2j(d.year, d.month, d.day)


def to_date(jy, jm, jd):
    """(jy, jm, jd) -> Gregorian datetime.date."""
    return _dt.date(*_j2g(jy, jm, jd))


def month_length(jy, jm):
    if jm <= 6:
        return 31
    if jm <= 11:
        return 30
    gap = (to_date(jy + 1, 1, 1) - to_date(jy, 12, 1)).days
    return gap  # 29 or 30


def prev_month(jy, jm):
    return (jy - 1, 12) if jm == 1 else (jy, jm - 1)


def next_month(jy, jm):
    return (jy + 1, 1) if jm == 12 else (jy, jm + 1)


def month_name(jm):
    return MONTHS[jm - 1]


def weekday_name(d):
    return WEEKDAYS[d.weekday()]


def format_date(jy, jm, jd):
    """مثال: ۱۲ آبان ۱۴۰۵ به شکل '12 آبان 1405'."""
    return f"{jd} {month_name(jm)} {jy}"


def format_date_of(d):
    jy, jm, jd = from_date(d)
    return format_date(jy, jm, jd)
