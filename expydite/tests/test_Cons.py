import datetime
from functools import reduce
from copy import copy, deepcopy

from expydite.impersistence import Cons


def test_Cons():
    Cons([])
    Cons(range(0))
    Cons(range(10))


def test___str__():
    iterable = range(3)
    a = Cons(iterable)
    assert a.__str__() == "(0 1 2)"
    assert str(a) == "(0 1 2)"


def test___eq__():
    iterable = range(3)
    a = Cons(iterable)
    b = Cons(iterable)
    c = Cons(range(4))
    d = Cons([])
    e = Cons(range(1,3))
    
    assert id(a) != id(b)
    assert a.__eq__(b)
    assert a == b
    assert a != c
    assert a != d
    assert a != e


def test___bool__():
    empty = Cons()
    assert not empty.__bool__()
    assert not bool(empty)
    assert not empty
    nonempty = Cons([0])
    assert nonempty.__bool__()
    assert bool(nonempty)
    assert nonempty


def test___contains__():
    a = Cons(range(3))
    assert a.__contains__(1)
    assert 1 in a


def test__iter_____next__():
    a = Cons(range(3))
    it = a.__iter__()
    assert it.__next__() == 0
    assert next(it) == 1
    assert next(it) == 2
    try:
        next(it)
        assert False
    except StopIteration:
        pass

    # Reinstantiating needs to work, thus need for separate iterator class.
    it = iter(a)
    assert it.__next__() == 0
    assert next(it) == 1
    assert next(it) == 2
    try:
        next(it)
        assert False
    except StopIteration:
        pass

    
def test_reverse___reversed__():
    a = Cons([1, 2, 3])
    a.reverse()
    assert a == Cons([3,2,1])
    b = Cons(reversed(a))
    assert b == Cons([1,2,3])
    assert a == Cons([3,2,1])

    
def test___copy_____deepcopy__():
    assert copy(Cons([])) == copy(Cons(()))
    a = Cons([1, 2, 3, 4])
    b = Cons([5, 6, a])
    thecopy = copy(b)  # Still has a pointer to a
    thedeepcopy = deepcopy(b)
    a._car = a._cdr._car
    a._cdr = a._cdr._cdr
    assert thecopy == Cons([5, 6, Cons([2, 3, 4])])  # affected by a changes
    assert thedeepcopy == Cons([5, 6, Cons([1, 2, 3, 4])])  # not affected


def test___len__():
    a = Cons(range(3))
    assert a.__len__() == 3
    assert len(a) == 3

    assert len(Cons()) == 0


def test_index():
    assert Cons(range(5)).index(2) == 2


def test_count():
    a = Cons([1, 2, 2, 2, 3, 4, 5, 5, 6, 6, 2, 6, 6])
    assert a.count(2) == 4
    assert a.count(9) == 0


def test___getitem__():
    a = Cons(range(10))
    # slice is int returns value
    assert a[1] == 1
    # slice is whole thing returns reference
    assert id(a[0:]) == id(a)
    assert id(a[:]) == id(a)
    # slice on tail returns reference
    b = a[1:]
    a._cdr._car = "hello"
    assert b._car == "hello"
    # slice with an end makes a copy
    a = Cons(range(10))
    b = a[:1]
    a._car = "hello"
    assert b == Cons([0])
    # slice with steps makes a copy
    a = Cons(range(10))
    b = a[0:6:2]
    a._car = "hello"
    assert b == Cons([0, 2, 4])

    # Negative indices in slice?
    a = Cons(range(10))
    assert a[-1] == 9
    assert a[-3:-1] == Cons([7, 8])
    assert a[7:-1] == Cons([7, 8])

    # Negative steps give reversed results
    assert a[7:0:-2] == Cons([7, 5, 3, 1])
    assert a[7:1:-2] == Cons([7, 5, 3])


def test___setitem__():
    a = Cons(range(10))
    a.__setitem__(0, 1)
    assert a._car == 1
    a[0] = 2
    assert a._car == 2
    a[1] = 3
    assert a._cdr._car == 3

    # contiguous slice no stop assigned to Cons
    a = Cons(range(10))
    b = Cons(["a", "b", "c"])
    a[1:] = b
    assert a == Cons([0, "a", "b", "c"])
    b[0] = "d"
    assert a == Cons([0, "d", "b", "c"])

    # contiguous slice with stop assigned to Cons
    a = Cons(range(10))
    b = Cons(["a", "b", "c"])
    a[1:8] = b
    assert a == Cons([0, "a", "b", "c", 8, 9])
    b[0] = "d"
    assert a == Cons([0, "d", "b", "c", 8, 9])

    # slice with another data type
    a = Cons(range(10))
    b = ["a", "b", "c"]
    a[1:8] = b
    assert a == Cons([0, "a", "b", "c", 8, 9])

    # slice with step > 1
    a = Cons(range(10))
    b = ["a", "b", "c"]
    a[2:7:2] = b
    assert a == Cons([0, 1, 'a', 3, 'b', 5, 'c', 7, 8, 9])

    # negative indices
    a = Cons(range(5))
    a[-1] = 10
    assert a == Cons([0, 1, 2, 3, 10])
    a[1:-2] = [9]
    assert a == Cons([0, 9, 3, 10])

    # negative step
    a = Cons(range(10))
    a[7:0:-2] = ["a", "b", "c", "d"]
    assert a == Cons([0, 'd', 2, 'c', 4, 'b', 6, 'a', 8, 9])

    # Badly sized range
    a = Cons(range(10))
    try:
        a[7:1:-2] = ["a", "b", "c", "d"]
        assert False
    except ValueError:
        pass


