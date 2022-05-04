import os
import sys
import time
import datetime
import math
from functools import reduce
from operator import add
from random import randint
from multiprocessing import Value
from multiprocessing.managers import SharedMemoryManager

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from parallelism import (
    CPU_COUNT,
    pmap, pfilter, preduce,
    psum,
    pany, pall,
    pmax, pmin,
    _pmap_builtin,
    _pmap_inplace
)


def baselpi(N):
    N = float(N)
    baselsum = 0.0
    n = 1.0
    while n <= N:
        baselsum += 1.0 / (n * n)
        n += 1.0

    return math.sqrt(6.0 * baselsum)
    

def test_pmap_correct_and_faster():
    inputs = [10000000] * 10
    test_func = baselpi

    start = datetime.datetime.now()
    serial_result = list(map(test_func, inputs))
    serial_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    parallel_result = pmap(test_func, inputs)
    parallel_time = datetime.datetime.now() - start

    assert serial_result == parallel_result
    assert serial_time > 1.2 * parallel_time


def test__pmap_inplace_correct_and_faster():

    smm = SharedMemoryManager()
    smm.start()
    
    inputs = [10000000] * 20
    inputs = smm.ShareableList(inputs)
    test_func = baselpi

    start = datetime.datetime.now()
    serial_result = list(map(test_func, inputs))
    serial_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    #parallel_result = _pmap_inplace(test_func, parallel_inputs)
    parallel_result = pmap(test_func, inputs, inplace=True)
    parallel_time = datetime.datetime.now() - start

    # Correct
    assert all(parallel_result[i] == serial_result[i]
               for i in range(len(serial_result)))

    # Inplace flag works
    assert inputs == parallel_result

    # Faster
    assert serial_time > 1.2 * parallel_time

    smm.shutdown()


def test_pmap_void_return_correct():
    inputs = list(range(2))

    def func(x):
        with open("tests/scratch" + str(x) + ".txt", "w") as file:
            pass

    start = datetime.datetime.now()
    parallel_result = pmap(func, inputs, void_return=True)
    parallel_time = datetime.datetime.now() - start
    
    # Void return
    assert parallel_result is None

    # func was carried out
    assert all(os.path.exists("tests/scratch" + str(x) + ".txt")
               for x in inputs)

    for x in inputs:
        os.remove("tests/scratch" + str(x) + ".txt")


def test_pmap_auto_void_return_works():
    inputs = list(range(2))

    def func(x : int) -> None:
        with open("tests/scratch" + str(x) + ".txt", "w") as file:
            pass

    start = datetime.datetime.now()
    parallel_result = pmap(func, inputs)
    parallel_time = datetime.datetime.now() - start
    
    # Void return
    assert parallel_result is None

    # func was carried out
    assert all(os.path.exists("tests/scratch" + str(x) + ".txt")
               for x in inputs)

    for x in inputs:
        os.remove("tests/scratch" + str(x) + ".txt")


def slow_even(n):
    time.sleep(1)
    return n % 2 == 0


def test_pfilter_correct_and_faster():
    test_array = [randint(0,10) for i in range(10)]

    start = datetime.datetime.now()
    serial_result = list(filter(slow_even, test_array))
    serial_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    parallel_result = pfilter(slow_even, test_array)
    parallel_time = datetime.datetime.now() - start

    assert serial_result == parallel_result
    assert serial_time > 1.5 * parallel_time


def test_preduce_correct_and_faster():
    test_array = [1] * 10

    def slow_sum(a, b):
        time.sleep(1)
        return a + b
    
    start = datetime.datetime.now()
    serial_sum = reduce(slow_sum, test_array)
    serial_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    parallel_sum = preduce(slow_sum, test_array)
    parallel_time = datetime.datetime.now() - start

    # Correct, faster
    assert serial_sum == parallel_sum
    assert serial_time > 1.5 * parallel_time


class SlowBoolean():   # Does pany make sense without something like this?
    def __init__(self, value):
        self.value = value

    def __bool__(self):
        time.sleep(1)
        return bool(self.value)

def test_pany_correct_and_faster():
    # Huge arrays of bools still don't benefit from pany
    #test_array = [False] * 100000000 + [True] + [False] * 100

    # pany makes sense when something delays evaluating truthiness
    test_array = ([SlowBoolean(False)] * 15 +
                  [SlowBoolean(True)] +
                  [SlowBoolean(False)] * 4)

    start = datetime.datetime.now()
    serial_result = any(test_array)
    serial_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    parallel_result = pany(test_array)
    parallel_time = datetime.datetime.now() - start
    
    assert serial_result == parallel_result
    assert serial_time > 1.5 * parallel_time


def test_pall_correct_and_faster():
    # pall makes sense when something delays evaluating truthiness
    test_array = ([SlowBoolean(True)] * 15 +
                  [SlowBoolean(False)] +
                  [SlowBoolean(True)] * 4)

    start = datetime.datetime.now()
    serial_result = all(test_array)
    serial_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    parallel_result = pall(test_array)
    parallel_time = datetime.datetime.now() - start
    
    assert serial_result == parallel_result
    assert serial_time > 1.5 * parallel_time


class SlowInteger():
    def __init__(self, value):
        self.value = value

    def __gt__(self, other):
        time.sleep(1)
        return self.value > other.value

    def __lt__(self, other):
        time.sleep(1)
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __add__(self, other):
        time.sleep(1)
        return SlowInteger(self.value + other.value)


def test_psum_correct_and_faster():
    test_array = [SlowInteger(n) for n in range(20)]

    start = datetime.datetime.now()
    serial_result = sum(test_array, SlowInteger(0))
    serial_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    parallel_result = psum(test_array)
    parallel_time = datetime.datetime.now() - start
    
    assert serial_result == parallel_result
    assert serial_time > 1.5 * parallel_time


def test_pmax_correct_and_faster():
    test_array = [SlowInteger(n) for n in range(20)]

    start = datetime.datetime.now()
    serial_result = max(test_array)
    serial_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    parallel_result = pmax(test_array)
    parallel_time = datetime.datetime.now() - start
    
    assert serial_result == parallel_result
    assert serial_time > 1.5 * parallel_time

    
def test_pmap_pfilter_correct_on_sets():
    test_set = set(range(20))

    def square(x):
        return x * x

    pmap_result = pmap(square, test_set)
    map_result = set(map(square, test_set))
    assert map_result == pmap_result

    def even(n):
        return n % 2 == 0

    pfilter_result = pfilter(even, test_set)
    filter_result = set(filter(even, test_set))
    assert pfilter_result == filter_result


def test_pmap_uses_multiple_argments():
    
    it = list(range(10))

    assert pmap(add, it, it) == list(map(add, it, it))

