# import inspect
# import importlib
# import pathlib
# import ast
# import astor
# import tempfile
# from types import ModuleType
from multiprocessing.managers import BaseManager
from multiprocessing import Manager

managers = dict()


class MyManager(BaseManager):
    pass


def get_manager(cls):
    """
    Get a shared memory manager object for class, initializing if needed.
    """
    global managers
    if cls.__name__ not in managers:
        exposed = ([attr for attr in dir(cls) if not attr.startswith("_")] +
                   ["__eq__", "__str__", "__deepcopy__", "__bool__"])
        manager = MyManager()
        manager.register(cls.__name__, cls, exposed=exposed)
        manager.__enter__()
        managers[cls.__name__] = manager
    manager = managers[cls.__name__]

    return manager


def shared(cls):
    """
    Makes cls's instances live in shared memory by replacing __new__ with
    make_shared.
    References to __new__ in cls's declaration will still point to the original
    constructor, so they need to be manually replaced by make_shared calls.
    """
    manager = get_manager(cls)
    cls.__new__ = make_shared

    return cls


def make_shared(cls, *args, **kwargs):
    return get_manager(cls).__getattribute__(cls.__name__).__call__(
        *args, **kwargs)


# def shared_fancy_prototype(cls):
#     """
#     Decorate a class declaration with this to make instances available across
#     processes.
#     Works by replacing the instance created by __new__ with a dynamically
#     registered proxy object that leaves public methods available.
#     """
#     # Even though the constructor will instantiate the manager, it needs to
#     # happen *here* first (ie import time) to prevent infinite recursion.
#     manager = get_manager(cls)

#     # Prepare an ast of the class for manipulation
#     cls_src = inspect.getsource(cls)
#     cls_code = ast.parse(cls_src)

#     # Replace calls to ctor in cls code with calls to make_shared
#     patched_cls_code = _replace_ctor_calls(cls_code, cls)

#     # Remove this decorator from the class
#     patched_cls_code = _remove_shared_decorator(patched_cls_code, cls)

#     # Generate patched class source code
#     patched_cls_src = astor.to_source(patched_cls_code)

#     # Get original complete source file
#     src_path = inspect.getfile(cls)
#     with open(src_path, "r") as handle:
#         src = handle.read()
#     module_name = pathlib.Path(src_path).stem

#     # Replace original declaration with modified src, reparse
#     almost_patched_src = src.replace(cls_src, patched_cls_src)
#     code = ast.parse(almost_patched_src)

#     # Ensure that make_shared is imported
#     code.body = [
#         ast.ImportFrom(module=__name__,
#                        names=[ast.alias(name='make_shared')],
#                        level=0)
#     ] + code.body

#     # Back to source
#     patched_src = astor.to_source(code)
#     print(patched_src)

#     # Compile the patched source
#     compiled = compile(patched_src, "", "exec")
#     module = ModuleType("huh", cls.__module__)
#     exec(compiled, module.__dict__)
#     module.hello()

#     # Extract patched class
#     patched_cls = getattr(module, cls.__name__)
#     print(cls)
#     print(patched_cls)
#     print(dir(patched_cls))
    
#     # Replace constructor with a proxy maker
#     patched_cls.__new__ = make_shared

#     return patched_cls


# def _remove_shared_decorator(code, cls):
#     if (isinstance(code, ast.ClassDef) and
#         code.name == cls.__name__ and
#         getattr(code, "decorator_list", [])):
#         code.decorator_list = [
#             dec for dec in code.decorator_list
#             if dec.id != shared.__name__]
#     elif isinstance(code, list):
#         for i in range(len(code)):
#             code[i] = _remove_shared_decorator(code[i], cls)
#         # Primitive data type is leaf node, no ctor call here.
#     elif not hasattr(code, "__dict__"): # Leaf node
#         pass
#     else:
#         for attr in vars(code):
#             setattr(code, attr,
#                     _remove_shared_decorator(
#                         getattr(code, attr), cls))

#     return code


# def _replace_ctor_calls(code, cls):
#     # Call to named function that is this ctor
#     if (isinstance(code, ast.Call) and
#         getattr(code.func, "id", None) == cls.__name__):
#         code.func.id = "make_shared"
#         code.args = [
#             ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()),
#                       attr='__class__',
#                       ctx=ast.Load())
#         ] + code.args

#     # Keep searching recursively.
#     elif isinstance(code, list):
#         for i in range(len(code)):
#             code[i] = _replace_ctor_calls(code[i], cls)
#     # Primitive data type is leaf node, no ctor call here.
#     elif not hasattr(code, "__dict__"): # Leaf node
#         pass
#     else:
#         for attr in vars(code):
#             setattr(code, attr,
#                     _replace_ctor_calls(getattr(code, attr), cls))

#     return code


