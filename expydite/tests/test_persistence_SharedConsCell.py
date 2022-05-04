import datetime

from multiprocessing import Process, Queue
from expydite.persistence.ConsCell import ConsCell, SharedConsCell


def test_SharedConsCell():
    # Can instantiate and manipulate SM object
    a = SharedConsCell(2, 3)
    a.cons(1)
    assert a.car() == 1
    b = a.cdr()
    assert b.car() == 2
    a.rplaca(0)
    a.rplacd(1)
    assert a.car() == 0
    assert a.cdr() == 1

    a = SharedConsCell(0, 1)
    
    # Other processes can see it
    results = Queue()
    def assert_is_a(somecons, results):
        try:
            assert somecons.car() == 0
            assert somecons.cdr() == 1
            results.put(True)
        except Exception as e:
            results.put(False)

    processes = []
    for i in range(5):
        process = Process(target=assert_is_a, args=(a,results))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    while not results.empty():
        assert results.get()

    # Other process can assign it
    def change_it(somecons):
        somecons.rplaca(999)

    process = Process(target=change_it, args=(a,))
    process.start()
    process.join()
    assert a.car() == 999

def test_shared__eq__():
    a = SharedConsCell(2, 3)
    b = SharedConsCell(2, 3)
    c = SharedConsCell()
    d = SharedConsCell(2, 4)
    e = SharedConsCell(2, SharedConsCell(3, 4))
    f = SharedConsCell(2, SharedConsCell(3, 4))
    g = SharedConsCell(2, SharedConsCell(3, 5))
    assert id(a) != id(b)
    assert a == b
    assert a != c
    assert a != d
    assert a != e
    assert e == f
    a = SharedConsCell(SharedConsCell(1, 2), 3)
    b = SharedConsCell(SharedConsCell(1, 2), 3)
    c = SharedConsCell(SharedConsCell(1, 2), 4)
    d = SharedConsCell(SharedConsCell(1, 99), 3)
    assert a == b
    assert a != c
    assert a != d

    # Long lists equality doesn't blow stack
    a = None
    b = None
    for i in range(100):
        a = SharedConsCell(1, a)
        b = SharedConsCell(1, b)
    assert a == b


def test_performance():
    N = 10000
    start = datetime.datetime.now()
    a = None
    for i in range(N):
        a = SharedConsCell(1, a)
    cons_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    node = a
    i = 0
    while node is not None:
        i += 1
        node = node.cdr()
    assert i == N
    walk_time = datetime.datetime.now() - start

    assert cons_time < datetime.timedelta(seconds=12)
    assert walk_time < datetime.timedelta(seconds=7)
    
#test_SharedConsCell()
