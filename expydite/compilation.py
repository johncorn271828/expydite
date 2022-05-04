"""
A decorator to automate native compilation of a single function with nuitka.
"""
import os
import sys
import pathlib
import inspect
import tempfile
import subprocess
import importlib
import ast
from functools import wraps

import nuitka  # Technically an unused import, but nuitka is a dependency.
from astor import to_source


def _remove_decorators(orig_src, func, decorator_name):
    """
    Given python source, remove decorators of a given name from the declaration
    of func and return the modified source code.
    """
    # Manipulating the ast is more robust/dignified than manipulating src.
    code = ast.parse(orig_src)

    # Determine import aliases, eg "from compilation import jit as foobar".
    decorator_aliases = []
    for elem in code.body:
        if getattr(elem, "module", None) == __name__:
            for alias in elem.names:
                if alias.name == decorator_name:
                    decorator_aliases.append(alias.asname)
                    break
            break

    # Find and remove this decorator from the decorated func in the ast.
    for elem in code.body:
        if getattr(elem, "name", None) == func.__name__:
            for decorator in elem.decorator_list:
                # from compilation import jit
                if getattr(decorator, "id", None) == decorator_name:
                    elem.decorator_list.remove(decorator)
                #from compilation import jit as foobar
                elif getattr(decorator, "id", None) in decorator_aliases:
                    elem.decorator_list.remove(decorator)
                # import compilation
                # @compilation.jit
                elif (getattr(getattr(decorator, "value", None), "id", None)
                    == __name__ and
                    getattr(decorator, "attr", "") == decorator_name):
                    elem.decorator_list.remove(decorator)

            break

    return to_source(code)


def jit(func):
    """
    Apply this decorator to a function to make it natively fast.
    """
    this_decorators_name = sys._getframe().f_code.co_name
    func_file = inspect.getfile(func)
    module_name = pathlib.Path(func_file).stem
    with open(func_file, "r") as handle:
        orig_src = handle.read()

    # Need to compile func_file natively *without this decorator* to avoid
    # recursively recompiling this code forever.
    src = _remove_decorators(orig_src, func, this_decorators_name)
    with tempfile.TemporaryDirectory() as build_dir:
        py_path = os.path.join(build_dir, os.path.basename(func_file))
        with open(py_path, "w") as handle:
            handle.write(src)

        # Compile with nuitka as a module to a shared object file.
        subprocess.run(["python3", "-m", "nuitka",
                        "--static-libpython=auto",
                        "--output-dir=" + build_dir,
                        "--module", py_path],
                       check=True)
        so_path = next(os.path.join(build_dir, f)
                       for f in os.listdir(build_dir) if f.endswith(".so"))
        spec = importlib.util.spec_from_file_location(module_name, so_path)
        native_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(native_module)

    native_func = getattr(native_module, func.__name__)

    return wraps(func)(native_func)


def jit_import(module_name):
    """
    Automate import keyword with native compilation, ie "import foo" becomes:
    
    from expydite.compilation import jit_import
    jit_import("foo")
    
    """
    module_name_parts = module_name.split(".")
    py_path = None
    for import_dir in sys.path:
        potential_path = os.path.join(import_dir, *module_name_parts[:-1],
                                      module_name_parts[-1] + ".py")
        if os.path.exists(potential_path):
            py_path = potential_path
            break
    if py_path is None:
        raise ModuleNotFoundError(module_name)
    with tempfile.TemporaryDirectory() as build_dir:
        # Compile with nuitka as a module to a shared object file.
        subprocess.run(["python3", "-m", "nuitka",
                        "--static-libpython=auto",
                        "--output-dir=" + build_dir,
                        "--module", py_path],
                       check=True)
        so_path = next(os.path.join(build_dir, f)
                       for f in os.listdir(build_dir) if f.endswith(".so"))
        spec = importlib.util.spec_from_file_location(module_name, so_path)
        native_module = importlib.util.module_from_spec(spec)

    return native_module
