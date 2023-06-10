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
from docker import DockerClient
from docker.models.containers import Container


class AppGUI(App):
    CSS_PATH = "style.css"
    BINDINGS = [
        ("h", "home", "Home"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]
    TITLE = "DOCKERY"

    def __init__(self, docker: DockerClient, **kargs):
        self.docker = docker
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with ContentSwitcher(initial="container-list"):
            yield VerticalScroll(id="container-list")
            with VerticalScroll(id="container-logs"):
                yield Static("", id="logs")

    def on_mount(self) -> None:
        cl = self.query_one("#container-list")
        for c in self.docker.containers.list(all=True):
            cw = ContainerWidget(c)  # type: ignore
            cl.mount(cw)

    def action_home(self) -> None:
        self.query_one(ContentSwitcher).current = "container-list"


class ContainerWidget(Static):
    def __init__(self, container: Container, **kargs):
        self.container = container
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Group(
            Static(self.container.name or ""),
            Static(self.container.short_id),
            classes="container-info",
        )
        yield Vertical(Static(self.container.status), classes="status-text")
        yield Group(StatusButtons(self.container))


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
