import threading
import time
from textual.app import ComposeResult
from textual.widgets import Static, TextLog, Tabs
from textual.reactive import reactive
from textual.containers import VerticalScroll
from docker.models.containers import Container

from .custom_widgets import CustomButton


class LogsButton(Static):
    def __init__(self, container: Container, **kargs):
        self.container = container
        super().__init__(**kargs)

    async def on_click(self) -> None:
        cl = self.app.query_one("VerticalScroll#container-logs", VerticalScroll)
        await cl.remove_children()
        lc = LogsContainer(self.container)
        await cl.mount(lc)
        self.app.query_one("#nav", Tabs).active = "container-logs"

    def compose(self) -> ComposeResult:
        yield CustomButton(":notebook:Logs", color="blue")


class LogsContainer(TextLog):
    last_log = reactive("")

    def __init__(self, container: Container, **kargs):
        self.container = container
        super().__init__(highlight=True, auto_scroll=True, wrap=True, **kargs)

    def on_mount(self) -> None:
        self.running = True
        self.thread = threading.Thread(target=self.update_log, daemon=True)
        self.thread.start()

    async def watch_last_log(self, new_log: str):
        self.write(new_log)

    def update_log(self) -> None:
        # Get the last 40 logs(get all logs can be slow)
        logs: bytes = self.container.logs(tail=40)
        self.last_log = logs.decode()
        # Start streaming logs(since last second)
        for log in self.container.logs(stream=True, since=time.time() - 1):
            if not self.running:
                # Finish the thread after removing the widget
                # TODO: it doesn't finish immediately, fix that
                return None
            self.last_log = log.decode()

    def on_unmount(self):
        self.running = False
