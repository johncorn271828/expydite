import os
import sys
import time
import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
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
