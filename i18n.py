"""چندزبانگی برنامه: فارسی، انگلیسی و عربی (به همراه جهت RTL/LTR)."""

LANGUAGES = [("fa", "فارسی"), ("en", "English"), ("ar", "العربية")]
RTL_LANGUAGES = {"fa", "ar"}

_current = "fa"

STRINGS = {
    "fa": {
        "app_title": "ساعت کاری",
        "company": "شرکت",
        "description": "شرح کار",
        "ready": "آماده",
        "working": "در حال کار",
        "paused": "متوقف موقت",
        "start": "شروع کار",
        "pause": "توقف موقت",
        "stop_save": "پایان و ذخیره",
        "resume": "ادامه",
        "history": "تاریخچه",
        "export": "خروجی اکسل",
        "companies": "شرکت‌ها",
        "started_at": "شروع {time}",
        "today": "امروز: {value}",
        "saved": "ثبت شد • {value} ساعت",
        "exit_title": "خروج",
        "exit_question": "یک جلسه در جریان است. خارج می‌شوید؟\nزمان تا این لحظه ذخیره می‌شود.",
        "choose_company": "ابتدا یک شرکت را انتخاب کنید.",
        "export_title": "خروجی اکسل",
        "export_nothing": "هنوز ساعتی ثبت نشده است.",
        "export_done": "فایل‌های زیر ساخته شدند:\n\n{names}\n\n{folder}\n\nپوشه باز شود؟",
        "error_file": "خطا در ساخت فایل:\n{error}",
        "export_prefix": "ساعت کاری",
        "history_title": "سوابق کار",
        "all_companies": "همه شرکت‌ها",
        "col_company": "شرکت",
        "col_date": "تاریخ",
        "col_start": "شروع",
        "col_end": "پایان",
        "col_duration": "مدت",
        "col_description": "شرح کار",
        "rows_summary": "{rows} ردیف   •   جمع {total} ساعت",
        "delete_selected": "حذف انتخاب‌شده",
        "close": "بستن",
        "delete_hint": "برای حذف می‌توانید چند ردیف را با Ctrl انتخاب کنید.",
        "delete_confirm": "{count} ردیف حذف شود؟ این کار قابل بازگشت نیست.",
        "select_row": "ابتدا یک ردیف را انتخاب کنید.",
        "delete": "حذف",
        "recent_descriptions": "شرح‌های قبلی",
        "edit_description": "ویرایش شرح",
        "save": "ذخیره",
        "cancel": "انصراف",
        "description_updated": "شرح ویرایش شد",
        "settings_title": "شرکت‌ها و تنظیمات",
        "my_companies": "شرکت‌های من",
        "company_name": "نام شرکت",
        "cycle_start": "شروع دوره",
        "new_company": "شرکت جدید",
        "save_changes": "ذخیره تغییرات",
        "cycle_preview": "{label}\nدورهٔ شامل امروز: {start} تا {end}",
        "export_dir": "پوشهٔ خروجی اکسل",
        "change_folder": "تغییر پوشه",
        "language": "زبان برنامه",
        "theme": "پوستهٔ ظاهری",
        "theme_dark": "تیره",
        "theme_light": "روشن",
        "theme_ocean": "اقیانوس",
        "theme_forest": "جنگل",
        "autostart": "اجرا با شروع ویندوز",
        "autostart_on": "فعال — برای غیرفعال کردن کلیک کنید",
        "autostart_off": "غیرفعال — برای فعال کردن کلیک کنید",
        "autostart_error": "تغییر تنظیم اجرای خودکار ممکن نشد:\n{error}",
        "company_exists": "شرکتی با این نام وجود دارد.",
        "name_required": "نام شرکت را وارد کنید.",
        "delete_company_confirm": "«{name}» حذف شود؟\nسوابق ثبت‌شده پاک نمی‌شوند و در خروجی اکسل می‌مانند.",
        "placement": "جای‌گیری ویجت",
        "dock_above_clock": "بالای ساعت تسک‌بار",
        "dock_top_right": "گوشهٔ بالا راست صفحه",
        "dock_top_left": "گوشهٔ بالا چپ صفحه",
        "dock_bottom_left": "گوشهٔ پایین چپ صفحه",
        "dock_taskbar": "داخل تسک‌بار",
        "dock_free": "جابه‌جایی آزاد (هر جای صفحه)",
        "mini_start": "شروع",
        "mini_pause": "توقف",
        "mini_resume": "ادامه",
        "mini_stop": "پایان",
        "period_full": "کل ماه شمسی (۱ تا آخر ماه)",
        "period_custom": "{day} هر ماه تا {prev} ماه بعد",
        "period_preview": "دورهٔ شامل امروز: {start} تا {end}",
        "settings_error": "خطا",
        "tray_show": "نمایش ویجت",
        "tray_hide": "پنهان کردن ویجت",
        "tray_exit": "خروج از برنامه",
    },
    "en": {
        "app_title": "Working Hours",
        "company": "Company",
        "description": "Task",
        "ready": "Ready",
        "working": "Working",
        "paused": "Paused",
        "start": "Start work",
        "pause": "Pause",
        "stop_save": "Stop & save",
        "resume": "Resume",
        "history": "History",
        "export": "Excel export",
        "companies": "Companies",
        "started_at": "Started {time}",
        "today": "Today: {value}",
        "saved": "Saved • {value} h",
        "exit_title": "Exit",
        "exit_question": "A session is running. Exit anyway?\nThe time so far will be saved.",
        "choose_company": "Select a company first.",
        "export_title": "Excel export",
        "export_nothing": "No hours recorded yet.",
        "export_done": "These files were created:\n\n{names}\n\n{folder}\n\nOpen the folder?",
        "error_file": "Could not create the file:\n{error}",
        "export_prefix": "Working Hours",
        "history_title": "Work log",
        "all_companies": "All companies",
        "col_company": "Company",
        "col_date": "Date",
        "col_start": "Start",
        "col_end": "End",
        "col_duration": "Duration",
        "col_description": "Description",
        "rows_summary": "{rows} rows   •   total {total} h",
        "delete_selected": "Delete selected",
        "close": "Close",
        "delete_hint": "Use Ctrl to select several rows before deleting.",
        "delete_confirm": "Delete {count} row(s)? This cannot be undone.",
        "select_row": "Select a row first.",
        "delete": "Delete",
        "recent_descriptions": "Previous descriptions",
        "edit_description": "Edit description",
        "save": "Save",
        "cancel": "Cancel",
        "description_updated": "Description updated",
        "settings_title": "Companies & settings",
        "my_companies": "My companies",
        "company_name": "Company name",
        "cycle_start": "Cycle start",
        "new_company": "New company",
        "save_changes": "Save changes",
        "cycle_preview": "{label}\nPeriod containing today: {start} to {end}",
        "export_dir": "Excel output folder",
        "change_folder": "Change folder",
        "language": "Language",
        "theme": "Theme",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "theme_ocean": "Ocean",
        "theme_forest": "Forest",
        "autostart": "Start with Windows",
        "autostart_on": "On — click to turn off",
        "autostart_off": "Off — click to turn on",
        "autostart_error": "Could not change the startup setting:\n{error}",
        "company_exists": "A company with this name already exists.",
        "name_required": "Enter a company name.",
        "delete_company_confirm": "Delete \"{name}\"?\nRecorded hours are kept and stay in the Excel export.",
        "placement": "Widget placement",
        "dock_above_clock": "Above the taskbar clock",
        "dock_top_right": "Top right of the screen",
        "dock_top_left": "Top left of the screen",
        "dock_bottom_left": "Bottom left of the screen",
        "dock_taskbar": "Inside the taskbar",
        "dock_free": "Free position (drag anywhere)",
        "mini_start": "Start",
        "mini_pause": "Pause",
        "mini_resume": "Resume",
        "mini_stop": "Stop",
        "period_full": "Full month (1st to last day)",
        "period_custom": "Day {day} of each month to day {prev} of the next",
        "period_preview": "Period containing today: {start} to {end}",
        "settings_error": "Error",
        "tray_show": "Show widget",
        "tray_hide": "Hide widget",
        "tray_exit": "Exit application",
    },
    "ar": {
        "app_title": "ساعات العمل",
        "company": "الشركة",
        "description": "وصف العمل",
        "ready": "جاهز",
        "working": "قيد العمل",
        "paused": "متوقف مؤقتاً",
        "start": "بدء العمل",
        "pause": "إيقاف مؤقت",
        "stop_save": "إنهاء وحفظ",
        "resume": "متابعة",
        "history": "السجل",
        "export": "تصدير Excel",
        "companies": "الشركات",
        "started_at": "البدء {time}",
        "today": "اليوم: {value}",
        "saved": "تم الحفظ • {value} ساعة",
        "exit_title": "خروج",
        "exit_question": "هناك جلسة جارية. هل تريد الخروج؟\nسيتم حفظ الوقت حتى الآن.",
        "choose_company": "اختر شركة أولاً.",
        "export_title": "تصدير Excel",
        "export_nothing": "لم يتم تسجيل أي ساعات بعد.",
        "export_done": "تم إنشاء الملفات التالية:\n\n{names}\n\n{folder}\n\nهل تريد فتح المجلد؟",
        "error_file": "تعذر إنشاء الملف:\n{error}",
        "export_prefix": "ساعات العمل",
        "history_title": "سجل العمل",
        "all_companies": "كل الشركات",
        "col_company": "الشركة",
        "col_date": "التاريخ",
        "col_start": "البداية",
        "col_end": "النهاية",
        "col_duration": "المدة",
        "col_description": "وصف العمل",
        "rows_summary": "{rows} صف   •   المجموع {total} ساعة",
        "delete_selected": "حذف المحدد",
        "close": "إغلاق",
        "delete_hint": "استخدم Ctrl لاختيار أكثر من صف قبل الحذف.",
        "delete_confirm": "حذف {count} صف؟ لا يمكن التراجع عن ذلك.",
        "select_row": "اختر صفاً أولاً.",
        "delete": "حذف",
        "recent_descriptions": "أوصاف سابقة",
        "edit_description": "تعديل الوصف",
        "save": "حفظ",
        "cancel": "إلغاء",
        "description_updated": "تم تعديل الوصف",
        "settings_title": "الشركات والإعدادات",
        "my_companies": "شركاتي",
        "company_name": "اسم الشركة",
        "cycle_start": "بداية الدورة",
        "new_company": "شركة جديدة",
        "save_changes": "حفظ التغييرات",
        "cycle_preview": "{label}\nالدورة التي تشمل اليوم: {start} حتى {end}",
        "export_dir": "مجلد تصدير Excel",
        "change_folder": "تغيير المجلد",
        "language": "لغة البرنامج",
        "theme": "المظهر",
        "theme_dark": "داكن",
        "theme_light": "فاتح",
        "theme_ocean": "المحيط",
        "theme_forest": "الغابة",
        "autostart": "التشغيل مع بدء Windows",
        "autostart_on": "مفعّل — اضغط لإيقافه",
        "autostart_off": "معطّل — اضغط لتفعيله",
        "autostart_error": "لم يتم تغيير إعداد التشغيل التلقائي:\n{error}",
        "company_exists": "توجد شركة بهذا الاسم.",
        "name_required": "أدخل اسم الشركة.",
        "delete_company_confirm": "حذف «{name}»؟\nلن تُحذف الساعات المسجلة وستبقى في ملف Excel.",
        "placement": "موضع الأداة",
        "dock_above_clock": "فوق ساعة شريط المهام",
        "dock_top_right": "أعلى يمين الشاشة",
        "dock_top_left": "أعلى يسار الشاشة",
        "dock_bottom_left": "أسفل يسار الشاشة",
        "dock_taskbar": "داخل شريط المهام",
        "dock_free": "موضع حر (اسحب أينما تريد)",
        "mini_start": "بدء",
        "mini_pause": "إيقاف",
        "mini_resume": "متابعة",
        "mini_stop": "إنهاء",
        "period_full": "الشهر الكامل (من ١ إلى آخر يوم)",
        "period_custom": "من اليوم {day} من كل شهر إلى اليوم {prev} من الشهر التالي",
        "period_preview": "الدورة التي تشمل اليوم: {start} حتى {end}",
        "settings_error": "خطأ",
        "tray_show": "إظهار الأداة",
        "tray_hide": "إخفاء الأداة",
        "tray_exit": "خروج من البرنامج",
    },
}

