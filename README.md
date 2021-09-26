<p align="center">
  <img alt="esguard-logo" src="esguard.png" height="100" />
  <h2 align="center">esguard</h2>
  <p align="center">esguard provides a Python decorator that waits for processing while monitoring the load of Elasticsearch.</p>
</p>

[![PyPi version](https://img.shields.io/pypi/v/esguard.svg)](https://pypi.python.org/pypi/esguard/) [![](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-390/) ![PyTest](https://github.com/po3rin/esguard/workflows/PyTest/badge.svg)

## Quick Start

You need to launch elasticsearch before quick start.

```python
from esguard import ESGuard


@ESGuard(os_cpu_percent=95).decorator
def mock_func(x):
    return x

self.assertEqual(mock_func(1), 1)
```

## Supports

- [x] os cpu usage
- [x] os mem usaged percent
- [x] jvm mem heap used percent
- [x] os load average 1m
- [ ] os load average 5m
- [ ] os load average 15m


## Test

You need to launch elasticsearch before testing.

```sh
$ docker compose up -d --build
$ poetry run pytest
```
