import datetime
from functools import reduce
from copy import copy, deepcopy

from expydite.persistence.ConsCell import ConsCell
from expydite.persistence.ConsList import ConsList


def test_ConsList():
    ConsList([])
    ConsList(range(0))
    ConsList(range(10))

    # ConsCell ctor
    a = ConsCell(1, None)
    b = ConsList(a)
    assert b._head.car() == 1
    assert b._head.cdr() is None


def test___str__():
    iterable = range(3)
    a = ConsList(iterable)
    assert a.__str__() == "(0 1 2)"
    assert str(a) == "(0 1 2)"
    


def test___eq__():
    iterable = range(3)
    a = ConsList(iterable)
    b = ConsList(iterable)
    c = ConsList(range(4))
    d = ConsList([])
    e = ConsList(range(1,3))

    assert id(a) != id(b)
    assert a.__eq__(b)
    assert id(a) != id(c)
    assert not a.__eq__(c)
    assert not a.__eq__(d)
    assert not a.__eq__(e)
    assert a == b
    assert a != c
    assert a != d
    assert a != e


def test___bool__():
    empty = ConsList()
    assert not empty.__bool__()
    assert not bool(empty)
    assert not empty
    nonempty = ConsList([0])
    print(nonempty)
    print(nonempty._head)
    print(nonempty._head.car())
    print(nonempty._head.cdr())
    assert nonempty.__bool__()
    assert bool(nonempty)
    assert nonempty


def test___copy_____deepcopy__():
    x = ConsList([])
    y = ConsList()
    assert x == y
    assert copy(x) == copy(y)

    # Internal updates affect shallow copy
    a = ConsCell(1, None)
    b = ConsList([a, 5, 6])
    thecopy = copy(b)  # Still has a pointer to a
    assert thecopy == b
    a.rplaca(99)
    assert thecopy._head.car().car() == 99

    # Internal updates don't affect deep copy
    a = ConsCell(1, None)
    b = ConsList([a, 5, 6])
    thedeepcopy = deepcopy(b)
    assert thedeepcopy == b
    a.rplaca(99)
    print(thedeepcopy)
    assert thedeepcopy._head.car().car() == 1


def test___reversed__():
    a = ConsList([1, 2, 3])
    a = a.__reversed__()
    assert a == ConsList([3,2,1])
    b = reversed(a)
    assert b == ConsList([1,2,3])
    assert a == ConsList([3,2,1])

    
def test___getitem__():
    
    # slice is int returns value
    a = ConsList(range(10))
    assert a[1] == 1
    
    # slice is whole thing returns reference
    a = ConsList(range(10))
    assert id(a[0:]._head) == id(a._head)
    assert id(a[:]._head) == id(a._head)
    
    # slice on tail returns reference
    a = ConsList(range(10))
    b = a[1:]
    a._head.cdr().rplaca("hello")
    assert b._head.car() == "hello"

    # slice with an end makes a copy
    a = ConsList(range(10))
    b = a[:1]
    a._head.rplaca("hello")
    assert b == ConsList([0])
    
    # slice with steps makes a copy
    a = ConsList(range(10))
    b = a[0:6:2]
    a._head.rplaca("hello")
    assert b == ConsList([0, 2, 4])

    # Negative indices in slice?
    a = ConsList(range(10))
    assert a[-1] == 9
    assert a[-3:-1] == ConsList([7, 8])
    assert a[7:-1] == ConsList([7, 8])

    # Negative steps give reversed results
    assert a[7:0:-2] == ConsList([7, 5, 3, 1])
    assert a[7:1:-2] == ConsList([7, 5, 3])


def test___len__():
    a = ConsList(range(3))
    assert a.__len__() == 3
    assert len(a) == 3

    assert len(ConsList()) == 0


def test___contains__():
    a = ConsList(range(3))
    assert a.__contains__(1)
    assert 1 in a


def test__iter_____next__():
    a = ConsList(range(3))
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

    
def test_index():
    assert ConsList(range(5)).index(2) == 2


def test_count():
    a = ConsList([1, 2, 2, 2, 3, 4, 5, 5, 6, 6, 2, 6, 6])
    assert a.count(2) == 4
    assert a.count(9) == 0


def test___add__():
    a = ConsList([1,2,3])
    b = ConsList([4,5,6])
    c = a + b
    assert c == ConsList([1,2,3,4,5,6])
    assert len(c) == 6
    assert a == ConsList([1,2,3])
    assert b == ConsList([4,5,6])


