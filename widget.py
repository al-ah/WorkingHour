"""پنجرهٔ ویجت ساعت کاری + پنجره‌های تاریخچه و تنظیمات (چندزبانه)."""

import datetime as dt
import os
import queue
import re
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

import autostart
import desktop
import exporter
import i18n
import store
import tray

FONT = "Segoe UI"

# پوسته‌ها: هر کلید مستقیماً یکی از رنگ‌های سراسری همین ماژول را بازنویسی می‌کند.
THEMES = {
    "dark": {
        "BG": "#14171e", "CARD": "#1d222c", "FIELD": "#262c38",
        "BORDER": "#333b49", "TEXT": "#e9edf5", "MUTED": "#8d96a8",
        "ACCENT": "#4f7cff", "GREEN": "#1f9d63", "AMBER": "#bd8628",
        "RED": "#cf4d4d",
    },
    "light": {
        "BG": "#f2f4f9", "CARD": "#ffffff", "FIELD": "#e7ecf5",
        "BORDER": "#d2dae7", "TEXT": "#1b2233", "MUTED": "#66728a",
        "ACCENT": "#3b66f0", "GREEN": "#178f5b", "AMBER": "#a9761b",
        "RED": "#c94444",
    },
    "ocean": {
        "BG": "#0b1a2b", "CARD": "#122840", "FIELD": "#18354f",
        "BORDER": "#24506f", "TEXT": "#e6f2fb", "MUTED": "#8fb0c9",
        "ACCENT": "#2f9dff", "GREEN": "#20b07a", "AMBER": "#dfa139",
        "RED": "#e1605a",
    },
    "forest": {
        "BG": "#101a13", "CARD": "#18251b", "FIELD": "#203327",
        "BORDER": "#2e4a36", "TEXT": "#e9f4ec", "MUTED": "#90a899",
        "ACCENT": "#4fae72", "GREEN": "#2f9e63", "AMBER": "#c79738",
        "RED": "#cf5c50",
    },
}
THEME_KEYS = tuple(THEMES)

BG = CARD = FIELD = BORDER = TEXT = MUTED = ACCENT = GREEN = AMBER = RED = None


def apply_theme(key):
    """رنگ‌های سراسری را از پوستهٔ داده‌شده پر می‌کند (ناشناخته ← تیره)."""
    if key not in THEMES:
        key = "dark"
    globals().update(THEMES[key])
    return key


apply_theme("dark")

DOCK_KEYS = ("above_clock", "top_right", "top_left", "bottom_left",
             "taskbar", "free")

_DESC_MODIFIER_KEYS = {
    "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",
    "Super_L", "Super_R", "Caps_Lock", "Num_Lock", "Escape", "Tab",
    "ISO_Left_Tab", "Print", "Pause",
}
_DESC_NAV_KEYS = {
    "Left", "Right", "Up", "Down", "Home", "End", "Prior", "Next",
}

# دنبالهٔ چپ‌به‌راست انتهای متن (عدد/لاتین) که در پاراگراف راست‌به‌چپ از سمت
# چپ چیده می‌شود؛ مکان‌نما باید بعد از آن قرار بگیرد.
_DESC_LTR_TAIL = re.compile(r"[A-Za-z0-9\u0660-\u0669\u06f0-\u06f9:.,/\\\\+\-\u2212 ]*$")


RLM = "\u200f"  # RIGHT-TO-LEFT MARK


def rtl_text(text):
    """متن نمایشی با جهت پایهٔ راست‌به‌چپ.

    Tk جهت پایه را از نخستین نویسهٔ قوی حدس می‌زند؛ رشته‌ای که با رقم شروع
    شود (تاریخ، جمع ساعت) چپ‌به‌راست چیده می‌شود و ارقام سر جای غلط می‌افتند.
    یک RLM در ابتدا جهت درست را تحمیل می‌کند.
    """
    text = "" if text is None else str(text)
    if not text or not i18n.is_rtl():
        return text
    return RLM + text


def t(key, **kwargs):
    return rtl_text(i18n.t(key, **kwargs))


def start_anchor():
    return "e" if i18n.is_rtl() else "w"


def start_side():
    return "right" if i18n.is_rtl() else "left"


def end_side():
    return "left" if i18n.is_rtl() else "right"


def end_anchor():
    return "w" if i18n.is_rtl() else "e"


