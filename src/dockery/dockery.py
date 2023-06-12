import docker
from docker.models.containers import Container
from docker.models.volumes import Volume
from docker.models.images import Image
import click
from rich import print

from .gui import AppGUI

default_options = [
    click.option(
        "--server",
        default=None,
        help="Docker server url, for example: unix:///var/run/docker.sock",
    ),
    click.option("--ssh", is_flag=True),
    click.option("--api-version", default="1.35", help="Docker API version"),
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def get_client(server, ssh, api_version, **kargs):
    if server is None:
        client = docker.from_env()
    else:
        client = docker.DockerClient(
            base_url=server, version=api_version, use_ssh_client=ssh
        )
    return client


def run_gui(**kargs):
    client = get_client(**kargs)
    gui = AppGUI(client)
    gui.run()


@click.group(invoke_without_command=True)
@add_options(default_options)
@click.pass_context
def main(ctx, **kargs):
    if ctx.invoked_subcommand is None:
        run_gui(**kargs)


@click.command
@add_options(default_options)
def df(**kargs):
    client = get_client(**kargs)
    print(client.df())


@click.command
@add_options(default_options)
def volumes(**kargs):
    client = get_client(**kargs)
    vlms: list[Volume] = client.volumes.list()  # type: ignore
    for v in vlms:
        print(v.attrs)


@click.command
@add_options(default_options)
@click.option("--all", "-a", is_flag=True)
def ps(**kargs):
    client = get_client(**kargs)
    containers: list[Container] = client.containers.list(
        all=kargs["all"],
    )  # type: ignore
    for c in containers:
        print(c.attrs)


@click.command
@add_options(default_options)
def stats(**kargs):
    client = get_client(**kargs)
    containers: list[Container] = client.containers.list(all=True)  # type: ignore
    for c in containers:
        print(f"[b]{c.name}:")
        stats = c.stats(decode=None, stream=False)
        print(stats)


@click.command
@add_options(default_options)
def images(**kargs):
    client = get_client(**kargs)
    imgs: list[Image] = client.images.list()  # type: ignore
    for i in imgs:
        print(i.attrs)


main.add_command(df)
main.add_command(volumes)
main.add_command(ps)
main.add_command(stats)
main.add_command(images)

if __name__ == "__main__":
    main()
