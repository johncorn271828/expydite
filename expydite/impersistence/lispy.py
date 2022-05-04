from copy import copy

from expydite.cons.Cons import Cons


def acons():
    raise NotImplemented()


def adjoin():
    raise NotImplemented()


def append(*x):
    raise NotImplemented()


def assoc():
    raise NotImplemented()


def assoc_if_not():
    raise NotImplemented()


def atom():
    raise NotImplemented()


def butlast():
    raise NotImplemented()


def caar():
    raise NotImplemented()


def caaar():
    raise NotImplemented()


def caadr():
    raise NotImplemented()


def cadar():
    raise NotImplemented()


def caddr():
    raise NotImplemented()


def cadr():
    raise NotImplemented()


def car(x):
    """
    """
    return getattr(x, "_car", None)


def cdaar():
    raise NotImplemented()


def cdadr():
    raise NotImplemented()


def cddar():
    raise NotImplemented()


def cdddr():
    raise NotImplemented()


def cddr():
    raise NotImplemented()


def cdr(x):
    """
    """
    return getattr(x, "_cdr", None)


def cons(a, b):
    """
    """
    result = Cons()
    result._car = a
    result._cdr = b

    return result


def conslist():
    raise NotImplemented()


def conslist_length():
    raise NotImplemented()


def copy_alist():
    raise NotImplemented()


def copy_tree():
    raise NotImplemented()


def endp():
    raise NotImplemented()


def first():
    raise NotImplemented()


def fifth():
    raise NotImplemented()


def fourth():
    raise NotImplemented()


def getf():
    raise NotImplemented()


def intersection():
    raise NotImplemented()


def last():
    raise NotImplemented()


def ldiff():
    raise NotImplemented()


def listp():
    raise NotImplemented()


def mapc():
    raise NotImplemented()


def mapcan():
    raise NotImplemented()


def mapcar():
    raise NotImplemented()


def mapcon():
    raise NotImplemented()


def mapl():
    raise NotImplemented()


def maplist():
    raise NotImplemented()


def member():
    raise NotImplemented()


def member_if():
    raise NotImplemented()


def member_if_not():
    raise NotImplemented()


def nbutlast():
    raise NotImplemented()


def nconc():
    raise NotImplemented()


def nintersection():
    raise NotImplemented()


def nset_difference():
    raise NotImplemented()


def nreconc():
    raise NotImplemented()


def nreverse(x):
    raise NotImplemented()

def nset_exclusive_or():
    raise NotImplemented()


def nsublis():
    raise NotImplemented()


def nsubst():
    raise NotImplemented()


def nsubst_if_not():
    raise NotImplemented()


def nth():
    raise NotImplemented()


def nthcdr():
    raise NotImplemented()


def nunion():
    raise NotImplemented()


def null():
    raise NotImplemented()


def pairlis():
    raise NotImplemented()


def pop():
    raise NotImplemented()


def push():
    raise NotImplemented()


def pushnew():
    raise NotImplemented()


def rassoc():
    raise NotImplemented()


def rassoc_if_not():
    raise NotImplemented()


def rest():
    raise NotImplemented()


def revappend():
    raise NotImplemented()


def reverse():
    raise NotImplemented()


def rplaca():
    raise NotImplemented()


def rplacd():
    raise NotImplemented()


def second():
    raise NotImplemented()


def set_difference():
    raise NotImplemented()


def set_exclusive_or():
    raise NotImplemented()


def sublis():
    raise NotImplemented()


def subsetp():
    raise NotImplemented()


def subst():
    raise NotImplemented()


def subst_if_not():
    raise NotImplemented()


def tailp():
    raise NotImplemented()


def third():
    raise NotImplemented()


def tree_equal():
    raise NotImplemented()


def union():
    raise NotImplemented()
