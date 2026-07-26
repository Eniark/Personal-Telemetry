import ctypes
import win32con
import pythoncom
import requests
import datetime
from shared.configs import TIMESTAMP_FORMAT, TIMESTAMP_MS_PRECISION
import win32process
import psutil
from dotenv import load_dotenv
import win32api
from queue import Queue
import threading
from shared.utils import get_env_variables
load_dotenv()

def get_process_info(window_id):
    _, pid = win32process.GetWindowThreadProcessId(window_id)
    try:
        process = psutil.Process(pid)
        return process.name(), process.exe()
    except psutil.NoSuchProcess:
        return "Unknown", None

def get_event_category(executable):
    BROWSER_EXECUTABLES = {
        "chrome.exe",
        "msedge.exe",
        "firefox.exe",
        "opera.exe",
        "brave.exe",
        "vivaldi.exe"
    }
    
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





def sender():
    while True:
        data = event_queue.get()
        try:
            print(data)
            requests.post(f"http://{HOST}:{PORT}/os_event", json=data)
        finally:
            event_queue.task_done()



def callback(hook, event, hwnd, idObject, idChild, thread, time):
    if hwnd: # the window ID
        length = user32.GetWindowTextLengthW(hwnd) # needed for C-language as C requires a fixed size memory buffer
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        
        if buffer.value:
            executable, absolute_path = get_process_info(hwnd)
            publisher_name = get_publisher_name(absolute_path)
            process_category = get_event_category(executable)
            data = {
                "process": executable,
                "title": buffer.value,
                "publisher": publisher_name,
                "category": process_category,
                "event_time": datetime.datetime.now().strftime(TIMESTAMP_FORMAT)[:TIMESTAMP_MS_PRECISION]
            }

            event_queue.put(data)
            threading.Thread(target=sender, daemon=True).start() # so no blocking of main thread happens

if __name__=='__main__':
    event_queue = Queue()
    user32 = ctypes.windll.user32

    HOST, PORT = get_env_variables()

    WinEventProc = ctypes.WINFUNCTYPE(
        None, ctypes.c_void_p, ctypes.c_uint,
        ctypes.c_void_p, ctypes.c_long, ctypes.c_long,
        ctypes.c_uint, ctypes.c_uint
    )

    hook_cb = WinEventProc(callback)

    user32.SetWinEventHook(
        win32con.EVENT_SYSTEM_FOREGROUND, # Starting range of event types to track
        win32con.EVENT_SYSTEM_FOREGROUND, # Ending range of event types to track
        0,
        hook_cb,
        0,
        0,
        win32con.WINEVENT_OUTOFCONTEXT
    )

    pythoncom.PumpMessages()