from dataclasses import dataclass


@dataclass
class Store:
    containers_images: list


store = Store(containers_images=[])
