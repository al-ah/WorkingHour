"""اجرای خودکار همراه با شروع ویندوز، با یک Shortcut در پوشهٔ Startup."""

import os
import subprocess
import sys
import tempfile

STARTUP_DIR = os.path.join(
    os.environ.get("APPDATA", ""),
    "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
)
LINK_NAME = "WorkingHour.lnk"
LINK_PATH = os.path.join(STARTUP_DIR, LINK_NAME)
CREATE_NO_WINDOW = 0x08000000


def launch_target(exe_path=None):
    """(فایل اجرایی, آرگومان‌ها, پوشهٔ کاری) برای Shortcut."""
    if exe_path:
        exe_path = os.path.abspath(exe_path)
        return exe_path, "", os.path.dirname(exe_path)
    if getattr(sys, "frozen", False):
        exe = os.path.abspath(sys.executable)
        return exe, "", os.path.dirname(exe)
    pythonw = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    return pythonw, f'"{script}"', os.path.dirname(script)


def is_enabled():
    return os.path.exists(LINK_PATH)


def _ps_quote(value):
    return '"' + str(value).replace('"', '""') + '"'


def _write_shortcut(target, arguments, workdir):
    script = (
        "$shell = New-Object -ComObject WScript.Shell\n"
        f'$link = $shell.CreateShortcut({_ps_quote(LINK_PATH)})\n'
        f'$link.TargetPath = {_ps_quote(target)}\n'
        f'$link.Arguments = {_ps_quote(arguments)}\n'
        f'$link.WorkingDirectory = {_ps_quote(workdir)}\n'
        f'$link.IconLocation = "{target},0"\n'
        '$link.Description = "Working Hours widget"\n'
        "$link.Save()\n"
    )
    handle = tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False,
                                         encoding="utf-8-sig")
    path = handle.name
    try:
        handle.write(script)
        handle.close()
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", path],
            check=False, creationflags=CREATE_NO_WINDOW,
        )
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def enable(exe_path=None):
    """ساخت Shortcut در Startup. exe_path برای وقتی است که exe جای دیگری باشد."""
    os.makedirs(STARTUP_DIR, exist_ok=True)
    target, arguments, workdir = launch_target(exe_path)
    _write_shortcut(target, arguments, workdir)
    return is_enabled()


def disable():
    try:
        os.remove(LINK_PATH)
    except OSError:
        pass
    return is_enabled()


def toggle():
    """وضعیت جدید را برمی‌گرداند: True یعنی اجرای خودکار فعال شد."""
    if is_enabled():
        disable()
        return False
    enable()
    return True
