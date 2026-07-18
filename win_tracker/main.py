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
    process = psutil.Process(pid)
    return process.name(), process.exe()

def get_event_category(window_id):
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

while True:
    pythoncom.PumpWaitingMessages()