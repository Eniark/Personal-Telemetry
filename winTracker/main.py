import ctypes
import win32con
import pythoncom
import requests

user32 = ctypes.windll.user32

def callback(hook, event, hwnd, idObject, idChild, thread, time):
    if hwnd: # the window ID
        length = user32.GetWindowTextLengthW(hwnd) # needed for C-language as C requires a fixed size memory buffer
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        if buffer.value:
            print("Event:", buffer.value)
            data = {
                "process": buffer.value
            }
            request = requests.post("http://127.0.0.1:8000/os_event", json=data)
            

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