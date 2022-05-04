import os
import sys
import math
import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from compilation3_helper import baselpi3


def baselpi(N):
    N = float(N)
    baselsum = 0.0
    n = 1.0
    while n < N:
        baselsum += 1.0 / n / n
        n += 1.0

    return math.sqrt(6.0 * baselsum)


def test_jit_works_with_vanilla_import():

    N = 1000000
    start = datetime.datetime.now()
    pi = baselpi(N)
    pi_elapsed = datetime.datetime.now() - start

    start = datetime.datetime.now()
    pi_native = baselpi3(N)
    pi_native_elapsed = datetime.datetime.now() - start

    assert pi == pi_native  # results same
    assert pi_elapsed > 2 * pi_native_elapsed   # twice as fast



