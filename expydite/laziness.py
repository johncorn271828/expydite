"""
Lazy evaluation decorator.
"""
from functools import wraps


class LazyEvaluator():
    """
    Delays evaluation of a function call.
    """
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    # Empty parenthesis invoke the function via this magic method, ie: thunk()
    def __call__(self):
        return self.func(*self.args, **self.kwargs)


def thunk(func):
    "Converts decorated function's output into thunks"
    @wraps(func)
    def decorated_func(*args, **kwargs):
        return LazyEvaluator(func, *args, **kwargs)

    return decorated_func