MONTH_NAMES = {
    "fa": ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
           "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"],
    "en": ["Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar",
           "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"],
    "ar": ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
           "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"],
}

# datetime.weekday(): Monday == 0
WEEKDAY_NAMES = {
    "fa": ["دوشنبه", "سه شنبه", "چهارشنبه", "پنج شنبه", "جمعه", "شنبه", "یکشنبه"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "ar": ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"],
}

_FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹"


def set_language(code):
    global _current
    _current = code if code in dict(LANGUAGES) else "fa"
    return _current


def current():
    return _current


def language_name(code=None):
    code = code or _current
    return dict(LANGUAGES).get(code, code)


def is_rtl(lang=None):
    return (lang or _current) in RTL_LANGUAGES


def local_digits(text):
    if _current != "fa":
        return str(text)
    return "".join(_FA_DIGITS[int(ch)] if ch.isdigit() else ch for ch in str(text))


def t(key, **kwargs):
    table = STRINGS.get(_current) or STRINGS["fa"]
    text = table.get(key) or STRINGS["fa"].get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text
    return text


def month_name(month):
    names = MONTH_NAMES.get(_current, MONTH_NAMES["fa"])
    return names[month - 1]


def weekday_name(date):
    names = WEEKDAY_NAMES.get(_current, WEEKDAY_NAMES["fa"])
    return names[date.weekday()]


def format_date(year, month, day):
    return f"{local_digits(day)} {month_name(month)} {local_digits(year)}"


def format_date_of(date):
    import jalali

    year, month, day = jalali.from_date(date)
    return format_date(year, month, day)


def period_label(day):
    day = max(1, min(31, int(day or 1)))
    if day == 1:
        return t("period_full")
    return t("period_custom", day=local_digits(day), prev=local_digits(day - 1))
