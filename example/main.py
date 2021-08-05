from esguard import EsGuard 


@ESGuard(os_cpu_percent=90, os_mem_used_percent=-1, jvm_mem_heap_used_percent=-1).decotator()
def f(x: int) -> int:
    return x

if __name__ == '__main__':
    f()
