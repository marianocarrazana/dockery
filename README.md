# dockery

Graphical interface for Docker in your console

[![Release](https://github.com/marianocarrazana/dockery/actions/workflows/release.yml/badge.svg)](https://github.com/marianocarrazana/dockery/actions/workflows/release.yml)

![screenshot1](https://github.com/marianocarrazana/dockery/assets/17238076/2c7ead87-ede2-4834-87e6-8556740c30bd)

## Installation

### From pip

```shell
pip install -U dockery
```

### From source

```shell
git clone https://github.com/marianocarrazana/dockery.git
cd dockery
pip install -e .
# update only:
git pull
```

## Usage

Run on your console:

```shell
dockery
```

**Warning:** you will probably need to install and run dockery as a root user, or you can add permissions to your user to run docker following [this instructions](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).

## Utils

```shell
dockery df
dockery ps
dockery volumes
dockery images
dockery networks
dockery stats
# Docker swarm
dockery configs
dockery secrets
```

You specify the format output of these commands with the parameter `--format`, e.g:

```shell
dockery df --format json
dockery df --format yaml
```

### Get logs

You can use `ΞLogs` button on the containers tabs to see the logs.

Or you can use the logs command to visualize them:

```shell
dockery logs {container_name}
```

You can use the parameter `--stream` to get the logs in real time, e.g:

```shel
dockery logs {container_name} --stream
```

### **Enjoy it!**
