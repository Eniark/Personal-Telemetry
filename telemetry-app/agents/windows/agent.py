import ctypes
import win32con
import pythoncom
import requests
import datetime
import win32process
import psutil
import win32api
import threading
import pybreaker
import os

from .api import WindowsAgentServer
from dotenv import load_dotenv
from queue import Queue, Empty
from collections import deque
from shared.configs import TIMESTAMP_FORMAT
from shared.utils import validate_env_variable
from shared.enums import EventType
from uuid import uuid4

load_dotenv()

class WindowsEventListener:
    def __init__(self, event_queue: Queue, browser_event_queue: list):
        self.event_queue = event_queue
        self.current_object = {}
        self.recent_windows = deque(maxlen=5)
        self.user32 = ctypes.windll.user32
        self.browser_event_queue = browser_event_queue

        self._PYBREAKER_NUM_RETRIES = 3
        self._PYBREAKER_STREAM_LOCK_SECONDS = 5

        self.api_breaker = pybreaker.CircuitBreaker(
            fail_max=self._PYBREAKER_NUM_RETRIES,
            reset_timeout=self._PYBREAKER_STREAM_LOCK_SECONDS
        )

        self.hook_cb = ctypes.WINFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_long,
            ctypes.c_long,
            ctypes.c_uint,
            ctypes.c_uint
        )(self.__callback)

        self.user32.SetWinEventHook(
            win32con.EVENT_SYSTEM_FOREGROUND, # Starting range of event types to track
            win32con.EVENT_SYSTEM_FOREGROUND, # Ending range of event types to track
            0,
            self.hook_cb,
            0,
            0,
            win32con.WINEVENT_OUTOFCONTEXT
        )

    def get_process_info(self, window_id):
        _, pid = win32process.GetWindowThreadProcessId(window_id)
        try:
            process = psutil.Process(pid)
            return process.name(), process.exe()
        except psutil.NoSuchProcess:
            return "Unknown", None

    def get_event_category(self, executable):
        BROWSER_EXECUTABLES = {
            "chrome.exe",
            "msedge.exe",
            "firefox.exe",
            "opera.exe",
            "brave.exe",
            "vivaldi.exe"
        }
        
        if executable.lower() in BROWSER_EXECUTABLES:
            return EventType.BROWSER.value
        return EventType.OS.value

    def get_publisher_name(self, exe_path):
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

    def start_listening(self):
        listener_thread = threading.Thread(target=self.__start_listening, daemon=True) # thread for start_listening process
        listener_thread.start()

    def __start_listening(self):
        @self.api_breaker
        def relay_data(data):
            response = requests.post(f"http://{HOST}:{PORT}/os_event", json=data, timeout=self._PYBREAKER_STREAM_LOCK_SECONDS-3)
            response.raise_for_status()
            pass

        while True:
            data = event_queue.get()
            try:
                print(
                    data["executable"],
                    data["title"],
                    data["publisher"],
                    data["category"],
                    data['browser_events']
                )
                relay_data(data)
            except pybreaker.CircuitBreakerError:
                print(f"API temporarily unavailable. Locking for {self._PYBREAKER_STREAM_LOCK_SECONDS} seconds.")
            except requests.RequestException as e:
                print(f"Failed to send event: {e}")
            finally:
                event_queue.task_done()


    def drain_browser_events(self):
        events = []

        while True:
            try:
                events.append(self.browser_event_queue.get_nowait())
            except Empty:
                break

        return events

    def __callback(self, hook, event, hwnd, idObject, idChild, thread, time):
        if hwnd: # the window ID
            length = self.user32.GetWindowTextLengthW(hwnd) # needed for C-language as C requires a fixed size memory buffer
            buffer = ctypes.create_unicode_buffer(length + 1)
            self.user32.GetWindowTextW(hwnd, buffer, length + 1)
            
            if buffer.value:
                executable, absolute_path = self.get_process_info(hwnd)
                publisher_name = self.get_publisher_name(absolute_path)
                process_category = self.get_event_category(executable)
                if self.current_object:
                    self.current_object["browser_events"].extend(self.drain_browser_events())

                    self.current_object["event_end_time"] = (datetime.datetime.now().strftime(TIMESTAMP_FORMAT))
                    self.current_object["recent_windows"] = tuple(
                        self.recent_windows
                    )

                    recent_object = self.current_object.copy()
                    del recent_object["recent_windows"]
                    self.recent_windows.appendleft(recent_object)

                    self.event_queue.put(self.current_object)

                self.current_object = {
                    "executable": executable,
                    "title": buffer.value,
                    "publisher": publisher_name,
                    "category": process_category,
                    "event_start_time": datetime.datetime.now().strftime(
                        TIMESTAMP_FORMAT
                    ),
                    "browser_events": [],
                    "id": str(uuid4())
                }
                print('OS event received')


if __name__=='__main__':

    validated_env_vars = validate_env_variable(REQUIRED_ENV_VARS=["WINDOWS_AGENT_SERVER_PORT"])
    PORT = validated_env_vars[0]
    HOST = os.getenv("WINDOWS_AGENT_SERVER_HOST")

    event_queue = Queue()
    server = WindowsAgentServer(host=HOST, port=PORT)
    listener = WindowsEventListener(event_queue, browser_event_queue=server.event_queue)
    listener.start_listening()

    server.start()

    
    pythoncom.PumpMessages()
    