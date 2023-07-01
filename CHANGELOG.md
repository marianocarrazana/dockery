# Change Log

## :zap: New Features

- New `logs` command, use it like this:

    `dockery logs {container}`, add the parameter
    `--stream` to get the logs in real time.

- New `--format` parameter to specify the output format of almost all commands output, for now it supports `json` and `yaml` only.

## :lady_beetle: Fixes

- Avoid exceptions on logs decode
