from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.reactive import reactive
from textual.containers import Vertical, Horizontal
from docker import DockerClient
from docker.models.volumes import Volume

from .custom_widgets import ResponsiveGrid
from .utils import daemon


class VolumesList(ResponsiveGrid):
    volumes_count = reactive(0)

    def __init__(self, docker: DockerClient, **kargs):
        self.volumes: list[Volume] = []
        self.docker = docker
        super().__init__(**kargs)

    def on_mount(self) -> None:
        self.get_volumes()
        self.set_interval(2, self.get_volumes)

    async def watch_volumes_count(self, count: int) -> None:
        await self.grid.remove_children()
        for c in self.volumes:
            cw = VolumeWidget(c, self.docker, classes="li")
            self.grid.mount(cw)

    @daemon
    def get_volumes(self) -> None:
        self.volumes = self.docker.volumes.list()  # type: ignore
        self.volumes_count = len(self.volumes)


class VolumeWidget(Static):
    def __init__(self, volume: Volume, client: DockerClient, **kargs):
        self.volume = volume
        self.client = client
        self.attrs = volume.attrs or {}
        self.isize = self.attrs.get("Size", 0) / 1000 / 1000
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[b]" + self.volume.name),
            Label(self.attrs.get("Mountpoint", "")),
            Horizontal(
                Label("Scope: " + self.attrs.get("Scope", "-")),
                Label(" Driver: " + self.attrs.get("Driver", "-")),
            ),
        )
