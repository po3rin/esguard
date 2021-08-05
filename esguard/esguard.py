from functools import wraps
import time
import random
from typing import Callable, TypeVar, Any
from elasticsearch import Elasticsearch
from logging import Logger


T = TypeVar("T")


class Error(Exception):
    pass


class MaxRetriesExceededError(Error):
    pass


class ESGuard:
    def __init__(
        self,
        es: Elasticsearch = Elasticsearch(),
        os_cpu_percent: int = 90,
        os_mem_used_percent: int = 90,
        jvm_mem_heap_used_percent: int = 90,
        logger: Logger = None,
    ) -> None:
        self.logger = logger
        self.es = es
        self.os_cpu_percent = os_cpu_percent
        self.os_mem_used_percent = os_mem_used_percent
        self.jvm_mem_heap_used_percent = jvm_mem_heap_used_percent

    def _warning(self, message: str) -> None:
        if self.logger is None:
            return
        self.logger.warning(message)

    def _wait(self) -> bool:
        wait = False
        res = self.es.nodes.stats(metric=["os", "jvm"])
        for k in res["nodes"].keys():
            cpu = res["nodes"][k]["os"]["cpu"]["percent"]
            if cpu >= self.os_cpu_percent and self.os_cpu_percent > 0:
                self._warning(
                    f"node({k}) OS CPU usage {cpu}% over {self.os_cpu_percent}% "
                )
                wait = True
                break

            mem = res["nodes"][k]["os"]["mem"]["used_percent"]
            if mem >= self.os_mem_used_percent and self.os_mem_used_percent > 0:
                self._warning(
                    f"node({k}) OS MEM usage {mem}% over {self.os_mem_used_percent}% "
                )
                wait = True
                break

            jvm_heap = res["nodes"][k]["jvm"]["mem"]["heap_used_percent"]
            if (
                jvm_heap >= self.jvm_mem_heap_used_percent
                and self.jvm_mem_heap_used_percent > 0
            ):
                self._warning(
                    f"node({k}) JVM heap usage {jvm_heap}% over {self.jvm_mem_heap_used_percent}% "
                )
                wait = True
                break

        return wait

    def decotator(self) -> Callable[[], T]:
        def _retry(func) -> Callable[[], T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                x = 0
                backoff_in_seconds = 1
                retries = 3

                while self._wait():
                    if x == retries:
                        raise MaxRetriesExceededError(f"max retries exceeded {retries}")
                    sleep = backoff_in_seconds * 2 ** x + random.uniform(0, 1)
                    time.sleep(sleep)
                    x += 1

                return func(*args, **kwargs)

            return wrapper

        return _retry