def test___setitem__():
    a = ConsList(range(10))
    b = ConsList(initializer=a._head, length=a._length)
    a.__setitem__(0, 1)
    assert a._head.car() == 1
    # b should be unmodified, ie the setitem made a new head and left b alone
    # Like Osaki's update function 
    assert b._head.car() == 0
    a[0] = 2
    assert a._head.car() == 2
    a[1] = 3
    assert a._head.cdr().car() == 3

    # contiguous slice no stop => whole new list
    a = ConsList(["a", "b", "c", "d", "e", "f"])
    b = ConsList(range(5))
    c = ConsList(a._head, length=a._length)
    a[1:] = b
    c[0] = 99  # Doesn't change a, its head points to new thing
    assert a == ConsList(["a", 0, 1, 2, 3, 4])

    # contiguous slice with stop => recycled tail
    a = ConsList(range(5))
    b = ConsList(["a", "b"])
    c = a
    a[0:2] = b
    c._head.cdr().cdr().rplaca(99)  # Shares tail with a, changes affect a
    assert a == ConsList(["a", "b", 99, 3, 4])

    # slice with step > 1 intersperses values
    a = ConsList(range(10))
    b = ConsList(["a", "b"])
    a[2:6:2] = b
    assert a == ConsList([0, 1, "a", 3, "b", 5, 6, 7, 8, 9])

    # slice with step < 0 splices reversed values
    a = ConsList(range(10))
    b = ConsList(["a", "b"])
    a[4:2:-1] = b
    print(a)
    assert a == ConsList([0, 1, 2, "b", "a", 5, 6, 7, 8, 9])

    # Too long value throws error
    try:
        a = ConsList(range(10))
        b = ConsList(["a", "b", "c", "d"])
        a[2:4] = b
        assert False
    except ValueError:
        pass



def test___delitem__():

    # Delete at integer index
    a = ConsList(range(10))
    b = ConsList()
    b._head = a._head
    a.__delitem__(0)
    assert a == ConsList(range(1,10))
    del a[1]
    assert a == ConsList([1,3,4,5,6,7,8,9])
    assert len(a) == len([1,3,4,5,6,7,8,9])
    # a and b still have tail in common
    b._head.cdr().cdr().cdr().cdr().rplaca(99)
    assert a == ConsList([1,3,99,5,6,7,8,9])

    # Delete at negative index
    a = ConsList(range(10))
    del a[-1]
    assert a == ConsList(range(9))

    # Delete tail
    a = ConsList(range(10))
    del a[0:]
    assert a == ConsList([])
    a = ConsList(range(10))
    del a[3:]
    assert a == ConsList([0,1,2])

    # Delete slice
    a = ConsList(range(10))
    del a[2:7:2]
    assert a == ConsList([0,1,3,5,7,8,9])
    

def test_insert():
    a = ConsList(range(4))
    b = ConsList()
    b._head = a._head
    a.insert(2, 10)
    assert a == ConsList([0, 1, 10, 2, 3])
    assert 10 not in b   # b left in place
    b._head.cdr().cdr().rplaca(99)
    assert a == ConsList([0, 1, 10, 99, 3])


def test_append():
    a = ConsList(range(4))
    a.append(10)
    assert a == ConsList([10, 0, 1, 2, 3])
    assert len(a) == 5

def test_reverse():
    a = ConsList(range(4))
    a.reverse()
    assert a == ConsList([3,2,1,0])

    
def test_extend():
    a = ConsList(range(4))
    b = ConsList(["a", "b", "c"])
    # extend by a cons assigns pointer
    a.extend(b)
    assert a == ConsList([0, 1, 2, 3, "a", "b", "c"])
    b._head.rplaca("d")
    assert a == ConsList([0, 1, 2, 3, "d", "b", "c"])  # affected by b change


def test_pop():
    a = ConsList(range(4))
    assert a.pop() == 0
    assert a == ConsList([1, 2, 3])
    assert a.pop(1) == 2
    assert a == ConsList([1, 3])
    a = ConsList()
    try:
        a.pop()
        assert False
    except IndexError:
        pass
    a = ConsList([99])
    assert a.pop() == 99
    assert a == ConsList()
    

def test_remove():
    a = ConsList(range(5))
    a.remove(0)
    assert a == ConsList([1,2,3,4])
    a.remove(2)
    assert a == ConsList([1,3,4])
    try:
        a.remove(5)
        assert False
    except ValueError:
        pass


def test___iadd__():
    a = ConsList([0])
    a += ConsList([1])
    a.__iadd__(ConsList([2]))
    assert a == ConsList([0, 1, 2])


