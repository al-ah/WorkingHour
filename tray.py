"""آیکن ناحیهٔ اعلان ویندوز (کنار ساعت)."""

import i18n

try:
    import pystray
    from PIL import Image, ImageDraw
except Exception:  # noqa: BLE001
    pystray = None


def icon_image(color="#4f7cff", size=64):
    """تصویر آیکن: صفحهٔ ساعت با عقربه‌ها."""
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    edge = size - 3
    draw.ellipse((2, 2, edge, edge), fill=color)
    middle = size / 2
    draw.line((middle, middle, middle, middle - size * 0.28),
              fill="#ffffff", width=max(2, int(size * 0.08)))
    draw.line((middle, middle, middle + size * 0.22, middle + size * 0.1),
              fill="#ffffff", width=max(2, int(size * 0.08)))
    dot = size * 0.06
    draw.ellipse((middle - dot, middle - dot, middle + dot, middle + dot),
                 fill="#ffffff")
    return image


class Tray:
    """آیکن سینی سیستم؛ فرمان‌ها را به UI تحویل می‌دهد.

    ``send`` باید نخ‌ـامن باشد (مثل ``queue.Queue.put``) چون از نخ آیکن
    صدا زده می‌شود. فرمان‌ها: ``toggle`` و ``exit``.
    """

    def __init__(self, send, accent=None, visible=True):
        self._send = send
        self._accent = accent or "#4f7cff"
        self._visible = visible
        self._icon = None

    # -------------------------------------------------------------- lifecycle

    def start(self):
        if pystray is None:
            return False
        menu = pystray.Menu(
            pystray.MenuItem(self._toggle_label, self._on_toggle, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda item: i18n.t("tray_exit"), self._on_exit),
        )
        self._icon = pystray.Icon(
            "WorkingHour", icon_image(self._accent),
            i18n.t("app_title"), menu,
        )
        self._icon.run_detached()
        return True

    def stop(self):
        icon, self._icon = self._icon, None
        if icon is not None:
            try:
                icon.stop()
            except Exception:  # noqa: BLE001
                pass

    def set_visible(self, visible):
        self._visible = bool(visible)

    def refresh(self):
        """پس از تغییر زبان، متن راهنما و منو را به‌روز می‌کند."""
        if self._icon is None:
            return
        try:
            self._icon.title = i18n.t("app_title")
            self._icon.update_menu()
        except Exception:  # noqa: BLE001
            pass

    # --------------------------------------------------------------- internal

    def _toggle_label(self, item=None):
        return i18n.t("tray_hide" if self._visible else "tray_show")

    def _on_toggle(self, icon=None, item=None):
        self._send("toggle")

    def _on_exit(self, icon=None, item=None):
        self._send("exit")
