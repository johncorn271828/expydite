import os
import sys
import math
import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from compilation import jit

@jit
def baselpi2(N):
    N = float(N)
    baselsum = 0.0
    n = 1.0
    while n < N:
        baselsum += 1.0 / n / n
        n += 1.0

    return math.sqrt(6.0 * baselsum)


