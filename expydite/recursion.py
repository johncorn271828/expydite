"""
Tail recursion optimization for CPython.
"""
import sys
from functools import wraps
import inspect
import ast


class UnexceptionalTailRecursionCallStackPop(BaseException):
    """
    A fake exception used to pop the call stack when tail recursing.
    """
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs


def tail_recurse(*args, **kwargs):
    """
    Pop the call stack and pass the popped args/kwargs along with the exception.
    """
    raise UnexceptionalTailRecursionCallStackPop(args, kwargs)


def _refers_to(expression, func):
    """
    Recursively search expression (a code object) for ast.Call to func.
    """
    # Found invocation of func.
    if (isinstance(expression, ast.Call) and
        expression.func.id == func.__name__):
        result = True
    # Primitive data type is leaf node, no func here.
    elif not hasattr(expression, "__dict__"):   # Leaf of code object
        result = False
    # Recursively search subexpressions.
    else:
        result =  any(_refers_to(getattr(expression, attr), func)
                      for attr in vars(expression))

    return result


def _verify_return(code, func):
    """
    Determine whether a return statement fits some rules meant to ensure that
    func is properly tail recursive.
    """
    # Expressions not containing func
    if not _refers_to(code, func):
        result = True
    # Expressions that are themselves func invocations whose arguments do not
    # depend on func.
    elif (isinstance(code, ast.Call) and
          code.func.id == func.__name__ and
          not _refers_to(code.args, func)):
        result = True
    # Infix if-else expressions whose branches are one of the above
    elif isinstance(code, ast.IfExp):
        result = (not _refers_to(code.test, func) and
                  _verify_return(code.body, func) and
                  _verify_return(code.orelse, func))
    else:
        result = False

    return result


def _tco_verify(code, func):
    """
    Recursively search code object to ensure all return statements are tail
    recursive with respect to func.
    """
    # Found a return statement. Verify the returned expression
    if isinstance(code, ast.Return):
        result = _verify_return(code.value, func)
    # Found a list of something, verify its contents
    elif isinstance(code, list):
        result = all(_tco_verify(statement, func)
                     for statement in code)
    # Primitive data type is a leaf in this tree, nothing more to check here
    elif not hasattr(code, "__dict__"):
        result = True
    # Recurse on attributes of code
    else:
        result = all(_tco_verify(getattr(code, attr), func)
                     for attr in vars(code))

    return result


def is_tail_recursive(func):
    """
    Determine whether func can use tail call optimization. Might be too strict.
    """
    code = ast.parse(inspect.getsource(func))
    #print(ast.dump(code))

    return _tco_verify(code, func)


def tail_call_optimized(verify=True):
    """
    @tail_call_optimized() decorator tricks CPython into tail call optimization.
    verify=True checks at compile time that func can be optimized this way.
    There may be other properly tail recursive funcs that fail this test; in
    that case set verify=False.
    """
    def tail_call_optimized_decorator(func):
        # Verify that func is properly tail recursive.
        if verify and not is_tail_recursive(func):
            raise Exception("{} appears not to be tail recursive"
                            .format(func.__name__))
        @wraps(func)
        def decorated_func(*args, **kwargs):
            # If recursion is happening, func will call decorated_func
            if getattr(getattr(sys._getframe().f_back, "f_code", None),
                       "co_name", None) == func.__name__:
                tail_recurse(*args, **kwargs)
            else:
                while True:
                    try:
                        return func(*args, **kwargs)
                    except UnexceptionalTailRecursionCallStackPop as exception:
                        args = exception.args
                        kwargs = exception.kwargs

        return decorated_func

    return tail_call_optimized_decorator


def tco(func): return tail_call_optimized(verify=False)(func)


def Y(func):
    """
    This Y-combinator implements tail call optimized recursion.
    Does NOT attempt to verify that this makes sense for your lambda.
    """
    def func_wrapper(*args, **kwargs):
        while True:
            try:
                return func(tail_recurse)(*args, **kwargs)
            except UnexceptionalTailRecursionCallStackPop as exception:
                args = exception.args
                kwargs = exception.kwargs

    return func_wrapper
