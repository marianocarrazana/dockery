# dockery

Graphical interface for Docker in your console

<table>
  <tr>
    <td><img src="https://github.com/marianocarrazana/dockery/assets/17238076/3c987e47-2d86-44ae-a078-73eced62dc11"/></td>
    <td><img src="https://github.com/marianocarrazana/dockery/assets/17238076/26dc43c9-1dd0-4097-ac02-aa006c3ff6b6"/></td>
  </tr>
  <tr>
    <td colspan="2"><img src="https://github.com/marianocarrazana/dockery/assets/17238076/c991ff4b-eebf-4495-b67c-2c57e933bd7d" /></td>
  </tr>
</table>

## Installation

### From source

```shell
git clone git@github.com:marianocarrazana/dockery.git
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

## Extra commands

```shell
dockery df
dockery ps
dockery volumes
dockery images
dockery networks
dockery stats
```

## **Enjoy it!**
