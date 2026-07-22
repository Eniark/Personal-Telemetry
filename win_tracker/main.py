import ctypes
import win32con
import pythoncom
import requests
import datetime
from configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION
import os
import win32process
import psutil
from dotenv import load_dotenv
import win32api
load_dotenv()

# FIXME: os.getenv returning None will cause int(None) to throw a TypeError and crash on startup if the .env file is missing or incomplete.
# SUGGESTION: Provide safe defaults: int(os.getenv("PORT", 8000)) or VALIDATE.
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

BROWSER_EXECUTABLES = {
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "opera.exe",
    "brave.exe",
    "vivaldi.exe"
}


def get_process_info(window_id):
    _, pid = win32process.GetWindowThreadProcessId(window_id)
    # FIXME: psutil.Process(pid) will throw psutil.AccessDenied for elevated system processes, and psutil.NoSuchProcess if the window closes too quickly. This will crash the hook.
    # SUGGESTION: Wrap this in a try-except block, and return fallback values (e.g. return "Unknown", None).
    process = psutil.Process(pid)
    return process.name(), process.exe()

def get_event_category(window_id):
    # FIXME: Performance issue. You already fetch process_info inside the callback, but you are re-fetching it here. psutil lookups are expensive on Windows.
    # SUGGESTION: Modify this function signature to accept the `executable` string directly instead of `window_id` so you don't query the OS twice for the same event.
    executable, _ = get_process_info(window_id)
    if executable.lower() in BROWSER_EXECUTABLES:
        return 'browser'
    return 'operating_system'

def get_publisher_name(exe_path):
    try:
        lang, codepage = win32api.GetFileVersionInfo(
            exe_path,
            r"\VarFileInfo\Translation"
        )[0]

        info = win32api.GetFileVersionInfo(
            exe_path,
            fr"\StringFileInfo\{lang:04x}{codepage:04x}\CompanyName"
        )

        return info
    except Exception:
        # FIXME: Bare Exception catches can hide serious bugs (!!!!! like KeyboardInterrupt or SystemExit).
        # SUGGESTION: Catch specific exceptions, or at least use `except Exception as e:` and log it in debug mode.
        return None


user32 = ctypes.windll.user32

def callback(hook, event, hwnd, idObject, idChild, thread, time):
    if hwnd: # the window ID
        length = user32.GetWindowTextLengthW(hwnd) # needed for C-language as C requires a fixed size memory buffer
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        
        if buffer.value:
            executable, absolute_path = get_process_info(hwnd)
            publisher_name = get_publisher_name(absolute_path)
            process_category = get_event_category(hwnd)
            data = {
                "process": executable,
                "title": buffer.value,
                "publisher": publisher_name,
                "category": process_category,
                "event_time": datetime.datetime.now().strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION]
            }
            print(data)
            # FIXME: CRITICAL PERFORMANCE BLOCKER. requests.post is synchronous. Doing network I/O inside a Windows system event hook callback will freeze the hook loop, cause system-wide stutter, and Windows will likely silently drop your hook for taking too long to return.
            # SUGGESTION: Decouple data extraction from network transmission. Put the `data` dictionary into a thread-safe Queue, and have a separate background worker thread pull from the queue to execute the `requests.post`.
            requests.post(f"http://{HOST}:{PORT}/os_event", json=data)
            

WinEventProc = ctypes.WINFUNCTYPE(
    None, ctypes.c_void_p, ctypes.c_uint,
    ctypes.c_void_p, ctypes.c_long, ctypes.c_long,
    ctypes.c_uint, ctypes.c_uint
)

hook_cb = WinEventProc(callback)

user32.SetWinEventHook(
    win32con.EVENT_SYSTEM_FOREGROUND, # Starting range of events to track
    win32con.EVENT_SYSTEM_FOREGROUND, # Ending range of events to track
    0,
    hook_cb,
    0,
    0,
    win32con.WINEVENT_OUTOFCONTEXT
)

# FIXME: CRITICAL CPU SPIKE. A `while True` loop without any sleep or blocking wait will pin a CPU core to 100% usage indefinitely.
# SUGGESTION: Replace this entire loop with `pythoncom.PumpMessages()`- it blocks the thread and yields CPU time while keeping the Windows message loop alive.
while True:
    pythoncom.PumpWaitingMessages()