def test___delitem__():

    # Delete at integer index
    a = Cons(range(10))
    a.__delitem__(0)
    assert a == Cons(range(1,10))
    del a[1]
    assert a == Cons([1,3,4,5,6,7,8,9])

    # Delete at negative index
    a = Cons(range(10))
    del a[-1]
    assert a == Cons(range(9))

    # Delete tail
    a = Cons(range(10))
    del a[0:]
    assert a == Cons([])
    a = Cons(range(10))
    del a[3:]
    assert a == Cons([0,1,2])

    # Delete slice
    a = Cons(range(10))
    del a[2:7:2]
    assert a == Cons([0,1,3,5,7,8,9])
    

def test_insert():
    a = Cons(range(4))
    a.insert(2, 10)
    assert a == Cons([0, 1, 10, 2, 3])


def test_append():
    a = Cons(range(4))
    a.append(10)
    assert a == Cons([10, 0, 1, 2, 3])

    
def test_extend():
    a = Cons(range(4))
    b = Cons(["a", "b", "c"])
    # extend by a cons assigns pointer
    a.extend(b)
    assert a == Cons([0, 1, 2, 3, "a", "b", "c"])
    b[0] = "d"
    assert a == Cons([0, 1, 2, 3, "d", "b", "c"])  # affected by b change

    # Extend by an iterable conses stuff
    a = Cons(range(4))
    b = ["a", "b", "c"]
    # extend by a cons assigns pointer
    a.extend(b)
    assert a == Cons([0, 1, 2, 3, "a", "b", "c"])
    b[0] = "d"
    assert a == Cons([0, 1, 2, 3, "a", "b", "c"])  # unaffected


def test_pop():
    a = Cons(range(4))
    a.pop()
    assert a == Cons([1, 2, 3])
    a.pop(1)
    assert a == Cons([1, 3])
    a = Cons()
    try:
        a.pop()
        assert False
    except IndexError:
        pass
    

def test_remove():
    a = Cons(range(5))
    a.remove(0)
    assert a == Cons([1,2,3,4])
    a.remove(2)
    assert a == Cons([1,3,4])
    try:
        a.remove(5)
        assert False
    except ValueError:
        pass


def test___iadd__():
    a = Cons([0])
    a += Cons([1])
    a.__iadd__([2])
    assert a == Cons([0, 1, 2])


def test_add():
    a = Cons(range(4))
    a.add(1)
    assert a == Cons(range(4))
    a.add(4)
    assert a == Cons([4,0,1,2,3])


def test_discard():
    a = Cons([0,0,0,1, 1, 1, 0, 1, 1, 0, 0])
    a.discard(0)
    assert a == Cons([1,1,1,1,1])


def test_mixins():
    # These should be automatically implemented by extending MutableSet
    # See https://docs.python.org/3/library/collections.abc.html
    assert all(
        mixin in dir(Cons()) for mixin in [
            "__le__",
            "__lt__",
            "__ne__",
            "__ge__",
            "__gt__",
            "__and__",
            "__iand__",
            "__or__", 
            "__ior__",
            "__sub__",
            "__isub__",
            "isdisjoint",
            "clear"])

def test___le_____lt__():
    a = Cons(range(3))
    b = Cons(range(4))
    assert a.__le__(a)
    assert a.__le__(b)
    assert a <= b
    assert not a.__lt__(a)
    assert a.__lt__(b)
    assert a < b


def test___ne__():
    a = Cons(range(3))
    b = Cons(range(4))
    c = Cons(range(3))
    assert a.__ne__(b)
    assert a != b
    assert not a.__ne__(a)
    assert not a != c


def test___ge____gt__():
    a = Cons(range(3))
    b = Cons(range(4))
    assert b.__ge__(a)
    assert b >= a
    assert b >= b
    assert b > a
    assert not b > b



def test___and_____iand__():
    a = Cons(range(3))
    b = Cons(range(4))
    c = a & b
    assert c == a
    b &= a
    assert b == a


def test___or_____ior__():
    a = Cons(range(3))
    b = Cons(range(4))
    c = a | b
    # As sets, c == b now
    assert all(elem in b for elem in c)
    assert all(elem in c for elem in b)
    a |= b
    # As sets a == b now
    assert all(elem in b for elem in a)
    assert all(elem in a for elem in b)
    
    
def test___sub_____isub__():
    a = Cons(range(3))
    b = Cons(range(4))
    assert b - a == Cons([3])
    b -= a
    assert b == Cons([3])


def test___xor_____ixor__():
    a = Cons(range(3))
    b = Cons(range(1,4))
    c = a ^ b
    # Set equality
    assert all(elem in c for elem in Cons([0,3]))
    assert all(elem in Cons([0,3]) for elem in c)
    a ^= b
    # Set equality
    assert all(elem in a for elem in Cons([0,3]))
    assert all(elem in Cons([0,3]) for elem in a)


def test_isdisjoint():
    a = Cons(range(3))
    b = Cons(range(1,5))
    c = Cons(range(4, 10))

    assert not a.isdisjoint(b)
    assert a.isdisjoint(c)
    assert not b.isdisjoint(c)
    

def test_clear():
    a = Cons(range(1,2,3))
    a.clear()
    assert a == Cons()


def square(x):
    return x * x


def even(n):
    return n % 2 == 0


def mysum(a, b):
    return a + b


def test_map_filter_reduce():
    a = Cons([1, 2, 3])
    assert Cons(map(square, a)) == Cons([1, 4, 9])
    assert Cons(filter(even, a)) == Cons([2])
    assert reduce(mysum, a) == 6


