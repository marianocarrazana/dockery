import docker
import click
from .gui import AppGUI


@click.command()
@click.option("--port", default=0, help="port")
@click.option("--host", default=0, help="host")
def main(port, host):
    client = docker.from_env()
    gui = AppGUI(client)
    gui.run()


if __name__ == "__main__":
    main()
