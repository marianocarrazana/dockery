import threading
from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.reactive import reactive
from textual.containers import  Vertical, Horizontal
from docker import DockerClient
from docker.models.networks import Network

from .custom_widgets import ResponsiveGrid


class NetworkList(ResponsiveGrid):
    networks_count = reactive(0)

    def __init__(self, docker: DockerClient, **kargs):
        self.networks = []
        self.docker = docker
        super().__init__(**kargs)

    def on_mount(self) -> None:
        self.get_networks()
        self.set_interval(2, self.count_timer)

    def count_timer(self) -> None:
        thread = threading.Thread(target=self.get_networks)
        thread.start()

    async def watch_networks_count(self, count: int) -> None:
        await self.grid.remove_children()
        for c in self.networks:
            cw = NetworkWidget(c, self.docker)  # type: ignore
            self.grid.mount(cw)

    def get_networks(self) -> None:
        self.networks = self.docker.networks.list()
        self.networks_count = len(self.networks)


class NetworkWidget(Static):
    def __init__(self, network: Network, client: DockerClient, **kargs):
        self.network = network
        self.client = client
        self.attrs = network.attrs or {}
        self.isize = self.attrs.get("Size", 0) / 1000 / 1000
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[b]" + (self.network.name or "")),
            Label(self.network.short_id),
            Horizontal(
                Label("Scope: " + self.attrs.get("Scope", "-")),
                Label(" Driver: " + self.attrs.get("Driver", "-")),
            ),
        )
