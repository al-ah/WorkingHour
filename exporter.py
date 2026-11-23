"""ساخت فایل اکسل خروجی، دقیقاً در قالب فایل‌های نمونهٔ پوشهٔ data."""

import datetime as dt
import os
import re

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

import i18n
import jalali

HEADERS = ["روز", "تاریخ", "ماه", "ساعت شروع", "ساعت پایان", "مدت", "جمع ساعت", "توضیحات"]
COLUMN_WIDTHS = {
    "A": 9.11, "B": 9.11, "C": 9.11, "D": 10.66, "E": 10.33,
    "F": 9.11, "G": 13.11, "H": 47.55,
}

_HEADER_FONT = Font(name="Calibri", size=11, bold=True)
_HEADER_FILL = PatternFill("solid", fgColor="EDF1F7")
_TOTAL_FONT = Font(name="Calibri", size=11, bold=True)
_THIN = Side(style="thin", color="D6DCE5")


def period_of(date, start_day):
    """دوره‌ای که این تاریخ در آن قرار می‌گیرد: ((سال, ماه), تاریخ شروع, تاریخ پایان).

    start_day == 1  -> دوره برابر ماه شمسی است.
    start_day == 28 -> دوره از ۲۸ ماه قبل تا ۲۷ ماه جاری (مثل فایل نمونهٔ پروژه A).
    """
    start_day = max(1, min(31, int(start_day or 1)))
    jy, jm, jd = jalali.from_date(date)
    if start_day == 1:
        return (
            (jy, jm),
            jalali.to_date(jy, jm, 1),
            jalali.to_date(jy, jm, jalali.month_length(jy, jm)),
        )
    end_day = start_day - 1
    if jd <= end_day:
        py, pm = jalali.prev_month(jy, jm)
        start = jalali.to_date(py, pm, min(start_day, jalali.month_length(py, pm)))
        end = jalali.to_date(jy, jm, min(end_day, jalali.month_length(jy, jm)))
        return (jy, jm), start, end
    ny, nm = jalali.next_month(jy, jm)
    start = jalali.to_date(jy, jm, min(start_day, jalali.month_length(jy, jm)))
    end = jalali.to_date(ny, nm, min(end_day, jalali.month_length(ny, nm)))
    return (ny, nm), start, end


def period_label(start_day):
    return i18n.period_label(start_day)


def _safe_filename(name):
    cleaned = re.sub(r'[\\/:*?"<>|]', "-", name).strip()
    return cleaned or "خروجی"


def _unique_title(wb, title):
    title = title[:31]
    if title not in wb.sheetnames:
        return title
    index = 2
    while True:
        suffix = f" ({index})"
        candidate = title[: 31 - len(suffix)] + suffix
        if candidate not in wb.sheetnames:
            return candidate
        index += 1


def _fill_sheet(ws, entries):
    ws.sheet_view.rightToLeft = True
    for column, width in COLUMN_WIDTHS.items():
        ws.column_dimensions[column].width = width

    for index, header in enumerate(HEADERS, start=1):
        cell = ws.cell(row=1, column=index, value=header)
        cell.font = _HEADER_FONT
        cell.fill = _HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(bottom=_THIN)
    ws.row_dimensions[1].height = 22

    row_index = 2
    for entry in entries:
        start = entry["start"]
        end = entry["end"]
        jy, jm, jd = jalali.from_date(start.date())
        start_time = start.time().replace(second=0, microsecond=0)
        end_time = end.time().replace(second=0, microsecond=0)
        minutes = max(0, int(round(entry["seconds"] / 60.0)))

        ws.cell(row=row_index, column=1, value=i18n.weekday_name(start))
        ws.cell(row=row_index, column=2, value=jd)
        ws.cell(row=row_index, column=3, value=i18n.month_name(jm)).number_format = "@"
        ws.cell(row=row_index, column=4, value=start_time).number_format = "h:mm"
        ws.cell(row=row_index, column=5, value=end_time).number_format = "h:mm"
        ws.cell(row=row_index, column=6, value=minutes / 1440.0).number_format = "h:mm"
        ws.cell(row=row_index, column=7, value=f"=SUM(F$2:F{row_index})").number_format = "[h]:mm"
        description = ws.cell(row=row_index, column=8, value=entry["description"])
        description.alignment = Alignment(horizontal="right", vertical="center", wrap_text=False)
        for column in range(1, 8):
            ws.cell(row=row_index, column=column).alignment = Alignment(
                horizontal="center", vertical="center"
            )
        row_index += 1

    last_data_row = row_index - 1
    if last_data_row >= 2:
        total_row = last_data_row + 1
        total_cell = ws.cell(row=total_row, column=7, value=f"=SUM(F$2:F{last_data_row})")
        total_cell.number_format = "[h]:mm"
        total_cell.font = _TOTAL_FONT
        total_cell.alignment = Alignment(horizontal="center", vertical="center")
        label = ws.cell(row=total_row, column=8, value="جمع کل")
        label.font = _TOTAL_FONT
        label.alignment = Alignment(horizontal="right", vertical="center")
        for column in range(1, 9):
            ws.cell(row=total_row, column=column).border = Border(top=_THIN)

    ws.freeze_panes = "A2"


def build_workbook(entries, start_day):
    """entries: سوابق یک شرکت -> Workbook با یک شیت برای هر دوره (جدیدترین اول)."""
    buckets = {}
    for entry in entries:
        key, _start, _end = period_of(entry["start"].date(), start_day)
        buckets.setdefault(key, []).append(entry)

    workbook = Workbook()
    workbook.remove(workbook.active)

    for jy, jm in sorted(buckets, key=lambda k: (k[0], k[1]), reverse=True):
        title = _unique_title(workbook, f"{i18n.month_name(jm)} {jy}")
        ws = workbook.create_sheet(title)
        rows = sorted(buckets[(jy, jm)], key=lambda e: (e["start"], e["id"]))
        _fill_sheet(ws, rows)

    if not workbook.sheetnames:
        workbook.create_sheet("خالی")
    return workbook


def export_group(name, entries, start_day, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    workbook = build_workbook(entries, start_day)
    path = os.path.join(out_dir, f"{i18n.t('export_prefix')}- {_safe_filename(name)}.xlsx")
    workbook.save(path)
    return path


def export_groups(groups, out_dir):
    paths = []
    for group in groups:
        if not group["entries"]:
            continue
        paths.append(
            export_group(
                group["name"],
                group["entries"],
                group.get("cycle_start_day", 1),
                out_dir,
            )
        )
    return paths


def total_minutes(entries):
    return sum(max(0, e["seconds"]) for e in entries) / 60.0
