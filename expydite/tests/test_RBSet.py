import datetime
from random import randint

from expydite.persistence.RBNode import RBSetNode
from expydite.persistence.RBSet import RBSet


xs = RBSetNode(False, "d",
            RBSetNode(True, "b",
                   RBSetNode(False, "a", None, None),
                   RBSetNode(False, "c", None, None)),
            RBSetNode(True, "g",
                   RBSetNode(False, "f", None, None),
                   RBSetNode(False, "h", None, None)))
ys = RBSetNode(False, 3,
            RBSetNode(True, 1,
                   RBSetNode(False, 0, None, None),
                   RBSetNode(False, 2, None, None)),
            RBSetNode(True, 6,
                   RBSetNode(False, 5, None, None),
                   RBSetNode(False, 7, None, None)))


def test_RBSetNode():
    xs_str = str(xs)
    assert xs_str.startswith("(B d (")


def test_RBSet():
    rbs = RBSet(xs)
    assert "g" in rbs
    assert "q" not in rbs
    assert len(rbs) == 7
    it = iter(rbs)
    assert next(it) == "a"
    assert next(it) == "b"
    assert next(it) == "c"
    assert next(it) == "d"
    assert next(it) == "f"
    assert next(it) == "g"
    assert next(it) == "h"
    try:
        next(it)
        assert False
    except StopIteration:
        assert True

    # Can iterate more than once
    letters = "abcdfgh"
    it = iter(letters)
    for key in rbs:
        assert key == next(it)
    
def test_mutable_RBSet():
    rbs = RBSet(xs)
    rbs2 = RBSet(xs)
    rbs.add("e")
    print(rbs._root)
    assert "e" in rbs
    assert "e" not in rbs2


def test_mutable_RBSet2():
    rbs = RBSet(ys)
    s = set(iter(rbs))
    for i in range(1000000):
        n = randint(0,500)
        rbs.add(n)
        s.add(n)
    rbs_set = set(rbs)
    for n in s:
        assert rbs.__contains__(n)


def test_mutable_RBSet_performance():

    N = 1000000
    max_n = 500
    
    rbs = RBSet(ys)
    s = set(iter(rbs))

    start = datetime.datetime.now()
    for i in range(N):
        n = randint(0,max_n)
        rbs.add(n)
    rbs_insert_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    for i in range(N):
        n = randint(0,max_n)
        s.add(n)
    s_insert_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    for i in range(N):
        n = randint(0,max_n)
        rbs.__contains__(n)
    rbs_search_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    for i in range(N):
        n = randint(0,max_n)
        s.__contains__(n)
    s_search_time = datetime.datetime.now() - start

    print(f"rbs_insert_time = {rbs_insert_time}")
    print(f"s_insert_time = {s_insert_time}")
    print(f"rbs_search_time = {rbs_search_time}")
    print(f"s_search_time = {s_search_time}")
    assert rbs_insert_time < 20 * s_insert_time
    assert rbs_search_time < 20 * s_search_time


if __name__ == "__main__":
    test_mutable_RBSet_performance()
