from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, MarkdownViewer, Markdown, Static, Button
from textual.containers import ScrollableContainer, VerticalScroll, Container as Group
from docker import DockerClient
from docker.models.containers import Container


class AppGUI(App):
    CSS_PATH = "style.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]
    TITLE = "Satori CLI"

    def __init__(self, docker: DockerClient, **kargs):
        self.docker = docker
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield Footer()
        yield VerticalScroll(id="container-list")

    def on_mount(self) -> None:
        cl = self.query_one("#container-list")
        for c in self.docker.containers.list(all=True):
            cw = ContainerWidget(c)  # type: ignore
            cl.mount(cw)


class ContainerWidget(Static):
    def __init__(self, container: Container, **kargs):
        self.container = container
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Group(Static(self.container.name or ""), Static(self.container.short_id))
        yield Group(Static(self.container.status))
