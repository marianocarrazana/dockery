from textual import work
from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.reactive import reactive
from docker import DockerClient, errors
from docker.models.containers import Container
from textual.containers import (
    Horizontal,
    Vertical,
    Container as Group,
)

from .utils import get_cpu_usage, get_mem_usage
from .logs import LogsButton
from .custom_widgets import CustomButton, ResponsiveGrid, ReactiveString
from .models import store


class ContainersList(ResponsiveGrid):
    container_count = reactive(0)

    def __init__(self, docker: DockerClient, **kargs):
        self.containers: list[Container] = []
        self.docker = docker
        super().__init__(**kargs)

    def on_mount(self) -> None:
        self.get_containers()
        self.set_interval(2, self.count_timer)

    def count_timer(self) -> None:
        self.get_containers()

    async def watch_container_count(self, count: int) -> None:
        await self.grid.remove_children()
        images_in_use = []
        for c in self.containers:
            cw = ContainerWidget(c, self.docker, classes="li")
            self.grid.mount(cw)
            images_in_use.append(c.image.id)  # type: ignore
        store.containers_images = images_in_use

    @work(exclusive=True)
    def get_containers(self) -> None:
        self.containers = self.docker.containers.list(all=True)  # type: ignore
        self.container_count = len(self.containers)


class ContainerWidget(Static):
    def __init__(self, container: Container, client: DockerClient, **kargs):
        self.container = container
        self.client = client
        self.container_id = container.id
        self.running = False
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield Group(
            Label("[b]" + (self.container.name or ""), classes="container-name"),
            Vertical(
                ReactiveString(classes="status"),
                Horizontal(
                    ReactiveString(classes="cpu"), ReactiveString(classes="mem")
                ),
                classes="stats-text",
            ),
            classes="container-info",
        )

        yield Group(StatusButtons(self.container))

    def on_mount(self):
        self.status_widget = self.query_one(".status", ReactiveString)
        self.cpu_widget = self.query_one(".cpu", ReactiveString)
        self.mem_widget = self.query_one(".mem", ReactiveString)
        self.set_interval(1, self.data_timer)
        self.mounted = True
        self.update_usage()

    def data_timer(self) -> None:
        self.update_data()

    @work(exclusive=True)
    def update_data(self) -> None:
        try:
            self.container.reload()
        except errors.NotFound:
            return None
        else:
            status = self.container.status.capitalize()
            self.running = status == "Running"
            self.status_widget.text = (
                "[green]" if self.running else "[bright_black]"
            ) + status
            self.classes = "li running" if self.running else "li"

    @work
    def update_usage(self) -> None:
        for stat in self.container.stats(stream=True, decode=True):
            if not self.mounted:  # finish the thread
                return None
            if self.running:
                mem_mb, mem_percent = get_mem_usage(stat)
                cpu_text = f"CPU: {get_cpu_usage(stat):.1f}%"
                mem_text = f"MEM: {mem_mb:.1f}MB({mem_percent:.1f}%)"
            else:
                cpu_text = "CPU: -"
                mem_text = "MEM: -"
            self.cpu_widget.text = cpu_text
            self.mem_widget.text = mem_text

    def on_unmount(self):
        self.mounted = False


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
        self.button = self.query_one(CustomButton)
        self.running = self.container.status == "running"

    def watch_running(self, running: bool):
        self.variant = "error" if running else "success"
        text = ":black_square_button:Stop" if running else ":arrow_forward: Start"
        self.button.text = text
        self.button.color = "red" if running else "green"

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