def fmt_hms(seconds):
    seconds = max(0, int(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def fmt_hm(seconds):
    seconds = max(0, int(seconds))
    hours, rest = divmod(seconds, 3600)
    return f"{hours}:{rest // 60:02d}"


def flat_button(parent, text, command, bg=None, fg=None, font=None,
                padx=10, pady=7, **kwargs):
    # رنگ‌های پیش‌فرض هنگام فراخوانی خوانده می‌شوند تا تغییر پوسته اثر کند.
    bg = FIELD if bg is None else bg
    fg = TEXT if fg is None else fg
    return tk.Button(
        parent, text=text, command=command, bg=bg, fg=fg,
        activebackground=bg, activeforeground=fg,
        relief="flat", bd=0, highlightthickness=0, cursor="hand2",
        font=font or (FONT, 10), padx=padx, pady=pady, **kwargs,
    )


def field_label(parent, text):
    return tk.Label(parent, text=text, bg=BG, fg=MUTED, font=(FONT, 8),
                    anchor=start_anchor())


def dark_entry(parent, **kwargs):
    options = dict(
        bg=FIELD, fg=TEXT, insertbackground=TEXT, relief="flat",
        highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT,
        font=(FONT, 10), justify="right" if i18n.is_rtl() else "left",
    )
    options.update(kwargs)
    return tk.Entry(parent, **options)


def dark_combo(parent, **kwargs):
    options = dict(
        style="Dark.TCombobox", font=(FONT, 9), state="readonly",
        justify="right" if i18n.is_rtl() else "left",
    )
    options.update(kwargs)
    return ttk.Combobox(parent, **options)


def rtl_combo_layout(layout):
    """چیدمان کادر کشویی را برای راست‌به‌چپ مرتب می‌کند: فلش در سمت چپ.\n
    فهرست عناصر هر پوسته کمی متفاوت است، پس به‌جای ساختن چیدمان دستی، عنصر\n
    فلش از چیدمان خود پوسته برداشته و به ابتدای فرزندانش منتقل می‌شود.\n
    """
    items = []
    for name, options in layout:
        options = dict(options)
        children = options.get("children")
        if children:
            options["children"] = rtl_combo_layout(children)
        if name == "Combobox.downarrow":
            options["side"] = "left"
        items.append((name, options))
    arrows = [item for item in items if item[0] == "Combobox.downarrow"]
    others = [item for item in items if item[0] != "Combobox.downarrow"]
    return arrows + others


def fit_geometry(widget, width, height, near_x=None, near_y=None):
    """اندازه/جای پنجره را داخل ناحیهٔ کاری ویندوز نگه می‌دارد (نه بیرون از آن)."""
    screen_w, screen_h = widget.winfo_screenwidth(), widget.winfo_screenheight()
    left, top, right, bottom = desktop.work_area() or (0, 0, screen_w, screen_h)
    if right - left < 240 or bottom - top < 240:
        left, top, right, bottom = 0, 0, screen_w, screen_h
    width = min(int(width), max(320, right - left - 24))
    height = min(int(height), max(240, bottom - top - 24))
    if near_x is None:
        near_x = (left + right) // 2
    if near_y is None:
        near_y = (top + bottom) // 2
    x = min(max(left + 12, near_x - width // 2), right - width - 12)
    y = min(max(top + 12, near_y - height // 2), bottom - height - 12)
    return f"{width}x{height}+{int(x)}+{int(y)}"


def short_desc(text, limit=38):
    """برچسب کوتاه یک‌خطی برای فهرست شرح‌های قبلی."""
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit - 1] + "…"


class RtlTextField(tk.Text):
    """کادر متن با نمایش و مکان‌نمای درست در فارسی و عربی.

    Tk در متن دوجهته هم مکان‌نما را در ابتدای خط می‌کشد و هم نگاشت کلیک به
    اندیس را منطقی برمی‌گرداند؛ بنابراین نویسه‌ها همیشه در انتهای متن درج
    می‌شوند و یک نشانگر باریک روی همان نقطه کشیده می‌شود.
    """

    BLINK_MS = 530

    def __init__(self, master, bg=None, fg=None, **kwargs):
        bg = FIELD if bg is None else bg
        fg = TEXT if fg is None else fg
        options = dict(
            bg=bg, fg=fg, font=(FONT, 10), wrap="word", padx=8, pady=6,
            spacing1=2, spacing3=2, relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, insertwidth=0, insertbackground=bg,
        )
        options.update(kwargs)
        super().__init__(master, **options)
        self._caret = tk.Frame(self, bg=fg, bd=0, highlightthickness=0)
        self._caret_on = True
        self._caret_after = None
        self.tag_configure("dir", justify="right" if i18n.is_rtl() else "left")
        self.bind("<KeyPress>", self._on_key)
        self.bind("<<Paste>>", self._on_paste)
        self.bind("<KeyRelease>", lambda event: self.apply_direction())
        self.bind("<FocusIn>", lambda event: self.kick_caret())
        self.bind("<FocusOut>", self.stop_caret)
        self.bind("<Configure>", lambda event: self.paint_caret())
        self.bind("<ButtonRelease-1>", lambda event: self.kick_caret())
        self.bind("<Destroy>", self.stop_caret)

    # ---------------------------------------------------------------- content

    def text(self):
        return self.get("1.0", "end-1c")

    def set_text(self, text):
        state = str(self.cget("state"))
        if state == "disabled":
            self.configure(state="normal")
        self.delete("1.0", "end")
        if text:
            self.insert("1.0", text)
        if state == "disabled":
            self.configure(state="disabled")
        self.apply_direction()

    def apply_direction(self):
        self.tag_add("dir", "1.0", "end")
        self.kick_caret()

    # ----------------------------------------------------------------- typing

    def insert_text(self, text):
        if not text:
            return
        if self.tag_ranges("sel"):
            self.delete("sel.first", "sel.last")
        self.insert("end-1c", text)
        self.mark_set("insert", "end-1c")
        self.see("end-1c")
        self.apply_direction()

    def delete_back(self):
        if self.tag_ranges("sel"):
            self.delete("sel.first", "sel.last")
        elif self.compare("end-1c", ">", "1.0"):
            self.delete("end-2c", "end-1c")
        self.mark_set("insert", "end-1c")
        self.apply_direction()

    def _on_key(self, event):
        if event.state & 0x0004:  # Ctrl/Alt: میان‌برهای پیش‌فرض
            return None
        keysym = event.keysym
        if keysym in _DESC_MODIFIER_KEYS:
            return None
        if keysym == "Return":
            self.insert_text("\n")
            return "break"
        if keysym == "BackSpace":
            self.delete_back()
            return "break"
        if keysym == "Delete":
            if self.tag_ranges("sel"):
                self.delete("sel.first", "sel.last")
            self.mark_set("insert", "end-1c")
            self.apply_direction()
            return "break"
        if keysym in _DESC_NAV_KEYS:
            self.mark_set("insert", "end-1c")
            return "break"
        if event.char and event.char.isprintable():
            self.insert_text(event.char)
            return "break"
        return None

    def _on_paste(self, event=None):
        try:
            text = self.clipboard_get()
        except tk.TclError:
            return "break"
        self.insert_text(text.replace("\r\n", "\n").replace("\r", "\n"))
        return "break"

    # ------------------------------------------------------------------ caret

    def focused(self):
        try:
            return self.focus_get() is self
        except (KeyError, tk.TclError):
            return False

    def _caret_box(self):
        """x/y/ارتفاع نشانگر روی نقطهٔ درج (انتهای متن).

        bbox/insert در متن دوجهته مختصات منطقی می‌دهند؛ dlineinfo تنها
        اندازه‌ای است که با جای واقعی خط می‌خواند.
        """
        font = tkfont.Font(font=self.cget("font"))
        line_height = font.metrics("linespace")
        try:
            geometry = self.dlineinfo("end-1c")
        except tk.TclError:
            geometry = None
        if geometry:
            x, y, width, height = geometry[:4]
            if i18n.is_rtl():
                tail = _DESC_LTR_TAIL.search(self.text())
                return x + (font.measure(tail.group(0)) if tail else 0), y, height
            return x + width, y, height
        if i18n.is_rtl():
            return max(0, self.winfo_width() - 12), 7, line_height
        return 9, 7, line_height

    def _caret_inset(self):
        """place() درون Text نسبت به مختصات dlineinfo به اندازهٔ حاشیه جابه‌جا است."""
        border = int(self.cget("highlightthickness")) + int(self.cget("bd") or 0)
        return (int(self.cget("padx")) + border,
                int(self.cget("pady")) + border)

    def paint_caret(self):
        caret = self._caret
        try:
            if not caret.winfo_exists():
                return
        except tk.TclError:
            return
        if (not self._caret_on or not self.focused()
                or str(self.cget("state")) == "disabled"):
            caret.place_forget()
            return
        x, y, height = self._caret_box()
        inset_x, inset_y = self._caret_inset()
        caret.place(x=max(0, x - inset_x), y=max(0, y - inset_y),
                    width=2, height=height)

    def kick_caret(self):
        """پس از هر تغییر متن: نشانگر روشن و سر جای درج."""
        self._caret_on = True
        self.paint_caret()
        if self._caret_after is None and self.focused():
            self._caret_after = self.after(self.BLINK_MS, self._blink_caret)

    def _blink_caret(self):
        self._caret_after = None
        self._caret_on = not self._caret_on
        self.paint_caret()
        if self.focused():
            self._caret_after = self.after(self.BLINK_MS, self._blink_caret)

    def stop_caret(self, event=None):
        if self._caret_after is not None:
            try:
                self.after_cancel(self._caret_after)
            except tk.TclError:
                pass
            self._caret_after = None
        self.paint_caret()


class WorkHourWidget:
    WIDTH = 352
    MINI_WIDTH = 320

    def __init__(self, root):
        self.root = root
        i18n.set_language(store.meta_get("language", "fa"))
        theme = store.meta_get("theme", "dark")
        self.theme = theme if theme in THEMES else "dark"
        apply_theme(self.theme)
        self.theme_var = tk.StringVar(value=self.theme)
        self._theme_menu = None
        self.companies = store.list_companies()
        self.session = store.active_get()
        dock = store.meta_get("dock", "above_clock")
        self.dock = dock if dock in DOCK_KEYS else "above_clock"
        # dock=taskbar only fits the compact strip, so start in that shape
        self.compact = self.dock == "taskbar"
        self.dock_var = tk.StringVar(value=self.dock)
        self._drag_offset = None
        self._drag_from = None
        self._menu = None
        self._history_window = None
        self._settings_window = None
        self.visible = True
        self._hidden_windows = []
        self._tray = None
        self._tray_commands = queue.Queue()
        self._recent_map = {}
        self._prefilled = ""
        self.x = 0
        self.y = 0

        self._configure_styles()
        self._setup_window()
        self._build()
        self._refresh()
        self._prefill_description()
        self._tick()
        self._start_tray()
        self._poll_tray()

    # ------------------------------------------------------------- setup

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Dark.TCombobox",
            fieldbackground=FIELD, background=FIELD, foreground=TEXT,
            arrowcolor=MUTED, bordercolor=BORDER, lightcolor=FIELD,
            darkcolor=FIELD, selectbackground=FIELD, selectforeground=TEXT,
            padding=6, relief="flat",
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", FIELD), ("disabled", FIELD)],
            foreground=[("readonly", TEXT)],
            arrowcolor=[("readonly", MUTED)],
        )
        # در چیدمان راست‌به‌چپ فلش کشویی سمت چپ کادر می‌نشیند.
        base_layout = style.layout("TCombobox")
        style.layout("Dark.TCombobox",
                     rtl_combo_layout(base_layout) if i18n.is_rtl() else base_layout)
        style.configure(
            "Dark.Treeview",
            background=CARD, fieldbackground=CARD, foreground=TEXT,
            rowheight=26, borderwidth=0, font=(FONT, 9),
        )
        style.configure(
            "Dark.Treeview.Heading",
            background=FIELD, foreground=TEXT, font=(FONT, 9, "bold"),
            relief="flat", borderwidth=0, padding=5,
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", "#ffffff")],
        )
        self.root.option_add("*TCombobox*Listbox.background", CARD)
        self.root.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        self.root.option_add("*TCombobox*Listbox.font", (FONT, 10))
        self.root.option_add("*TCombobox*Listbox.justify",
                             "right" if i18n.is_rtl() else "left")

    def _setup_window(self):
        root = self.root
        root.title(t("app_title"))
        root.configure(bg=BG)
        try:
            root.overrideredirect(True)
        except tk.TclError:
            pass
        root.attributes("-topmost", store.meta_get("always_on_top", "1") == "1")

        self.x = max(0, root.winfo_screenwidth() // 2 - self.WIDTH // 2)
        self.y = max(0, root.winfo_screenheight() // 2 - 220)
        if self.dock == "free":
            position = store.meta_get("pos", "")
            if position and "," in position:
                try:
                    self.x, self.y = [int(part) for part in position.split(",")]
                except ValueError:
                    pass
        root.geometry(f"{self.WIDTH}x440+{self.x}+{self.y}")
        root.update_idletasks()
        root.lift()
        root.after(300, root.lift)

    def _build(self):
        self._build_header()
        self._build_body()
        self._build_mini()
        self.root.update_idletasks()
        self._apply_mode()

    def _build_header(self):
        self.header = tk.Frame(self.root, bg=CARD, height=34)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        title = tk.Label(self.header, text=t("app_title"), bg=CARD, fg=TEXT,
                         font=(FONT, 10, "bold"))
        title.pack(side=start_side(), padx=12)

        for text, command in (("✕", self.close), ("–", self.toggle_collapse)):
            flat_button(self.header, text, command, bg=CARD, fg=MUTED,
                        font=(FONT, 11), padx=8, pady=1, width=2).pack(
                side=end_side(), padx=1)
        self.menu_button = flat_button(self.header, "⋯", self.open_placement_menu,
                                       bg=CARD, fg=MUTED, font=(FONT, 11),
                                       padx=8, pady=1, width=2)
        self.menu_button.pack(side=end_side(), padx=1)
        self.pin_button = flat_button(self.header, "◉", self.toggle_pin, bg=CARD,
                                      fg=MUTED, font=(FONT, 10), padx=8, pady=1, width=2)
        self.pin_button.pack(side=end_side(), padx=1)
        self._paint_pin()

        for widget in (self.header, title):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._on_drag)
            widget.bind("<ButtonRelease-1>", self._end_drag)
        self.header.bind("<Double-Button-1>", lambda e: self.toggle_collapse())

    def _build_body(self):
        self.body = tk.Frame(self.root, bg=BG)
        self.body.pack(fill="both", expand=True)
        self.body.grid_columnconfigure(0, weight=1)

        field_label(self.body, t("company")).grid(
            row=0, column=0, sticky=start_anchor(), padx=16, pady=(12, 3))
        self.company_var = tk.StringVar()
        self.company_cb = dark_combo(
            self.body, textvariable=self.company_var, font=(FONT, 10), values=[],
        )
        self.company_cb.grid(row=1, column=0, sticky="ew", padx=16)
        self.company_cb.bind("<<ComboboxSelected>>", self._on_company_selected)

        desc_head = tk.Frame(self.body, bg=BG)
        desc_head.grid(row=2, column=0, sticky="ew", padx=16, pady=(10, 3))
        field_label(desc_head, t("description")).pack(side=start_side())
        self.recent_var = tk.StringVar()
        self.recent_cb = dark_combo(
            desc_head, textvariable=self.recent_var, font=(FONT, 8), width=16,
            values=[],
        )
        self.recent_cb.pack(side=end_side())
        self.recent_cb.bind("<<ComboboxSelected>>", self._on_recent_selected)

        self.desc = RtlTextField(self.body, height=2, bg=FIELD, fg=TEXT)
        self.desc.grid(row=3, column=0, sticky="ew", padx=16)
        self.desc.bind("<Control-Return>", self._start_from_keyboard)

        card = tk.Frame(self.body, bg=CARD, highlightbackground=BORDER,
                        highlightthickness=1)
        card.grid(row=4, column=0, sticky="ew", padx=16, pady=(12, 0))
        card.grid_columnconfigure(0, weight=1)

        self.status_lbl = tk.Label(card, text=t("ready"), bg=CARD, fg=MUTED,
                                   font=(FONT, 9))
        self.status_lbl.grid(row=0, column=0, pady=(10, 0))
        self.timer_lbl = tk.Label(card, text="00:00:00", bg=CARD, fg=TEXT,
                                  font=(FONT, 25, "bold"))
        self.timer_lbl.grid(row=1, column=0, pady=(0, 0))
        self.meta_lbl = tk.Label(card, text="", bg=CARD, fg=MUTED, font=(FONT, 8))
        self.meta_lbl.grid(row=2, column=0, pady=(2, 10))

        self.actions = tk.Frame(self.body, bg=BG)
        self.actions.grid(row=5, column=0, sticky="ew", padx=16, pady=(10, 0))
        self.actions.grid_columnconfigure(0, weight=1)
        self.actions.grid_columnconfigure(1, weight=1)

        footer = tk.Frame(self.body, bg=BG)
        footer.grid(row=6, column=0, sticky="ew", padx=16, pady=(10, 14))
        for index in range(3):
            footer.grid_columnconfigure(index, weight=1)
        items = [
            (t("history"), self.open_history),
            (t("export"), self.export_excel),
            (t("companies"), self.open_settings),
        ]
        if not i18n.is_rtl():
            items = items[::-1]
        for index, (label, command) in enumerate(items):
            padding = (0, 3) if index == 0 else ((3, 0) if index == 2 else 3)
            flat_button(footer, label, command, bg=FIELD, fg=MUTED,
                        font=(FONT, 8), padx=6, pady=6).grid(
                row=0, column=index, sticky="ew", padx=padding)

    def _build_mini(self):
        self.mini = tk.Frame(self.root, bg=CARD, highlightbackground=BORDER,
                            highlightthickness=1)
        self.mini.grid_columnconfigure(1, weight=1)

        self.mini_expand = flat_button(self.mini, "▣", self.toggle_collapse, bg=CARD,
                                       fg=MUTED, font=(FONT, 10), padx=6, pady=2,
                                       width=2)
        self.mini_expand.grid(row=0, column=0, padx=(5, 0), pady=5)
        self.mini_timer = tk.Label(self.mini, text="00:00:00", bg=CARD, fg=TEXT,
                                   font=(FONT, 14, "bold"), anchor="center")
        self.mini_timer.grid(row=0, column=1, sticky="ew")
        self.mini_actions = tk.Frame(self.mini, bg=CARD)
        self.mini_actions.grid(row=0, column=2, padx=(0, 6), pady=5)

        for widget in (self.mini, self.mini_timer):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._on_drag)
            widget.bind("<ButtonRelease-1>", self._end_drag)
        self.mini.bind("<Double-Button-1>", lambda e: self.toggle_collapse())

    def _render_mini(self):
        if not hasattr(self, "mini_actions"):
            return
        for widget in self.mini_actions.winfo_children():
            widget.destroy()
        if not self.session:
            flat_button(self.mini_actions, t("mini_start"), self.start_work,
                        bg=ACCENT, fg="#ffffff", font=(FONT, 8, "bold"),
                        padx=9, pady=4).grid(row=0, column=0)
            return
        paused = self.session["paused"]
        flat_button(self.mini_actions, t("mini_resume") if paused else t("mini_pause"),
                    self.resume_work if paused else self.pause_work,
                    bg=GREEN if paused else AMBER, fg="#ffffff",
                    font=(FONT, 8, "bold"), padx=9, pady=4).grid(row=0, column=0)
        flat_button(self.mini_actions, t("mini_stop"), self.stop_work, bg=RED,
                    fg="#ffffff", font=(FONT, 8, "bold"), padx=9, pady=4).grid(
            row=0, column=1, padx=(4, 0))

    def _apply_mode(self):
        self._render_mini()
        if self.compact:
            self.header.pack_forget()
            self.body.pack_forget()
            self.mini.pack(fill="both", expand=True)
        else:
            self.mini.pack_forget()
            self.header.pack(fill="x")
            self.body.pack(fill="both", expand=True)
        self._relayout()

    # ------------------------------------------------------------- window

    def _relayout(self):
        self.root.update_idletasks()
        if self.compact:
            width = self.MINI_WIDTH
            height = max(38, self.mini.winfo_reqheight() + 2)
        else:
            width = self.WIDTH
            height = self.header.winfo_reqheight() + self.body.winfo_reqheight() + 2
        self._place(width, height)

    def _place(self, width, height):
        if self.dock == "free":
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            x = min(max(0, self.x), max(0, screen_w - 80))
            y = min(max(0, self.y), max(0, screen_h - 60))
        else:
            x, y = self._dock_position(width, height)
        self.x, self.y = int(x), int(y)
        self.root.geometry(f"{width}x{height}+{self.x}+{self.y}")

    def _dock_position(self, width, height):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        left, top, right, bottom = desktop.work_area() or (0, 0, screen_w, screen_h)
        margin = 10

        if self.dock == "taskbar" and self.compact:
            taskbar = desktop.taskbar_rect()
            if taskbar:
                tb_left, tb_top, tb_right, tb_bottom = taskbar
                if tb_bottom - tb_top >= height:
                    tray = 260  # فضای ساعت و آیکون‌های کنار ساعت
                    x = min(tb_right - width - tray, tb_right - width - 8)
                    x = max(tb_left + 8, x)
                    y = tb_top + max(0, (tb_bottom - tb_top - height) // 2)
                    return x, y
            return right - width - margin, bottom - height - margin

        if self.dock == "above_clock":
            return right - width - margin, bottom - height - margin
        if self.dock == "top_right":
            return right - width - margin, top + margin
        if self.dock == "top_left":
            return left + margin, top + margin
        if self.dock == "bottom_left":
            return left + margin, bottom - height - margin
        return right - width - margin, bottom - height - margin

    def set_dock(self, key):
        if key not in DOCK_KEYS:
            return
        self.dock = key
        self.dock_var.set(key)
        store.meta_set("dock", key)
        if key == "taskbar":
            self.compact = True
            if not self.root.attributes("-topmost"):
                self.root.attributes("-topmost", True)
                store.meta_set("always_on_top", "1")
                self._paint_pin()
        self._apply_mode()

    def open_placement_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg=CARD, fg=TEXT,
                       activebackground=ACCENT, activeforeground="#ffffff",
                       font=(FONT, 9), bd=0)
        for key in DOCK_KEYS:
            menu.add_radiobutton(label=t("dock_" + key), variable=self.dock_var,
                                 value=key, command=lambda k=key: self.set_dock(k),
                                 selectcolor=ACCENT, activebackground=ACCENT,
                                 activeforeground="#ffffff")
        menu.add_separator()
        theme_menu = tk.Menu(menu, tearoff=0, bg=CARD, fg=TEXT,
                             activebackground=ACCENT, activeforeground="#ffffff",
                             font=(FONT, 9), bd=0)
        for key in THEME_KEYS:
            theme_menu.add_radiobutton(
                label=t("theme_" + key), variable=self.theme_var, value=key,
                command=lambda k=key: self._choose_theme_from_menu(k),
                selectcolor=ACCENT, activebackground=ACCENT,
                activeforeground="#ffffff")
        menu.add_cascade(label=t("theme"), menu=theme_menu)
        self._theme_menu = theme_menu
        self._menu = menu
        x = self.menu_button.winfo_rootx()
        y = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _choose_theme_from_menu(self, key):
        # منو باید پیش از بازسازی ویجت بسته شود تا Tcl خطا ندهد.
        if self._menu is not None:
            try:
                self._menu.unpost()
            except tk.TclError:
                pass
        self.root.after(120, lambda: self.set_theme(key))

    def _start_drag(self, event):
        self._drag_offset = (event.x_root - self.x, event.y_root - self.y)
        self._drag_from = (self.x, self.y)

    def _on_drag(self, event):
        if not self._drag_offset:
            return
        self.x = event.x_root - self._drag_offset[0]
        self.y = event.y_root - self._drag_offset[1]
        self.root.geometry(f"+{self.x}+{self.y}")

    def _end_drag(self, event):
        if self._drag_offset is None:
            return
        self._drag_offset = None
        moved = self._drag_from is None or (abs(self.x - self._drag_from[0]) > 3 or
                                           abs(self.y - self._drag_from[1]) > 3)
        if moved and self.dock != "free":
            self.dock = "free"
            self.dock_var.set("free")
            store.meta_set("dock", "free")
        store.meta_set("pos", f"{self.x},{self.y}")

    def _paint_pin(self):
        pinned = self.root.attributes("-topmost")
        self.pin_button.configure(fg=ACCENT if pinned else MUTED)

    def toggle_pin(self):
        pinned = not bool(self.root.attributes("-topmost"))
        self.root.attributes("-topmost", pinned)
        store.meta_set("always_on_top", "1" if pinned else "0")
        self._paint_pin()

    def toggle_collapse(self):
        # The dock setting is kept as chosen: expanding the form only floats it
        # above the taskbar for the moment (see _dock_position).
        self.compact = not self.compact
        self._apply_mode()

    def close(self):
        if not self.visible:
            self.show_widget()
        if self.session:
            if not messagebox.askyesno(t("exit_title"), t("exit_question"),
                                       parent=self.root):
                return
            store.active_pause()
        store.meta_set("pos", f"{self.x},{self.y}")
        self.stop_tray()
        self.root.destroy()

    def stop_tray(self):
        """آیکن را برمی‌دارد؛ بدون آن نخ آیکن پروسه را زنده نگه می‌دارد."""
        if self._tray is not None:
            self._tray.stop()
            self._tray = None

    # ---------------------------------------------------------------- tray

    def _start_tray(self):
        """آیکن کنار ساعت؛ اگر pystray مهیا نباشد برنامه بی‌آن هم کار می‌کند."""
        try:
            self._tray = tray.Tray(self._tray_commands.put, ACCENT,
                                   visible=self.visible)
            if not self._tray.start():
                self._tray = None
        except Exception:  # noqa: BLE001
            self._tray = None

    def _poll_tray(self):
        while True:
            try:
                command = self._tray_commands.get_nowait()
            except queue.Empty:
                break
            if command == "toggle":
                self.toggle_visible()
            elif command == "exit":
                self.close()
                return
        self.root.after(150, self._poll_tray)

    def toggle_visible(self):
        if self.visible:
            self.hide_widget()
        else:
            self.show_widget()

    def hide_widget(self):
        self.visible = False
        self._hidden_windows = [
            window for window in (self._history_window, self._settings_window)
            if window is not None and window.winfo_exists()
            and window.state() == "normal"
        ]
        for window in self._hidden_windows:
            window.withdraw()
        self.root.withdraw()
        if self._tray is not None:
            self._tray.set_visible(False)

    def show_widget(self):
        self.visible = True
        self.root.deiconify()
        self._relayout()
        self.root.lift()
        windows, self._hidden_windows = self._hidden_windows, []
        for window in windows:
            if window.winfo_exists():
                window.deiconify()
                window.lift()
        if self._tray is not None:
            self._tray.set_visible(True)

    # ------------------------------------------------------------- language

    def _rebuild_ui(self):
        for attr in ("_history_window", "_settings_window"):
            window = getattr(self, attr)
            if window is not None and window.winfo_exists():
                window.destroy()
            setattr(self, attr, None)

        self.root.title(t("app_title"))
        self.root.configure(bg=BG)
        for child in self.root.winfo_children():
            child.destroy()
        self._configure_styles()
        self._build()
        self._refresh()
        self._prefill_description()
        if self._tray is not None:
            self._tray.refresh()

    def set_language(self, code):
        i18n.set_language(code)
        store.meta_set("language", i18n.current())
        self._rebuild_ui()

    def set_theme(self, key):
        if key not in THEMES:
            return
        self.theme = apply_theme(key)
        self.theme_var.set(self.theme)
        store.meta_set("theme", self.theme)
        self._rebuild_ui()

    # ------------------------------------------------------------- session

    def selected_company(self):
        name = self.company_var.get().strip()
        return next((c for c in self.companies if c["name"] == name), None)

    # ------------------------------------------------------ recent descriptions

    def _recent_choices(self):
        """شرح‌های اخیر همان شرکت، تازه‌ترین اول."""
        company = self.selected_company()
        if not company:
            return []
        return store.recent_descriptions(company["id"], limit=8)

    def _refresh_recent(self):
        labels = []
        self._recent_map = {}
        for description in self._recent_choices():
            label = short_desc(description)
            if label not in self._recent_map:
                self._recent_map[label] = description
                labels.append(label)
        if not hasattr(self, "recent_cb"):
            return
        self.recent_cb.configure(values=labels,
                                 state="readonly" if labels else "disabled")
        self.recent_var.set(t("recent_descriptions") if labels else "")

    def _on_recent_selected(self, event=None):
        description = self._recent_map.get(self.recent_var.get())
        self.recent_var.set(t("recent_descriptions") if self._recent_map else "")
        if description is None or self.session:
            return
        self.desc.set_text(description)
        self._prefilled = description

    def _on_company_selected(self, event=None):
        self._prefill_description()
        self._refresh_recent()

    def _prefill_description(self):
        """شرح آخرین کار همان شرکت را پیشنهاد می‌دهد؛ نوشتهٔ کاربر را پاک نمی‌کند."""
        if self.session:
            return
        current = self.desc.text().strip()
        if current and current != self._prefilled:
            return
        choices = self._recent_choices()
        self._prefilled = choices[0] if choices else ""
        self.desc.set_text(self._prefilled)

    def _start_from_keyboard(self, event):
        if not self.session:
            self.start_work()
        return "break"

    def start_work(self):
        if self.session:
            return
        company = self.selected_company()
        if not company:
            messagebox.showwarning(t("app_title"), t("choose_company"), parent=self.root)
            return
        description = self.desc.text().strip()
        store.active_start(company["id"], company["name"], description)
        store.meta_set("last_company", company["name"])
        self.session = store.active_get()
        self.compact = True
        self._refresh()

    def pause_work(self):
        store.active_pause()
        self.session = store.active_get()
        self._refresh()

    def resume_work(self):
        store.active_resume()
        self.session = store.active_get()
        self._refresh()

    def stop_work(self):
        entry = store.active_stop()
        self.session = None
        self.compact = False
        self.desc.configure(state="normal")
        self.desc.set_text("")
        self._prefilled = ""
        self._refresh()
        self._prefill_description()
        if entry:
            self.flash(t("saved", value=fmt_hm(entry["seconds"])))

    def flash(self, text):
        self.status_lbl.configure(text=text, fg=GREEN)
        self.root.after(4000, self._clear_flash)

    def _clear_flash(self):
        if not self.session:
            self.status_lbl.configure(text=t("ready"), fg=MUTED)

    # -------------------------------------------------------------- render

    def reload_companies(self):
        self.companies = store.list_companies()
        self._refresh()

    def _refresh(self):
        names = [c["name"] for c in self.companies]
        self.company_cb["values"] = names
        if self.session:
            current = self.session["company_name"]
        elif self.company_var.get() in names:
            current = self.company_var.get()
        else:
            current = store.meta_get("last_company", names[0] if names else "")
            if current not in names and names:
                current = names[0]
        if current or not self.company_var.get():
            self.company_var.set(current)

        if self.session:
            description = self.session["description"]
            self.desc.configure(state="normal")
            if self.desc.text().strip() != description:
                self.desc.set_text(description)
            self.desc.configure(state="disabled")
        else:
            self.desc.configure(state="normal")
        self._refresh_recent()

        self._render_actions()
        self._apply_mode()
        self._update_labels()

    def _render_actions(self):
        for widget in self.actions.winfo_children():
            widget.destroy()

        if not self.session:
            flat_button(self.actions, t("start"), self.start_work, bg=ACCENT,
                        fg="#ffffff", font=(FONT, 11, "bold"), pady=10).grid(
                row=0, column=0, columnspan=2, sticky="ew")
        elif self.session["paused"]:
            flat_button(self.actions, t("resume"), self.resume_work, bg=GREEN,
                        fg="#ffffff", font=(FONT, 10, "bold"), pady=10).grid(
                row=0, column=0, sticky="ew", padx=(0, 4))
            flat_button(self.actions, t("stop_save"), self.stop_work, bg=RED,
                        fg="#ffffff", font=(FONT, 10, "bold"), pady=10).grid(
                row=0, column=1, sticky="ew", padx=(4, 0))
        else:
            flat_button(self.actions, t("pause"), self.pause_work, bg=AMBER,
                        fg="#ffffff", font=(FONT, 10, "bold"), pady=10).grid(
                row=0, column=0, sticky="ew", padx=(0, 4))
            flat_button(self.actions, t("stop_save"), self.stop_work, bg=RED,
                        fg="#ffffff", font=(FONT, 10, "bold"), pady=10).grid(
                row=0, column=1, sticky="ew", padx=(4, 0))

    def _tick(self):
        self._update_labels()
        self.root.after(1000, self._tick)

    def _update_labels(self):
        today = dt.date.today()
        company = self.selected_company()

        if self.session:
            elapsed = store.active_elapsed(self.session)
            self.timer_lbl.configure(text=fmt_hms(elapsed))
            self.mini_timer.configure(
                text=fmt_hms(elapsed),
                fg=AMBER if self.session["paused"] else TEXT)
            if self.session["paused"]:
                self.timer_lbl.configure(fg=AMBER)
                self.status_lbl.configure(text=t("paused"), fg=AMBER)
            else:
                self.timer_lbl.configure(fg=TEXT)
                self.status_lbl.configure(text=t("working"), fg=GREEN)
            day_total = store.seconds_for_day(today, self.session["company_id"])
            if self.session["started"].date() == today:
                day_total += elapsed
            started_text = self.session["started"].strftime("%H:%M")
            self.meta_lbl.configure(
                text=f"{t('started_at', time=started_text)}   •   "
                     f"{t('today', value=fmt_hm(day_total))}"
            )
        else:
            self.timer_lbl.configure(text="00:00:00", fg=TEXT)
            self.mini_timer.configure(text="00:00:00", fg=TEXT)
            if self.status_lbl.cget("fg") != GREEN:
                self.status_lbl.configure(text=t("ready"), fg=MUTED)
            if company:
                total = store.seconds_for_day(today, company["id"])
                self.meta_lbl.configure(text=t("today", value=fmt_hm(total)))
            else:
                self.meta_lbl.configure(text="")

    # ------------------------------------------------------------- windows

    def open_history(self):
        if self._history_window and self._history_window.winfo_exists():
            self._history_window.lift()
            self._history_window.focus_force()
            return
        self._history_window = HistoryWindow(self)

    def open_settings(self):
        if self._settings_window and self._settings_window.winfo_exists():
            self._settings_window.lift()
            self._settings_window.focus_force()
            return
        self._settings_window = SettingsWindow(self)

    def export_excel(self):
        out_dir = store.meta_get("export_dir") or os.path.join(store.BASE_DIR, "exports")
        groups = store.entries_grouped()
        if not any(group["entries"] for group in groups):
            messagebox.showinfo(t("export_title"), t("export_nothing"), parent=self.root)
            return
        try:
            paths = exporter.export_groups(groups, out_dir)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(t("export_title"), t("error_file", error=exc),
                                 parent=self.root)
            return
        names = "\n".join(os.path.basename(path) for path in paths)
        if messagebox.askyesno(
            t("export_title"),
            t("export_done", names=names, folder=out_dir),
            parent=self.root,
        ):
            try:
                os.startfile(out_dir)
            except Exception:  # noqa: BLE001
                pass


class HistoryWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.configure(bg=BG)
        self.title(t("history_title"))
        self.attributes("-topmost", True)
        self.transient(app.root)
        self.geometry(fit_geometry(self, 860, 520, app.x, app.y - 60))
        self.minsize(640, 360)
        self._build()
        self._load()

    def _build(self):
        wrapper = tk.Frame(self, bg=BG)
        wrapper.pack(fill="both", expand=True, padx=14, pady=12)
        wrapper.grid_columnconfigure(1, weight=1)
        wrapper.grid_rowconfigure(1, weight=1)

        tk.Label(wrapper, text=t("company"), bg=BG, fg=MUTED, font=(FONT, 9)).grid(
            row=0, column=0, sticky=start_anchor(), padx=(0, 8), pady=(0, 8))

        self.filter_var = tk.StringVar(value=t("all_companies"))
        self.filter_cb = dark_combo(
            wrapper, textvariable=self.filter_var, font=(FONT, 9), width=28,
            values=[t("all_companies")] + [c["name"] for c in self.app.companies],
        )
        self.filter_cb.grid(row=0, column=1, sticky="w", pady=(0, 8))
        self.filter_cb.bind("<<ComboboxSelected>>", lambda e: self._load())

        self.sum_lbl = tk.Label(wrapper, text="", bg=BG, fg=MUTED, font=(FONT, 9))
        self.sum_lbl.grid(row=0, column=2, sticky="w", padx=(16, 0), pady=(0, 8))

        tree_frame = tk.Frame(wrapper, bg=BORDER)
        tree_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("company", "date", "start", "end", "duration", "description")
        headings = {
            "company": t("col_company"), "date": t("col_date"),
            "start": t("col_start"), "end": t("col_end"),
            "duration": t("col_duration"), "description": t("col_description"),
        }
        widths = {"company": 130, "date": 140, "start": 70, "end": 70,
                  "duration": 80, "description": 320}
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 style="Dark.Treeview", selectmode="extended")
        for column in columns:
            self.tree.heading(column, text=headings[column], anchor=start_anchor())
            self.tree.column(column, width=widths[column],
                             anchor=start_anchor() if column == "description" else "e",
                             stretch=(column == "description"))
        if i18n.is_rtl():
            self.tree.configure(displaycolumns=tuple(reversed(columns)))
        self.tree.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 1), pady=1)
        self.tree.configure(yscrollcommand=scroll.set)

        buttons = tk.Frame(wrapper, bg=BG)
        buttons.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        flat_button(buttons, t("delete_selected"), self._delete_selected, bg=RED,
                    fg="#ffffff", font=(FONT, 9, "bold")).pack(side="right")
        flat_button(buttons, t("edit_description"), self._edit_selected, bg=ACCENT,
                    fg="#ffffff", font=(FONT, 9, "bold")).pack(side="right", padx=(0, 8))
        flat_button(buttons, t("close"), self.destroy, bg=FIELD, fg=MUTED,
                    font=(FONT, 9)).pack(side="left")
        tk.Label(buttons, text=t("delete_hint"), bg=BG, fg=MUTED,
                 font=(FONT, 8)).pack(side="left", padx=12)

    def _load(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        selected = self.filter_var.get()
        company_id = None
        if selected != t("all_companies"):
            company = next((c for c in self.app.companies if c["name"] == selected), None)
            company_id = company["id"] if company else -1
        entries = store.entries_list(company_id)
        total = 0
        for entry in entries:
            total += entry["seconds"]
            self.tree.insert(
                "", "end", iid=str(entry["id"]),
                values=(
                    rtl_text(entry["company_name"]),
                    rtl_text(i18n.format_date_of(entry["start"].date())),
                    rtl_text(f"{entry['start']:%H:%M}"),
                    rtl_text(f"{entry['end']:%H:%M}"),
                    rtl_text(fmt_hm(entry["seconds"])),
                    rtl_text(entry["description"]),
                ),
            )
        self.sum_lbl.configure(
            text=t("rows_summary", rows=len(entries), total=fmt_hm(total)))

    def _delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(t("delete"), t("select_row"), parent=self)
            return
        if not messagebox.askyesno(t("delete"),
                                   t("delete_confirm", count=len(selection)),
                                   parent=self):
            return
        for item in selection:
            store.entry_delete(int(item))
        self._load()
        self.app._update_labels()

    def _on_tree_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self._edit_row(item)

    def _edit_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(t("edit_description"), t("select_row"), parent=self)
            return
        self._edit_row(selection[0])

    def _edit_row(self, item):
        entry_id = int(item)
        DescriptionEditor(
            self, store.entry_description(entry_id),
            lambda text: self._save_description(entry_id, text),
        )

    def _save_description(self, entry_id, description):
        store.entry_set_description(entry_id, description)
        self._load()
        self.app.flash(t("description_updated"))


class DescriptionEditor(tk.Toplevel):
    """ویرایش شرح یک سابقهٔ ثبت‌شده."""

    def __init__(self, parent, description, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.configure(bg=BG)
        self.title(t("edit_description"))
        self.attributes("-topmost", True)
        self.transient(parent)
        self.resizable(False, False)
        self.geometry(fit_geometry(self, 420, 240,
                                   parent.winfo_rootx() + parent.winfo_width() // 2,
                                   parent.winfo_rooty() + parent.winfo_height() // 2))

        tk.Label(self, text=t("edit_description"), bg=BG, fg=TEXT,
                 font=(FONT, 10, "bold"), anchor=start_anchor()).pack(
            fill="x", padx=14, pady=(12, 6))
        self.field = RtlTextField(self, height=4, bg=FIELD, fg=TEXT)
        self.field.pack(fill="both", expand=True, padx=14)
        self.field.set_text(description)

        buttons = tk.Frame(self, bg=BG)
        buttons.pack(fill="x", padx=14, pady=(10, 12))
        flat_button(buttons, t("save"), self._save, bg=ACCENT, fg="#ffffff",
                    font=(FONT, 9, "bold"), padx=18, pady=6).pack(side=start_side())
        flat_button(buttons, t("cancel"), self.destroy, bg=FIELD, fg=MUTED,
                    font=(FONT, 9), padx=18, pady=6).pack(side=end_side())
        self.bind("<Escape>", lambda event: self.destroy())
        self.after(50, self.field.focus_force)

    def _save(self):
        text = self.field.text().strip()
        self.destroy()
        self.on_save(text)


class SettingsWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.configure(bg=BG)
        self.title(t("settings_title"))
        self.attributes("-topmost", True)
        self.transient(app.root)
        self.resizable(False, False)
        self._build()
        self._load()
        self.update_idletasks()
        self.geometry(fit_geometry(self, self.winfo_reqwidth(),
                                   self.winfo_reqheight(),
                                   app.x, app.y - 80))

    def _build(self):
        wrapper = tk.Frame(self, bg=BG)
        wrapper.pack(fill="both", expand=True, padx=16, pady=14)

        language_row = tk.Frame(wrapper, bg=BG)
        language_row.pack(fill="x", pady=(0, 12))
        tk.Label(language_row, text=t("language"), bg=BG, fg=MUTED,
                 font=(FONT, 9)).pack(side=start_side(), padx=(0, 8))
        self.lang_var = tk.StringVar(value=i18n.language_name())
        self.lang_cb = dark_combo(
            language_row, textvariable=self.lang_var, width=16,
            values=[name for _code, name in i18n.LANGUAGES],
        )
        self.lang_cb.pack(side=start_side())
        self.lang_cb.bind("<<ComboboxSelected>>", self._change_language)

        theme_row = tk.Frame(wrapper, bg=BG)
        theme_row.pack(fill="x", pady=(0, 12))
        tk.Label(theme_row, text=t("theme"), bg=BG, fg=MUTED,
                 font=(FONT, 9)).pack(side=start_side(), padx=(0, 8))
        self.theme_var = tk.StringVar(value=t("theme_" + self.app.theme))
        self.theme_cb = dark_combo(
            theme_row, textvariable=self.theme_var, width=16,
            values=[t("theme_" + key) for key in THEME_KEYS],
        )
        self.theme_cb.pack(side=start_side())
        self.theme_cb.bind("<<ComboboxSelected>>", self._change_theme)

        placement_row = tk.Frame(wrapper, bg=BG)
        placement_row.pack(fill="x", pady=(0, 12))
        tk.Label(placement_row, text=t("placement"), bg=BG, fg=MUTED,
                 font=(FONT, 9)).pack(side=start_side(), padx=(0, 8))
        self.dock_var = tk.StringVar(value=t("dock_" + self.app.dock))
        self.dock_cb = dark_combo(
            placement_row, textvariable=self.dock_var, width=26,
            values=[t("dock_" + key) for key in DOCK_KEYS],
        )
        self.dock_cb.pack(side=start_side())
        self.dock_cb.bind("<<ComboboxSelected>>", self._change_dock)

        tk.Label(wrapper, text=t("my_companies"), bg=BG, fg=TEXT,
                 font=(FONT, 10, "bold")).pack(anchor=start_anchor())
        tree_frame = tk.Frame(wrapper, bg=BORDER)
        tree_frame.pack(fill="x", pady=(6, 12))
        self.tree = ttk.Treeview(tree_frame, columns=("name", "cycle"), show="headings",
                                 height=6, style="Dark.Treeview", selectmode="browse")
        self.tree.heading("name", text=t("company_name"), anchor=start_anchor())
        self.tree.heading("cycle", text=t("cycle_start"), anchor=start_anchor())
        self.tree.column("name", width=200, anchor=start_anchor())
        self.tree.column("cycle", width=300, anchor=start_anchor())
        if i18n.is_rtl():
            self.tree.configure(displaycolumns=("cycle", "name"))
        self.tree.pack(side="right", fill="x", expand=True, padx=1, pady=1)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        form = tk.Frame(wrapper, bg=BG)
        form.pack(fill="x")
        form.grid_columnconfigure(1, weight=1)

        tk.Label(form, text=t("company_name"), bg=BG, fg=MUTED, font=(FONT, 9)).grid(
            row=0, column=0, sticky=start_anchor(), padx=(0, 8), pady=4)
        self.name_entry = dark_entry(form)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=4, ipady=5)

        tk.Label(form, text=t("cycle_start"), bg=BG, fg=MUTED, font=(FONT, 9)).grid(
            row=1, column=0, sticky=start_anchor(), padx=(0, 8), pady=4)
        self.day_var = tk.StringVar(value="1")
        self.day_spin = tk.Spinbox(
            form, from_=1, to=31, textvariable=self.day_var, width=6,
            bg=FIELD, fg=TEXT, buttonbackground=FIELD, relief="flat",
            highlightthickness=1, highlightbackground=BORDER, font=(FONT, 10),
            justify="center", command=self._update_hint)
        self.day_spin.grid(row=1, column=1, sticky="w", pady=4, ipady=4)
        self.day_spin.bind("<KeyRelease>", self._update_hint)

        self.hint = tk.Label(wrapper, text="", bg=BG, fg=MUTED, font=(FONT, 8),
                             justify="right" if i18n.is_rtl() else "left",
                             anchor=start_anchor(), wraplength=510)
        self.hint.pack(fill="x", pady=(4, 10))

        buttons = tk.Frame(wrapper, bg=BG)
        buttons.pack(fill="x")
        flat_button(buttons, t("new_company"), self._new, bg=FIELD, fg=TEXT,
                    font=(FONT, 9)).pack(side=start_side())
        flat_button(buttons, t("save_changes"), self._save, bg=ACCENT, fg="#ffffff",
                    font=(FONT, 9, "bold")).pack(side=start_side(), padx=8)
        flat_button(buttons, t("delete"), self._delete, bg=RED, fg="#ffffff",
                    font=(FONT, 9)).pack(side=end_side())

        tk.Frame(wrapper, bg=BORDER, height=1).pack(fill="x", pady=(16, 12))

        startup_row = tk.Frame(wrapper, bg=BG)
        startup_row.pack(fill="x", pady=(0, 12))
        tk.Label(startup_row, text=t("autostart"), bg=BG, fg=TEXT,
                 font=(FONT, 9, "bold")).pack(side=start_side())
        self.autostart_btn = flat_button(
            startup_row, "", self._toggle_autostart, bg=FIELD, fg=MUTED,
            font=(FONT, 8), padx=8, pady=4)
        self.autostart_btn.pack(side=end_side())
        self._paint_autostart()

        tk.Frame(wrapper, bg=BORDER, height=1).pack(fill="x", pady=(4, 12))

        tk.Label(wrapper, text=t("export_dir"), bg=BG, fg=TEXT,
                 font=(FONT, 9, "bold")).pack(anchor=start_anchor())
        row = tk.Frame(wrapper, bg=BG)
        row.pack(fill="x", pady=(6, 0))
        self.dir_lbl = tk.Label(row, text="", bg=BG, fg=MUTED, font=(FONT, 8),
                                anchor=start_anchor(), wraplength=320,
                                justify="right" if i18n.is_rtl() else "left")
        self.dir_lbl.pack(side=start_side(), fill="x", expand=True)
        flat_button(row, t("change_folder"), self._choose_dir, bg=FIELD, fg=TEXT,
                    font=(FONT, 8)).pack(side=end_side())

        flat_button(wrapper, t("close"), self.destroy, bg=FIELD, fg=MUTED,
                    font=(FONT, 9)).pack(anchor=end_anchor(), pady=(16, 0))

    def _load(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for company in self.app.companies:
            self.tree.insert("", "end", iid=str(company["id"]), values=(
                rtl_text(company["name"]),
                rtl_text(exporter.period_label(company["cycle_start_day"])),
            ))
        out_dir = store.meta_get("export_dir") or os.path.join(store.BASE_DIR, "exports")
        self.dir_lbl.configure(text=out_dir)

    def _change_language(self, event=None):
        chosen = self.lang_var.get()
        code = next((c for c, name in i18n.LANGUAGES if name == chosen), i18n.current())
        self.app.set_language(code)
        self.app.open_settings()

    def _change_theme(self, event=None):
        chosen = self.theme_var.get()
        key = next((k for k in THEME_KEYS if t("theme_" + k) == chosen), None)
        if key:
            self.app.set_theme(key)
            self.app.open_settings()

    def _change_dock(self, event=None):
        chosen = self.dock_var.get()
        key = next((k for k in DOCK_KEYS if t("dock_" + k) == chosen), None)
        if key:
            self.app.set_dock(key)

    def _paint_autostart(self):
        try:
            enabled = autostart.is_enabled()
        except Exception:  # noqa: BLE001
            enabled = False
        self.autostart_btn.configure(
            text=t("autostart_on") if enabled else t("autostart_off"),
            fg=GREEN if enabled else MUTED,
        )

    def _toggle_autostart(self):
        try:
            autostart.toggle()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(t("settings_error"), t("autostart_error", error=exc),
                                 parent=self)
            return
        self._paint_autostart()

    def _on_select(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return
        company = store.company_by_id(int(selection[0]))
        if not company:
            return
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, company["name"])
        self.day_var.set(str(company["cycle_start_day"]))
        self._update_hint()

    def _update_hint(self, event=None):
        try:
            day = int(self.day_var.get())
        except (TypeError, ValueError):
            return
        day = max(1, min(31, day))
        _key, start, end = exporter.period_of(dt.date.today(), day)
        self.hint.configure(
            text=t("cycle_preview", label=exporter.period_label(day),
                   start=i18n.format_date_of(start), end=i18n.format_date_of(end)))

    def _new(self):
        self.tree.selection_remove(self.tree.selection())
        self.name_entry.delete(0, "end")
        self.day_var.set("1")
        self._update_hint()
        self.name_entry.focus_set()

    def _save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning(t("company"), t("name_required"), parent=self)
            return
        try:
            day = max(1, min(31, int(self.day_var.get())))
        except (TypeError, ValueError):
            day = 1
        selection = self.tree.selection()
        company_id = int(selection[0]) if selection else None
        if store.company_name_exists(name, company_id):
            messagebox.showwarning(t("company"), t("company_exists"), parent=self)
            return
        store.save_company(name, day, company_id)
        self.app.reload_companies()
        self._load()
        if company_id:
            self.tree.selection_set(str(company_id))
        self.app._update_labels()

    def _delete(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(t("delete"), t("select_row"), parent=self)
            return
        company = store.company_by_id(int(selection[0]))
        if not company:
            return
        if not messagebox.askyesno(t("delete"),
                                   t("delete_company_confirm", name=company["name"]),
                                   parent=self):
            return
        store.delete_company(company["id"])
        self.app.reload_companies()
        self._new()
        self._load()

    def _choose_dir(self):
        chosen = filedialog.askdirectory(parent=self, title=t("export_dir"))
        if chosen:
            store.meta_set("export_dir", os.path.normpath(chosen))
            self.dir_lbl.configure(text=os.path.normpath(chosen))
