import uvicorn
from fastapi import FastAPI
from threading import Thread


class WindowsAgentServer:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.app = FastAPI()

        self._register_endpoints()

    def _register_endpoints(self):
        @self.app.post("/browser_event")
        async def receive_browser_event(event: dict):
            print('Browser event received')
            return {"ok": True}

    def run(self):
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            reload=False
        )

    def start(self):
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()