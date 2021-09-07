from functools import wraps
from logging import Logger
from typing import Callable, TypeVar, Any, cast

from elasticsearch import Elasticsearch
from tenacity import Retrying, wait_exponential, wait_random, stop_after_attempt, RetryError

F = TypeVar('F', bound=Callable[..., Any])


class Error(Exception):
    pass


class MaxRetriesExceededError(Error):
    pass


class ResourceUsageError(Error):
    pass


class ESGuard:
    def __init__(
        self,
        es: Elasticsearch = Elasticsearch(),
        os_cpu_percent: int = 90,
        os_mem_used_percent: int = 90,
        jvm_mem_heap_used_percent: int = 90,
        retry_backoff_sec: int = 1,
        max_retries: int = 3,
        logger: Logger = None,
    ) -> None:
        self.logger = logger
        self.es = es
        self.os_cpu_percent = os_cpu_percent
        self.os_mem_used_percent = os_mem_used_percent
        self.jvm_mem_heap_used_percent = jvm_mem_heap_used_percent
        self.retry_backoff_sec = retry_backoff_sec
        self.max_retries = max_retries

    def _warning(self, message: str) -> None:
        if self.logger is None:
            return
        self.logger.warning(message)

    def _wait(self) -> None:
        res = self.es.nodes.stats(metric=["os", "jvm"])
        for k in res["nodes"].keys():
            cpu = res["nodes"][k]["os"]["cpu"]["percent"]
            if cpu >= self.os_cpu_percent and self.os_cpu_percent > 0:
                self._warning(
                    f"node({k}) OS CPU usage {cpu}% over {self.os_cpu_percent}% "
                )
                raise ResourceUsageError(
                    f"node({k}) OS CPU usage {cpu}% over {self.os_cpu_percent}% "
                )

            mem = res["nodes"][k]["os"]["mem"]["used_percent"]
            if mem >= self.os_mem_used_percent and self.os_mem_used_percent > 0:
                self._warning(
                    f"node({k}) OS MEM usage {mem}% over {self.os_mem_used_percent}% "
                )
                raise ResourceUsageError(
                    f"node({k}) OS MEM usage {mem}% over {self.os_mem_used_percent}% "
                )

            jvm_heap = res["nodes"][k]["jvm"]["mem"]["heap_used_percent"]
            if (jvm_heap >= self.jvm_mem_heap_used_percent
                    and self.jvm_mem_heap_used_percent > 0):
                self._warning(
                    f"node({k}) JVM heap usage {jvm_heap}% over {self.jvm_mem_heap_used_percent}% "
                )
                raise ResourceUsageError(
                    f"node({k}) JVM heap usage {jvm_heap}% over {self.jvm_mem_heap_used_percent}% "
                )

    def _get_retryer(self) -> Callable:
        return Retrying(wait=wait_exponential(min=self.retry_backoff_sec) +
                        wait_random(min=0, max=1),
                        stop=stop_after_attempt(self.max_retries))

    def decorator(self, func: F) -> F:
        retryer = self._get_retryer()

        def wrapper(*args: Any, **kwds: Any) -> Any:
            try:
                retryer(self._wait)
            except RetryError:
                raise MaxRetriesExceededError(
                    f"max retries exceeded {self.max_retries}")
            return func(*args, **kwds)

        return cast(F, wrapper)
