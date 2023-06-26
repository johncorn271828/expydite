"""
Test suite for Red Black tree sets.
"""
import datetime
from collections import deque
from random import randint

from expydite.persistence.RBNode import RBNode, Color
from expydite.persistence.RBSet import RBSet, E


xs = ["a", "b", "c", "d", "f" , "g", "h"]
ys = [1, 2, 3, 4, 5, 6, 7]


def test_ctor():
    s = RBSet()
    assert s._root == E
    s = RBSet(E)
    assert s._root == E
    s = RBSet(123)
    assert s._root.datum.key == 123

def test_RBSet():
    rbs = RBSet(xs)
    print(rbs)
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
    for node in rbs:
        assert node == next(it)
    
def test_mutable_RBSet():
    rbs = RBSet(xs)
    print(rbs)
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


def test_Set_mixins():
    s1 = RBSet(set([1,2,3]))
    s2 = RBSet(set([1,2]))
    s3 = RBSet(set([3]))
    assert s2 <= s1
    assert s2 < s1
    assert s2 == RBSet([1,2])
    assert s1 != s2
    assert s1 > s2
    assert s1 >= s2
    assert s1 & s2 == s2
    assert s1 | s2 == s1
    assert s1 - s2 == s3
    assert s1 ^ s2 == s3
    assert s2.isdisjoint(s3)
    assert not s2.isdisjoint(s1)


def test_MutableSet_mixins():
    s = RBSet([1,2,3])
    s.clear()
    assert s._root == E
    assert s._length == 0
    s = RBSet([1,2,3])
    assert s.pop() == 1
    assert s == RBSet([2,3])
    s.remove(2)
    assert s == RBSet([3])
    s = RBSet([1,2,3])
    s2 = RBSet([3, 4])
    s |= s2
    print(s)
    assert s == RBSet([1,2,3,4])
    s = RBSet([1,2,3])
    s &= s2
    assert s == RBSet([3])
    s = RBSet([1,2,3])
    s ^= s2
    s == RBSet([1,2,4])
    s = RBSet([1,2,3])
    s -= RBSet([1,2])
    assert s == RBSet([3])
    

def test_mutable_RBSet_performance():

    N = 1000000
    max_n = 500
    
    rbs = RBSet(ys)
    s = set(iter(rbs))

    # Race insert
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

    # Race search
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

    # Race delete
    start = datetime.datetime.now()
    for i in range(N):
        n = randint(0,max_n)
        rbs.discard(n)
    rbs_delete_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    for i in range(N):
        n = randint(0,max_n)
        s.discard(n)
    s_delete_time = datetime.datetime.now() - start

    
    print(f"rbs_insert_time = {rbs_insert_time}")
    print(f"s_insert_time = {s_insert_time}")
    assert rbs_insert_time < 4 * s_insert_time
    print(f"rbs_search_time = {rbs_search_time}")
    print(f"s_search_time = {s_search_time}")
    assert rbs_search_time < 4 * s_search_time
    print(f"rbs_delete_time = {rbs_delete_time}")
    print(f"s_delete_time = {s_delete_time}")
    assert rbs_delete_time < 4 * s_delete_time


if __name__ == "__main__":
    test_mutable_RBSet2()
    #test_mutable_RBSet_performance()
