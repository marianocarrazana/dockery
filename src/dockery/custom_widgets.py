import math
from textual.app import ComposeResult
from textual.widgets import Static
from textual.reactive import reactive
from textual.containers import VerticalScroll, Grid
from textual.events import Resize
from rich.text import TextType


class CustomButton(Static):
    text = reactive("")
    color = reactive("")

    def __init__(self, text: str, variant="round", color: str = "green", **kargs):
        self.variant = variant
        self.start_text = text
        self.start_color = color
        super().__init__(shrink=True, expand=True, **kargs)

    def render(self) -> TextType:
        return self.text

    def watch_color(self, new_color: str):
        if new_color != "":
            self.styles.outline = (self.variant, new_color) # type: ignore

    def on_mount(self) -> None:
        self.text = self.start_text
        self.color = self.start_color


class ResponsiveGrid(VerticalScroll):
    container_count = reactive(0)

    def __init__(self, **kargs):
        self.grid = Grid()
        super().__init__(**kargs)

    def compose(self) -> ComposeResult:
        yield self.grid

    def on_mount(self) -> None:
        self.resize()
        self.grid.styles.grid_columns = "1fr"
        self.grid.styles.grid_rows = "4"
        self.grid.styles.width = "100%"
        self.grid.styles.height = "auto"

    def on_resize(self, e: Resize):
        self.resize()

    def resize(self):
        min_container_width = 75
        columns = math.floor(self.size.width / min_container_width)
        self.grid.styles.grid_size_columns = columns


class ReactiveString(Static):
    text = reactive("")

    def __init__(self, **kargs):
        super().__init__(shrink=True, expand=True, **kargs)

    def render(self) -> TextType:
        return self.text
