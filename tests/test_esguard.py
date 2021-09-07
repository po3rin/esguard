import unittest
from esguard.esguard import ESGuard, MaxRetriesExceededError
from esguard import __version__


def test_version():
    assert __version__ == '0.1.8'


class TestEsGuard(unittest.TestCase):
    def test_no_threshold(self):
        @ESGuard(os_cpu_percent=-1, os_mem_used_percent=-1, jvm_mem_heap_used_percent=-1).decorator
        def mock_func(x):
            return x

        self.assertEqual(mock_func(1), 1)

    def test_cpu_threshold(self):
        @ESGuard(os_cpu_percent=90, os_mem_used_percent=-1, jvm_mem_heap_used_percent=-1).decorator
        def mock_func(x):
            return x

        self.assertEqual(mock_func(1), 1)

    def test_max_retries(self):
        @ESGuard(os_cpu_percent=-1, os_mem_used_percent=-1, jvm_mem_heap_used_percent=1).decorator
        def mock_func(x):
            return x

        with self.assertRaises(MaxRetriesExceededError, msg='max retries exceeded 3'):
            self.assertEqual(mock_func(1), 1)
