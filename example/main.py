from esguard import ESGuard


@ESGuard(os_cpu_percent=0, os_mem_used_percent=0, jvm_mem_heap_used_percent=0).decotator()
def f(x: int) -> int:
    return x

if __name__ == '__main__':
    print(f(2))
