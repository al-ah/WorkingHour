"""نقطهٔ شروع برنامهٔ ویجت ساعت کاری."""

import ctypes
import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:  # noqa: BLE001
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:  # noqa: BLE001
        pass

from widget import WorkHourWidget  # noqa: E402

_INSTANCE_MUTEX = None
ERROR_ALREADY_EXISTS = 183


def claim_single_instance():
    """یک نسخه از برنامه اجازهٔ اجرا دارد؛ اجرای دوباره بی‌صدا خارج می‌شود."""
    global _INSTANCE_MUTEX
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        mutex = kernel32.CreateMutexW(None, False, "Local\\WorkingHourWidget")
        if not mutex:
            return True
        if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
            return False
        _INSTANCE_MUTEX = mutex
        return True
    except Exception:  # noqa: BLE001
        return True


def main():
    if not claim_single_instance():
        return
    root = tk.Tk()
    widget = WorkHourWidget(root)
    try:
        root.mainloop()
    finally:
        widget.stop_tray()


if __name__ == "__main__":
    main()
