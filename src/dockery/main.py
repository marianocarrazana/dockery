import docker
from docker import errors
from docker.models.containers import Container
from docker.models.volumes import Volume
from docker.models.images import Image
from docker.models.networks import Network
import click
from rich import print

from .gui import AppGUI
from .utils import var_dump

default_options = [
    click.option(
        "--server",
        default=None,
        help="Docker server url, for example: unix:///var/run/docker.sock",
    ),
    click.option("--ssh", is_flag=True),
    click.option("--api-version", default="1.35", help="Docker API version"),
    click.option("--format", "-f", default="yaml", help="Output format"),
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
    var_dump(client.df(), kargs["format"])


@click.command
@add_options(default_options)
def volumes(**kargs):
    client = get_client(**kargs)
    vlms: list[Volume] = client.volumes.list()  # type: ignore
    vlm_list = list(map(lambda x: x.attrs, vlms))
    var_dump(vlm_list, kargs["format"])


@click.command
@add_options(default_options)
@click.option("--all", "-a", is_flag=True)
def ps(**kargs):
    client = get_client(**kargs)
    containers: list[Container] = client.containers.list(
        all=kargs["all"]
    )  # type: ignore
    con_list = list(map(lambda x: x.attrs, containers))
    var_dump(con_list, kargs["format"])


@click.command
@add_options(default_options)
def stats(**kargs):
    client = get_client(**kargs)
    containers: list[Container] = client.containers.list(all=True)  # type: ignore
    stats = list(map(lambda x: x.stats(stream=False), containers))
    var_dump(stats, kargs["format"])


@click.command
@add_options(default_options)
def images(**kargs):
    client = get_client(**kargs)
    imgs: list[Image] = client.images.list()  # type: ignore
    img_list = list(map(lambda x: x.attrs, imgs))
    var_dump(img_list, kargs["format"])


@click.command
@add_options(default_options)
def networks(**kargs):
    client = get_client(**kargs)
    netw: list[Network] = client.networks.list()  # type: ignore
    net_list = list(map(lambda x: x.attrs, netw))
    var_dump(net_list, kargs["format"])


@click.command
@add_options(default_options)
@click.argument("container")
@click.option("--stream", is_flag=True)
def logs(**kargs):
    client = get_client(**kargs)
    try:
        container: Container = client.containers.get(kargs["container"])  # type: ignore
    except errors.NotFound:
        print(f"Container [b]{kargs['container']}[/] not found")
    else:
        if kargs["stream"]:
            for log in container.logs(stream=True):
                print(log.decode("utf-8", errors="ignore"), end="")
        else:
            logs: bytes = container.logs()
            print(logs.decode("utf-8", errors="ignore"))


main.add_command(df)
main.add_command(volumes)
main.add_command(ps)
main.add_command(stats)
main.add_command(images)
main.add_command(networks)
main.add_command(logs)

if __name__ == "__main__":
    main()
