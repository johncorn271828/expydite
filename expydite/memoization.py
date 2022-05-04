"""
A memoization decorator with multiprocessing support.
"""
import pickle
from functools import wraps
from multiprocessing import Manager


serial_memo = dict()
parallel_memo = Manager().dict()


def memoized(parallel=False):
    """
    Constructs a decorator that stores func's results for later.
    Set parallel=True to share results amongst multiprocessing.Process-es.
    """
    def decorator(func):
        memo = parallel_memo if parallel else serial_memo
        fid = id(func)
        @wraps(func)
        def decorated_func(*args, **kwargs):
            key = (fid, pickle.dumps(args), pickle.dumps(kwargs))
            if key in memo:
                result = pickle.loads(memo[key])
            else:
                result = func(*args, **kwargs)
                memo[key] = pickle.dumps(result)

            return result

        return decorated_func

    return decorator
