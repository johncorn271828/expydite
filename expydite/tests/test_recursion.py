import os
import sys
import datetime
from functools import reduce
from operator import mul

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
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


def test_tail_call_verification():
    # This shouldn't work 
    try: 
        @tail_call_optimized(verify=True)
        def factorial3(n):
            if n == 0:
                return 1
            else:
                return n * factorial3(n - 1)
        assert False
    except:
        pass

    # Broken thing allowed with verify flag off
    @tail_call_optimized(verify=False)
    def factorial3(n):
        if n == 0:
            return 1
        else:
            return n * factorial3(n - 1)


def test_Y_tco():
    combinator_factorial = Y(FACTORIAL_LAMBDA)
    start = datetime.datetime.now()
    combinator_N_factorial = combinator_factorial(N, 1)
    combinator_factorial_elapsed = datetime.datetime.now() - start
    start = datetime.datetime.now()
    N_factorial = tail_call_optimized_factorial(N)
    factorial_elapsed = datetime.datetime.now() - start

    assert combinator_N_factorial == N_factorial
