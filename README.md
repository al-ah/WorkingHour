# WorkingHour

A small Windows widget for logging freelance working hours, with a monthly Excel export.

## Running

```
pip install -r requirements.txt
python app.py
```

Or double-click `run.bat` (it runs without a console window).

To start it automatically when Windows starts, right-click `run.bat` and copy a
shortcut to it into the `shell:startup` folder.

## Usage

1. Pick a company from the list.
2. Type the work description.
3. Press “Start work”. If you step away, press “Pause” and press “Resume” when you return.
4. “Finish & save” stores the entry; it can be deleted from “History”.
5. “Excel export” creates one file per company, with one sheet per month.

## Monthly cycle

In the “Companies” window, set “Cycle start” for each company:

- `1` → the full Jalali (Persian) month (first to last day).
- `28` → the cycle runs from the 28th of the previous month to the 27th of the
  current one; this is what you see in the “Working Hours - Project A” file
  (the Mehr sheet includes 30 and 31 Shahrivar).
- Any other number between 1 and 31 also works.

The sheet name and month label are the month in which the cycle ends.

## Compact mode and placement

Pressing “Start work” collapses the widget into a small bar (timer + pause/resume +
finish), and “Finish & save” expands it again. The `▣` button on that bar expands it
temporarily.

Placement is set in two ways: the `⋯` button in the widget header, or the “Widget
placement” field in the “Companies” window. Options:

- Above the taskbar clock (default)
- Top/bottom corners of the screen
- Inside the taskbar (the bar takes the taskbar height and sits next to the clock)
- Free move: just drag the bar with the mouse; “free” mode is enabled automatically.

The `◉` button toggles “always on top” (it is always on in inside-taskbar mode).

## Clock-area icon

While the app is running, a clock icon appears in the Windows notification area
(next to the clock). A left click hides/shows the widget, and the right-click menu
has two entries: “Hide widget” (or “Show widget”) and “Quit” — quitting asks for
confirmation first if a session is running, just like the `✕` button.

Windows 11 keeps new icons in the `^` overflow area first; if you want it next to
the clock permanently, drag it out of that area onto the taskbar.

## Themes

Four themes: Dark (default), Light, Ocean and Forest. Choose one from the “Theme”
field in the “Companies” window or from the “Theme” submenu of the `⋯` menu; your
choice is saved and persists across runs.

## Language and text direction

Pick the UI language in the “Companies” window: فارسی, English or العربية. The
direction of the whole interface, and of typing in the “Work description” box,
follows the selected language (Persian/Arabic right-to-left, English left-to-right).
Excel sheet names and column headers are generated in the same language too.

## Standalone exe

`dist\WorkingHour.exe` is the standalone build and runs on Windows without Python
installed. The `storage` (database) and `exports` (Excel output) folders are created
next to that file, so you can move the exe to any folder and your data travels with
it.

To rebuild after changing the code, double-click `build.bat`.

## Start with Windows

A shortcut named `WorkingHour.lnk` is created in the Windows Startup folder:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WorkingHour.lnk
```

The “Start with Windows” button in the “Companies” window creates or removes that
file; you can also delete the file itself to disable it. In every case only one
copy of the app runs (a second launch exits silently).

## Data

- `storage/worklog.db` — database of entries and settings.
- `exports/` — generated Excel files (changeable from the “Companies” window).

## License

Released under the MIT License — see [LICENSE](LICENSE).
