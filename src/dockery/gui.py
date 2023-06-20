import threading
from rich.text import TextType
from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, ContentSwitcher, Tabs, Tab
from textual.widgets._header import HeaderClock
from textual.containers import (
    VerticalScroll,
    Horizontal,
    Vertical,
    Container as Group,
    Grid,
)
from textual.reactive import reactive
from textual.events import Resize
from docker import DockerClient, errors
from docker.models.containers import Container

from .utils import get_cpu_usage, get_mem_usage
from .logs import LogsButton
from .buttons import CustomButton


class AppGUI(App):
    CSS_PATH = "style.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]
    TITLE = "DOCKERY"

    def __init__(self, docker: DockerClient, **kargs):
        self.docker = docker
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        with Horizontal(id="header"):
            yield HeaderClock()
            yield Tabs(
                Tab("Containers", id="container-list"),
                Tab("Logs", id="container-logs"),
                id="nav",
            )
        yield Footer()
        with ContentSwitcher():
            yield ContainersList(self.docker, id="container-list")
            with VerticalScroll(id="container-logs"):
                yield Static("", id="logs")

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        self.query_one(ContentSwitcher).current = event.tab.id


class ContainersList(VerticalScroll):
    container_count = reactive(0)

    def __init__(self, docker: DockerClient, **kargs):
        self.containers = []
        self.docker = docker
        self.grid = Grid()
        super().__init__(**kargs)

    # def compose(self) -> ComposeResult:
    #     yield self.grid

    def on_mount(self) -> None:
        self.get_containers()
        self.set_interval(2, self.count_timer)

    def count_timer(self) -> None:
        thread = threading.Thread(target=self.get_containers)
        thread.start()

    async def watch_container_count(self, count: int) -> None:
        # await self.grid.remove_children()
        await self.remove_children()
        for c in self.containers:
            cw = ContainerWidget(c, self.docker)  # type: ignore
            # self.grid.mount(cw)
            self.mount(cw)

    def get_containers(self) -> None:
        self.containers = self.docker.containers.list(all=True)
        self.container_count = len(self.containers)

    # def on_resize(self, e: Resize):
    #     print(e)


class ContainerWidget(Static):
    def __init__(self, container: Container, client: DockerClient, **kargs):
        self.container = container
        self.client = client
        self.container_id = container.id
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Group(
            Static("[b]" + (self.container.name or "")),
            Vertical(
                ReactiveString(id="status"),
                Horizontal(ReactiveString(id="cpu"), ReactiveString(id="mem")),
                classes="stats-text",
            ),
            classes="container-info",
        )

        yield Group(StatusButtons(self.container))

    def on_mount(self):
        self.set_interval(1, self.data_timer)
        self.running = True
        thread = threading.Thread(target=self.update_usage, daemon=True)
        thread.start()

    def data_timer(self) -> None:
        thread = threading.Thread(target=self.update_data, daemon=True)
        thread.start()

    def update_data(self) -> None:
        try:
            c: Container = self.client.containers.get(self.container_id)  # type: ignore
        except errors.NotFound:
            return None
        else:
            self.container = c
            status = c.status.capitalize()
            self.query_one("#status", ReactiveString).text = (
                "[green]" if status == "Running" else "[bright_black]"
            ) + status

    def update_usage(self) -> None:
        c = self.container
        cpu = self.query_one("#cpu", ReactiveString)
        mem = self.query_one("#mem", ReactiveString)
        for stat in c.stats(stream=True, decode=True):
            if not self.running:  # finish the thread
                return None
            cpu.text = f"CPU: {get_cpu_usage(stat):.1f}"
            mem.text = f"MEM: {get_mem_usage(stat):.1f}"

    def on_unmount(self):
        self.running = False


class ReactiveString(Static):
    text = reactive("")

    def __init__(self, **kargs):
        super().__init__(shrink=True, expand=True, **kargs)

    def render(self) -> TextType:
        return self.text


class StatusButtons(Static):
    def __init__(self, container: Container, **kargs):
        self.container = container
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Horizontal(
            StartStopButton(self.container),
            RestartButton(self.container),
            LogsButton(self.container),
            classes="buttons-container",
        )


class StartStopButton(Static):
    running = reactive(bool)

    def __init__(self, container: Container, **kargs):
        self.container = container
        super().__init__(**kargs)

    def on_click(self) -> None:
        self.running = not self.running
        if self.running:
            self.container.start()
        else:
            self.container.stop()

    def on_mount(self) -> None:
        self.running = self.container.status == "running"

    def watch_running(self, running: bool):
        self.variant = "error" if running else "success"
        text = ":black_square_button:Stop" if running else ":arrow_forward: Start"
        btn = self.query_one(CustomButton)
        btn.text = text
        btn.color = "red" if running else "green"

    def compose(self) -> ComposeResult:
        yield CustomButton("Start")


class RestartButton(Static):
    def __init__(self, container: Container, **kargs):
        self.container = container
        super().__init__(**kargs)

    def on_click(self) -> None:
        self.container.restart()

    def compose(self) -> ComposeResult:
        yield CustomButton(":grey_exclamation:Restart", color="orange")
