        # Expydite
#### A Python library for performant functional programming.

Expydite began as a bundle of utility functions for functional programming,
and grew into a more complete framework for developing performant code using
persistent or shared memory data structures.
It has decorators for native compilation, lazy evaluation, tail recursion
optimization, and memoization to accelerate existing code without modification.
Includes fast implementations of parallel functional control flow functions
(map, filter, reduce).
Its "persistence" data structures module includes persistent shared memory cons
sequences and an implementation of the Okasaki-Germane-Might algorithm for
immutable Red-Black trees, allowing Clojure-like semantics with logarithmic
guarantees on persistent collections in shared memory.

A quick demo:
#### Native just-in-time compilation:
```Python
from compilation import jit 


def baselpi(N):
    N = float(N)
    baselsum = 0.0
    n = 1.0
    while n < N:
        baselsum += 1.0 / n / n
        n += 1.0

    return math.sqrt(6.0 * baselsum)


def test_jit():
    baselpi_native = jit(baselpi)

    N = 1000000
    start = datetime.datetime.now()
    pi = baselpi(N)
    pi_elapsed = datetime.datetime.now() - start

    start = datetime.datetime.now()
    pi_native = baselpi_native(N)
    pi_native_elapsed = datetime.datetime.now() - start

    assert pi == pi_native  # results same
    assert pi_elapsed > 2 * pi_native_elapsed   # twice as fast

```

#### Lazy evaluation:
```Python
from laziness import thunk


SLOW_FUNC_WAIT = 5

@thunk
def cheap(x):
    return 2 * x


@thunk
def expensive(x):
    time.sleep(SLOW_FUNC_WAIT)
    return x * x


def client_func(x, y):
    return cheap(3 * x), expensive(4 * y)


def test_thunk():
    # Thunk-ify functions called within client code to postpone or cancel evaluation.
    start = datetime.datetime.now()
    cheap_thunk, discard_thunk = client_func(1, 2)
    result = cheap_thunk()
    finish = datetime.datetime.now()

    # Result correct, faster than without laziness.
    assert result == 6
    assert finish - start < datetime.timedelta(seconds=SLOW_FUNC_WAIT)

```

#### Memoization:
```Python
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

```

#### Tail call recursion optimization:
```Python
from operator import mul
from recursion import tail_call_optimized, Y


N = 1000
FACTORIAL_LAMBDA = lambda f: lambda n, acc: acc if n == 0 else f(n - 1, n * acc)


def factorial(n, acc=1):
    return acc if n == 0 else factorial(n - 1, acc=acc * n)


@tail_call_optimized()
def tail_call_optimized_factorial(n, acc=1):
    return acc if n == 0 else tail_call_optimized_factorial(n - 1, acc=acc * n)


def test_tail_call_optimized():

    # Regular thing blows call stack
    try:
        print(factorial(N))
        assert False
    except RecursionError:
        pass

    # Optimized does not blow call stack, gets right answer
    assert tail_call_optimized_factorial(N) == reduce(mul, range(1, N + 1))

```

#### Parallel functional control flow
```Python
from parallelism import pmap

def test_pmap():
    inputs = [10000000] * 10
    test_func = baselpi

    start = datetime.datetime.now()
    serial_result = list(map(test_func, inputs))
    serial_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    parallel_result = pmap(test_func, inputs)
    parallel_time = datetime.datetime.now() - start

    assert serial_result == parallel_result  # Correct
    assert serial_time > 1.2 * parallel_time  # Faster

```

#### Immutable collections with logarithmic guarantees a la clojure:
```Python
from persistence.RBDict import RBDict

def test_basics():
    old = {1:2, 3:4, 5:6}
    d = RBDict(old)
    assert d[1] == 2
    for k in d:
        assert d[k] == old[k]
    assert len(d) == 3
    del d[1]
    assert d == RBDict({3:4, 5:6})
    assert 3 in d.keys()
    assert 4 in d.values()
```

#### Shared memory variants:
```Python
def test_SharedConsCell():
    # Can instantiate and manipulate SM object
    a = SharedConsCell(2, 3)
    a.cons(1)
    assert a.car() == 1
    b = a.cdr()
    assert b.car() == 2
    a.rplaca(0)
    a.rplacd(1)
    assert a.car() == 0
    assert a.cdr() == 1

    a = SharedConsCell(0, 1)
    
    # Other processes can see it
    results = Queue()
    def assert_is_a(somecons, results):
        try:
            assert somecons.car() == 0
            assert somecons.cdr() == 1
            results.put(True)
        except Exception as e:
            results.put(False)

    processes = []
    for i in range(5):
        process = Process(target=assert_is_a, args=(a,results))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    while not results.empty():
        assert results.get()

    # Other process can assign it
    def change_it(somecons):
        somecons.rplaca(999)

    process = Process(target=change_it, args=(a,))
    process.start()
    process.join()
    assert a.car() == 999


```
