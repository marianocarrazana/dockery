import docker
import click
from .gui import AppGUI


@click.command()
@click.option(
    "--server",
    default=None,
    help="Docker server url, for example: unix:///var/run/docker.sock",
)
@click.option("--ssh", is_flag=True)
@click.option("--api-version", default="1.35", help="Docker API version")
def main(server, ssh, api_version):
    print(server, ssh, api_version)
    if server is None:
        client = docker.from_env()
    else:
        client = docker.DockerClient(
            base_url=server, version=api_version, use_ssh_client=ssh
        )
    gui = AppGUI(client)
    gui.run()


if __name__ == "__main__":
    main()
