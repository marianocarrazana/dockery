import threading
from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.reactive import reactive
from textual.containers import VerticalScroll, Grid, Vertical, Horizontal
from textual.events import Resize
from rich.text import TextType
from docker import DockerClient, errors
from docker.models.images import Image

from .custom_widgets import ResponsiveGrid, ReactiveString, CustomButton


class ImagesList(ResponsiveGrid):
    images_count = reactive(0)

    def __init__(self, docker: DockerClient, **kargs):
        self.images = []
        self.docker = docker
        super().__init__(**kargs)

    def on_mount(self) -> None:
        self.get_images()
        self.set_interval(2, self.count_timer)

    def count_timer(self) -> None:
        thread = threading.Thread(target=self.get_images)
        thread.start()

    async def watch_images_count(self, count: int) -> None:
        await self.grid.remove_children()
        for c in self.images:
            cw = ImageWidget(c, self.docker)  # type: ignore
            self.grid.mount(cw)

    def get_images(self) -> None:
        self.images = self.docker.images.list(all=False)
        self.images_count = len(self.images)


class ImageWidget(Static):
    def __init__(self, image: Image, client: DockerClient, **kargs):
        self.image = image
        self.client = client
        self.attrs = image.attrs or {}
        self.isize = self.attrs.get("Size", 0) / 1000 / 1000
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[b]" + (self.image.tags[0] or "")),
            Label(self.image.short_id.replace("sha256:", "")),
            Label(f"Size: {self.isize:.2f}MB"),
        )
