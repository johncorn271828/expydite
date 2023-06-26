from multiprocessing import Process, Queue
from expydite.persistence.ConsCell import ConsCell


def test_ConsCell():
    a = ConsCell(2, 3)
    print(a)
    a.cons(1)
    assert a.car() == 1
    b = a.cdr()
    print(b)
    assert b.car() == 2
    a.rplaca(0)
    a.rplacd(1)
    assert a.car() == 0
    assert a.cdr() == 1

    
def test__eq__():
    a = ConsCell(2, 3)
    b = ConsCell(2, 3)
    c = ConsCell()
    d = ConsCell(2, 4)
    e = ConsCell(2, ConsCell(3, 4))
    f = ConsCell(2, ConsCell(3, 4))
    g = ConsCell(2, ConsCell(3, 5))
    assert id(a) != id(b)
    assert a == b
    assert a != c
    assert a != d
    assert a != e
    assert e == f
    a = ConsCell(ConsCell(1, 2), 3)
    b = ConsCell(ConsCell(1, 2), 3)
    c = ConsCell(ConsCell(1, 2), 4)
    d = ConsCell(ConsCell(1, 99), 3)
    assert a == b
    assert a != c
    assert a != d

    # Long lists equality doesn't blow stack
    a = None
    b = None
    for i in range(10000):
        a = ConsCell(1, a)
        b = ConsCell(1, b)
    assert a == b

    
# test_ConsCell()
# test__eq__()
