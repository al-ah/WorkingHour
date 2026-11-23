"""اطلاعات ناحیهٔ کاری صفحه و محل تسک‌بار ویندوز (برای جای‌گیری ویجت)."""

import ctypes
from ctypes import wintypes

SPI_GETWORKAREA = 0x0030
ABM_GETTASKBARPOS = 0x00000005


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", RECT),
        ("lParam", wintypes.LPARAM),
    ]


def work_area():
    """(left, top, right, bottom) ناحیهٔ کاری صفحه، بدون تسک‌بار."""
    rect = RECT()
    try:
        ok = ctypes.windll.user32.SystemParametersInfoW(
            SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    except Exception:  # noqa: BLE001
        ok = 0
    if ok:
        return rect.left, rect.top, rect.right, rect.bottom
    return None


def taskbar_rect():
    """مختصات تسک‌بار؛ None اگر در دسترس نباشد."""
    data = APPBARDATA()
    data.cbSize = ctypes.sizeof(APPBARDATA)
    try:
        ok = ctypes.windll.shell32.SHAppBarMessage(ABM_GETTASKBARPOS,
                                                   ctypes.byref(data))
    except Exception:  # noqa: BLE001
        ok = 0
    if ok:
        return data.rc.left, data.rc.top, data.rc.right, data.rc.bottom
    return None
