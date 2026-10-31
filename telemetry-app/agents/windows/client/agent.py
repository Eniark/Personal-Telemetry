import ctypes
import time
import win32con
import pythoncom
import requests
import datetime
import win32process
import psutil
import win32api
import threading
import os

from .api import WindowsAgentServer
from agents.windows.db.repository import EventRepository
from dotenv import load_dotenv
from queue import Queue, Empty
from collections import deque
from shared.configs import TIMESTAMP_FORMAT
from shared.utils import validate_env_variable
from shared.enums import EventType
from uuid import uuid4
from shared.utils import create_db_connection
from shared.configs import QUEUE_DB_PATH

load_dotenv()

class WindowsEventListener:
    def __init__(self, event_queue: Queue, browser_event_queue: list, queue_repository: EventRepository):
        self.repository = queue_repository
        self.event_queue = event_queue
        self.event = {}
        self.recent_windows = deque(maxlen=5)
        self.user32 = ctypes.windll.user32
        self.browser_event_queue = browser_event_queue

        # API-related properties
        self.retry_delay = 60
        self.max_retry_delay = 900
        self.next_retry_at = 0
        # =============

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

    def get_process_info(self, window_id: str):
        _, pid = win32process.GetWindowThreadProcessId(window_id)
        try:
            process = psutil.Process(pid)
            return process.name(), process.exe()
        except psutil.NoSuchProcess:
            return "Unknown", None

    def get_event_category(self, executable: str):
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

    def monitor_queue(self):
        monitor_thread = threading.Thread(target=self.__monitor_queue, daemon=True) # thread for monitor_queue process
        monitor_thread.start()

    def __monitor_queue(self):

        while True:
            data = [event_queue.get()]
            pending_events = repository.get_pending_events()
            data.extend(pending_events)
            
            try:
                if time.monotonic() < self.next_retry_at:
                    for event in data:
                        event['sent_at'] = None
                    repository.upsert_events(events=data, are_acknowledged=False)
                    continue

                try:
                    for event in data:
                        event['sent_at'] = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
                    response = requests.post(f"http://{TELEMETRY_SERVER_HOST}:{TELEMETRY_SERVER_PORT}/os_event", json=data)
                    print(response.text)
                    response.raise_for_status()

                    repository.upsert_events(events=data, are_acknowledged=True)

                    self.retry_delay = 60
                    self.next_retry_at = 0

                except requests.RequestException as e:
                    print(f"API is unavailable: {e}")
                    for event in data:
                        event['sent_at'] = None

                    repository.upsert_events(events=data, are_acknowledged=False)

                    self.next_retry_at = time.monotonic() + self.retry_delay

                    print(f"Next retry in {self.retry_delay} seconds.")

                    # Increasing the retry delay before the next request
                    self.retry_delay = min(
                        self.retry_delay * 2,
                        self.max_retry_delay
                    )

            finally:
                event_queue.task_done()


    def collect_browser_events(self):
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
                if self.event:
                    self.event["browser_events"].extend(self.collect_browser_events())
                    self.event["event_end_time"] = (datetime.datetime.now().strftime(TIMESTAMP_FORMAT))
                    self.event["recent_windows"] = tuple(self.recent_windows)

                    recent_object = self.event.copy()
                    del recent_object["recent_windows"]
                    self.recent_windows.appendleft(recent_object)

                    self.event_queue.put(self.event)

                self.event = {
                    "executable": executable,
                    "title": buffer.value,
                    "publisher": publisher_name,
                    "category": process_category,
                    "event_start_time": datetime.datetime.now().strftime(TIMESTAMP_FORMAT),
                    "browser_events": [],
                    "id": str(uuid4())
                }


if __name__=='__main__':

    validated_env_vars = validate_env_variable(REQUIRED_ENV_VARS=["WINDOWS_AGENT_SERVER_PORT", "TELEMETRY_SERVER_PORT"])
    WINDOWS_AGENT_SERVER_HOST = validated_env_vars[0]
    TELEMETRY_SERVER_PORT = validated_env_vars[1]
    TELEMETRY_SERVER_HOST = os.getenv("WINDOWS_AGENT_SERVER_HOST")

    event_queue = Queue()
    db = create_db_connection(QUEUE_DB_PATH)
    repository = EventRepository(db)
    server = WindowsAgentServer(host=TELEMETRY_SERVER_HOST, port=WINDOWS_AGENT_SERVER_HOST)
    listener = WindowsEventListener(event_queue, browser_event_queue=server.event_queue, queue_repository=repository)

    server.start()
    listener.monitor_queue()
    
    pythoncom.PumpMessages()
    