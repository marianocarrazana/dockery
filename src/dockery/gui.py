from textual.app import App, ComposeResult
from textual.widgets import Footer, ContentSwitcher, Tabs, Tab
from textual.widgets._header import HeaderClock
from textual.containers import (
    VerticalScroll,
    Horizontal,
)
from docker import DockerClient

from .containers import ContainersList
from .images import ImagesList
from .networks import NetworkList
from .volumes import VolumesList


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
                Tab("Images", id="image-list"),
                Tab("Networks", id="network-list"),
                Tab("Volumes", id="volume-list"),
                Tab("Logs", id="container-logs"),
                id="nav",
            )
        yield Footer()
        with ContentSwitcher():
            yield ContainersList(self.docker, id="container-list")
            yield VerticalScroll(id="container-logs")
            yield ImagesList(self.docker, id="image-list")
            yield NetworkList(self.docker, id="network-list")
            yield VolumesList(self.docker, id="volume-list")

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        self.query_one(ContentSwitcher).current = event.tab.id
