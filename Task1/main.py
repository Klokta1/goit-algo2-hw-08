import random
import time
from typing import Callable

from lru_cache import LRUCache


def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n // 2), random.randint(n // 2, n - 1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:  # ~3% Update queries
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:  # ~97% Range queries
            if random.random() < p_hot:  # 95% of ranges are "hot"
                left, right = random.choice(hot)
            else:  # 5% are random
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


def range_sum_no_cache(array: list[int], left: int, right: int) -> int:
    return sum(array[left:right + 1])


def update_no_cache(array: list[int], index: int, value: int) -> None:
    if 0 <= index < len(array):
        array[index] = value


cache: LRUCache


def range_sum_with_cache(array: list[int], left: int, right: int) -> int:
    global cache
    key = (left, right)
    cached_value = cache.get(key)
    if cached_value != -1:
        return cached_value

    result = range_sum_no_cache(array, left, right)
    cache.put(key, result)
    return result


def update_with_cache(array: list[int], index: int, value: int) -> None:
    global cache
    if 0 <= index < len(array):
        array[index] = value
        keys_to_invalidate = [key for key in cache.cache if key[0] <= index <= key[1]]

        for key in keys_to_invalidate:
            if key in cache.cache:
                node_to_remove = cache.cache.pop(key)
                cache.list.remove(node_to_remove)


def run_benchmark(array: list, query_list: list, sum_func: Callable, update_func: Callable) -> float:
    start_time = time.perf_counter()
    for query in query_list:
        op_type, arg1, arg2 = query
        if op_type == 'Range':
            sum_func(array, arg1, arg2)
        elif op_type == 'Update':
            update_func(array, arg1, arg2)
    return time.perf_counter() - start_time


if __name__ == '__main__':
    N = 100_000
    Q = 50_000
    CACHE_CAPACITY = 1000

    queries = make_queries(N, Q)
    base_array = [random.randint(1, 100) for _ in range(N)]

    time_no_cache = run_benchmark(base_array[:], queries, range_sum_no_cache, update_no_cache)

    cache = LRUCache(CACHE_CAPACITY)
    time_with_cache = run_benchmark(base_array[:], queries, range_sum_with_cache, update_with_cache)

    print(f"Без кешу :  {time_no_cache:.2f} c")
    speedup = time_no_cache / time_with_cache
    print(f"LRU-кеш  :   {time_with_cache:.2f} c  (прискорення ×{speedup:.1f})")

# Run output:
# Без кешу :  20.63 c
# LRU-кеш  :   7.78 c  (прискорення ×2.7)
#
# Process finished with exit code 0
