from textual import work
from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.reactive import reactive
from textual.containers import Vertical
from docker import DockerClient
from docker.models.images import Image

from .custom_widgets import ResponsiveGrid
from .models import store


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
        self.get_images()

    async def watch_images_count(self, count: int) -> None:
        await self.grid.remove_children()
        for c in self.images:
            cw = ImageWidget(c, self.docker, classes="li")  # type: ignore
            self.grid.mount(cw)

    @work(exclusive=True)
    def get_images(self) -> None:
        self.images = self.docker.images.list(all=False)
        self.images_count = len(self.images)


class ImageWidget(Static):
    def __init__(self, image: Image, client: DockerClient, **kargs):
        self.image = image
        self.client = client
        self.attrs = image.attrs or {}
        self.isize = self.attrs.get("Size", 0) / 1000000
        self.short_id = self.image.short_id.replace("sha256:", "")
        if self.image.tags:
            self.tag = self.image.tags[0]
        elif self.image.id:
            self.tag = self.image.id.replace("sha256:", "")
        else:
            self.tag = ""
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("[b]" + self.tag),
            Label(self.short_id),
            Label(f"Size: {self.isize:.2f}MB"),
        )

    def on_mount(self):
        self.set_interval(2, self.count_timer)

    def count_timer(self):
        self.update_usage()

    @work(exclusive=True)
    def update_usage(self):
        print(self.image.id)
        print(store.containers_images)
        self.classes = (
            "li running" if self.image.id in store.containers_images else "li"
        )
