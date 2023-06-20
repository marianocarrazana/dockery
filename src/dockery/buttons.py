from textual.app import ComposeResult
from textual.widgets import Static
from textual.reactive import reactive
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
            self.styles.outline = (self.variant, new_color)

    def on_mount(self) -> None:
        self.text = self.start_text
        self.color = self.start_color
