import os
import sys
import time
import datetime
from multiprocessing import Process

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from memoization import memoized


N = 35


def fibonacci(n):
    if n == 0 or n == 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


@memoized()
def memoized_fibonacci(n):
    if n == 0 or n == 1:
        return n
    else:
        return memoized_fibonacci(n - 1) + memoized_fibonacci(n - 2)


def test_memoized():
    start = datetime.datetime.now()
    fib_N = fibonacci(N)
    fibonacci_elapsed = datetime.datetime.now() - start

    start = datetime.datetime.now()
    fib_memoized_N = memoized_fibonacci(N)
    fibonacci_memoized_elapsed = datetime.datetime.now() - start

    # Result correct
    assert fib_N == fib_memoized_N

    # Faster
    assert fibonacci_elapsed > 1000 * fibonacci_memoized_elapsed


@memoized(parallel=True)
def slowsquare(x):
    print(f"Squaring {x}")
    time.sleep(1)
    return x * x


def test_pmemoized():
    p1 = Process(target=slowsquare, args=(2,))
    p1.start()
    p1.join()

    p2 = Process(target=slowsquare, args=(2,))
    start = datetime.datetime.now()
    p2.start()
    p2.join()
    elapsed = datetime.datetime.now() - start

    # 2nd process recovered first's memo (implied by the speed)
    assert elapsed < datetime.timedelta(seconds=1)
