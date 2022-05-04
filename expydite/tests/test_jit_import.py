import os
import datetime

from expydite.compilation import jit_import


def test_jit_import():
    import expydite.tests.foomodule as foomodule
    native_module = jit_import("foomodule")
    N = 10000000
    start = datetime.datetime.now()
    cpython_result = foomodule.baselpi(N)
    cpython_time = datetime.datetime.now() - start
    start = datetime.datetime.now()
    native_result = native_module.baselpi(N)
    native_time = datetime.datetime.now() - start

    assert cpython_result == native_result
    assert cpython_time > 2 * native_time
