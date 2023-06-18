import threading
from rich.text import TextType
from textual.app import App, ComposeResult
from textual.widgets import (
    Footer,
    Header,
    Static,
    Button,
    ContentSwitcher,
)
from textual.containers import (
    VerticalScroll,
    Horizontal,
    Vertical,
    Container as Group,
)
from textual.reactive import reactive
from textual.css import query
from docker import DockerClient, errors
from docker.models.containers import Container

from .utils import get_cpu_usage, get_mem_usage


class AppGUI(App):
    CSS_PATH = "style.css"
    BINDINGS = [
        ("h", "home", "Home"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]
    TITLE = "DOCKERY"
    container_count = reactive(0)

    def __init__(self, docker: DockerClient, **kargs):
        self.docker = docker
        self.containers = []
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with ContentSwitcher(initial="container-list"):
            yield VerticalScroll(id="container-list")
            with VerticalScroll(id="container-logs"):
                yield Static("", id="logs")

    def action_home(self) -> None:
        self.query_one(ContentSwitcher).current = "container-list"

    def on_mount(self) -> None:
        self.get_containers()
        self.set_interval(2, self.count_timer)

    def count_timer(self) -> None:
        thread = threading.Thread(target=self.get_containers)
        thread.start()

    def watch_container_count(self, count: int) -> None:
        print(f"{count=}")
        cl = self.app.query_one("#container-list")
        cl.remove_children()
        for c in self.containers:
            c_id = f"c{c.short_id}"
            try:
                cl.query_one(f"#{c_id}")
            except query.NoMatches:
                cw = ContainerWidget(c, self.docker, id=c_id)  # type: ignore
                cl.mount(cw)

    def get_containers(self) -> None:
        self.containers = self.docker.containers.list(all=True)
        self.container_count = len(self.containers)


class ContainerWidget(Static):
    not_found = reactive(False)

    def __init__(self, container: Container, client: DockerClient, **kargs):
        self.container = container
        self.client = client
        self.container_id = container.id
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Group(
            Static(self.container.name or ""),
            Static(self.container.short_id),
            classes="container-info",
        )
        yield Vertical(
            ReactiveString(id="status"),
            ReactiveString(id="cpu"),
            ReactiveString(id="mem"),
            classes="status-text",
        )
        yield Group(StatusButtons(self.container))

    def on_mount(self):
        self.set_interval(1, self.data_timer)
        self.set_interval(4, self.usage_timer)

    def watch_not_found(self, remove):
        print(f"{remove=}")
        if remove:
            print("Removing....")
            self.remove()

    def data_timer(self) -> None:
        thread = threading.Thread(target=self.update_data)
        thread.start()

    def update_data(self) -> None:
        try:
            c: Container = self.client.containers.get(self.container_id)  # type: ignore
        except errors.NotFound:
            self.not_found = True
        else:
            self.container = c
            self.query_one("#status", ReactiveString).value = c.status.capitalize()

    def usage_timer(self) -> None:
        thread = threading.Thread(target=self.update_usage)
        thread.start()

    def update_usage(self) -> None:
        print("Updating stats")
        c = self.container
        cpu = self.query_one("#cpu", ReactiveString)
        mem = self.query_one("#mem", ReactiveString)
        if c.status == "running":
            try:
                stats = c.stats(decode=None, stream=False)
            except Exception:
                return None
            else:
                cpu.value = f"CPU: {get_cpu_usage(stats):.1f}"
                mem.value = f"MEM: {get_mem_usage(stats):.1f}"
        else:
            cpu.value = ""
            mem.value = ""


class ReactiveString(Static):
    value = reactive("")

    def render(self) -> str:
        return self.value


class StatusButtons(Static):
    def __init__(self, container: Container, **kargs):
        self.container = container
        self.button = StartStopButton(container)
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Horizontal(
            self.button,
            RestartButton(self.container),
            LogsButton(self.container),
            # Button("Details"),
            classes="buttons-container",
        )


class StartStopButton(Button):
    def __init__(self, container: Container, **kargs):
        self.running = container.status == "running"
        self.container = container
        super().__init__(**kargs)

    def on_click(self) -> None:
        self.running = not self.running
        if self.running:
            self.container.start()
        else:
            self.container.stop()
        self.on_mount()

    def on_mount(self) -> None:
        self.variant = "error" if self.running else "success"
        self.text = "Stop" if self.running else "Start"

    def render(self) -> TextType:
        return self.text


class RestartButton(Button):
    def __init__(self, container: Container, **kargs):
        self.container = container
        super().__init__(**kargs)

    def on_click(self) -> None:
        self.container.restart()

    def on_mount(self) -> None:
        self.variant = "warning"

    def render(self) -> TextType:
        return "Restart"


class LogsButton(Button):
    def __init__(self, container: Container, **kargs):
        self.container = container
        super().__init__(**kargs)

    def on_click(self) -> None:
        logs: bytes = self.container.logs(tail=20)
        cl = self.app.query_one("#logs")
        lw = Static(logs.decode())
        cl.mount(lw)
        self.app.query_one(ContentSwitcher).current = "container-logs"

    def on_mount(self) -> None:
        self.variant = "primary"

    def render(self) -> TextType:
        return "Logs"
