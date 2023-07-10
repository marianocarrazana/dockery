# dockery

Graphical interface for Docker in your console

[![Release](https://github.com/marianocarrazana/dockery/actions/workflows/release.yml/badge.svg)](https://github.com/marianocarrazana/dockery/actions/workflows/release.yml)

<table>
  <tr>
    <td><img src="https://github.com/marianocarrazana/dockery/assets/17238076/bcff22c9-898c-4877-adac-ddf2e58007c4"/></td>
    <td><img src="https://github.com/marianocarrazana/dockery/assets/17238076/0da0c13c-d84d-4e8a-8b6f-a0d779c2d98d"/></td>
  </tr>
  <tr>
    <td colspan="2"><img src="https://github.com/marianocarrazana/dockery/assets/17238076/c991ff4b-eebf-4495-b67c-2c57e933bd7d" /></td>
  </tr>
</table>

## Installation

### From source

```shell
git clone https://github.com/marianocarrazana/dockery.git
cd dockery
pip install -e .
# update only:
git pull
```

### From pip

```shell
pip install -U dockery
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
```

You specify the format output of these commands with the parameter `--format`, e.g:

```shell
dockery df --format json
dockery df --format yaml
```

### Get logs

```shel
dockery logs {container_name}
```

You can use the parameter `--stream` to get the logs in real time, e.g:

```shel
dockery logs {container_name} --stream
```

### **Enjoy it!**
