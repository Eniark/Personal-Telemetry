import ctypes
import win32con
import pythoncom
import requests
import datetime
from configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION
import win32gui
import win32process
import psutil


BROWSERS = {
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "opera.exe",
    "brave.exe",
    "vivaldi.exe"
}

def get_event_category(window_id):
    _, pid = win32process.GetWindowThreadProcessId(window_id)
    process = psutil.Process(pid)
    if process.name().lower() in BROWSERS:
        return 'browser'
    return 'operating_system'

user32 = ctypes.windll.user32

def callback(hook, event, hwnd, idObject, idChild, thread, time):
    if hwnd: # the window ID
        length = user32.GetWindowTextLengthW(hwnd) # needed for C-language as C requires a fixed size memory buffer
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        
        if buffer.value:
            process_category = get_event_category(hwnd)
            data = {
                "process": buffer.value,
                "category": process_category,
                "started_at": datetime.datetime.now().strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION]
            }
            print(data)
            requests.post("http://127.0.0.1:8000/os_event", json=data)
            

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

while True:
    pythoncom.PumpWaitingMessages()