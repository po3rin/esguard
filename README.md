# esguard

esguard provides a Python decorator that waits for processing while monitoring the load of Elasticsearch.

## Quick Start

```python
@ESGuard(os_cpu_percent=90, os_mem_used_percent=-1, jvm_mem_heap_used_percent=-1).decotator()
def mock_func(x):
    return x
        
self.assertEqual(mock_func(1), 1)
```

## Test

You need to launch elasticsearch before testing.

```sh
$ docker-compose up -d --build
$ poetry run pytest
```

