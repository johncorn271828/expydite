"""
Test suite and stress test for Okasaki/Germane/Might algorithm.
"""
import datetime
import pytest
from random import randint, shuffle
from typing import Optional, Any 
from dataclasses import dataclass
from enum import Enum
from collections import OrderedDict

from expydite.recursion import tco
from expydite.persistence.RBNode import (
    _make_datum,
    _blacken, T, insert, search, delete, count, R, B, BB, E, EE, T)


def test_insert_count():
    xs = T(B, T(R, T(B, E, _make_datum(0), E), _make_datum(1), T(B, E, _make_datum(2), E)), _make_datum(3),
           T(R, T(B, E, _make_datum(5), E), _make_datum(6), T(B, E, _make_datum(7), E)))

    xs = insert(4, xs)
    #print(str(xs))
    assert " 4 " in str(xs)
    assert count(xs) == 8

#@pytest.mark.skip(reason="SLOW")
def test_insert_performance():
    print("test_insert_performance...")
    # xs = T(B, T(R, T(B, E, _make_datum(0), E), _make_datum(1), T(B, E, _make_datum(2), E)), _make_datum(3),
    #        T(R, T(B, E, _make_datum(5), E), _make_datum(6), T(B, E, _make_datum(7), E)))
    # xs = insert(4, xs)

    # s = set(range(8))

    xs = E
    s = set()

    N = 1_000_000
    max_n = 500

    for i in range(1000):
        n = randint(0, max_n)
        xs = insert(n, xs)
        s.add(n)
    for n in range(max_n):
        if n in s:
            assert search(n, xs) is not None
        else:
            assert search(n, xs) is None
    
    start = datetime.datetime.now()
    for i in range(N):
        n = randint(0,max_n)
        xs = insert(n, xs)
    rbs_insert_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    for i in range(N):
        n = randint(0,max_n)
        s.add(n)
    s_insert_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    for i in range(N):
        n = randint(0,max_n)
        search(n, xs)
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
    assert rbs_insert_time < 15 * s_insert_time
    assert rbs_search_time < 3 * s_search_time


def test_delete():
    print("test_delete...")
    xs = T(B, T(R, T(B, E, _make_datum(0), E), _make_datum(1), T(B, E, _make_datum(2), E)), _make_datum(3),
           T(R, T(B, E, _make_datum(5), E), _make_datum(6), T(B, E, _make_datum(7), E)))
    #print(xs)
    old_str = str(xs)
    xs = insert(4, xs)
    #print(xs)
    xs = delete(4, xs)
    #print(xs)
    assert str(xs) == old_str

    assert search(4, xs) is None
    assert search(5, xs) is not None

    # Stress test to throw errors
    max_n = 500
    rbs = E
    s = set()
    rands = []
    for i in range(3000):
        rands.append(randint(0, max_n))
    #print(rands)
    for i in range(3000):
        n = rands[i]
        rbs = insert(n, rbs)
        s.add(n)
    for i in range(3000):
        n = rands[i]
        if n in s and i % 2 == 0:
            rbs = delete(n, rbs)
            s.remove(n)
    for n in s:
        assert (str(n) + " " ) in str(rbs)

    # Compare correctness vs set
    max_n = 500
    rbs = E
    s = set()
    rands = []
    for i in range(1000):
        n = randint(0, max_n)
        rands.append(n)
    #print(rands)
    for i in range(len(rands)):
        n = rands[i]
        rbs = insert(n, rbs)
    for i in range(len(rands)):
        if i % 2 == 0:
            rbs = delete(n, rbs)
            if (" " + str(n) + " " ) in str(rbs):
                print(f"Failed to delete {n} from {rbs}")
                assert False

                
def test_delete_performance():
    print("test_delete_performance...")
    N = 1_000_000
    max_n = 35_000
    prbs = E
    rbs = OrderedDict()
    rands = []
    
    for i in range(N):
        #n = randint(0, max_n)
        if i % 3 == 0:
            pass
        rands.append(i % max_n)
    shuffle(rands)

    start = datetime.datetime.now()
    for n in rands:
        #s.add(n)
        rbs[n] = True
    rbs_insert_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    for n in rands:
        prbs = insert(n, prbs)
    prbs_insert_time = datetime.datetime.now() - start

    rands = list(set(rands))
    shuffle(rands)

    start = datetime.datetime.now()
    for n in rands:
        #s.remove(n)
        del rbs[n]
    rbs_delete_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    for n in rands:
        prbs = delete(n, prbs)
    prbs_delete_time = datetime.datetime.now() - start

    print(f"rbs_insert_time = {rbs_insert_time}")
    print(f"rbs_delete_time = {rbs_delete_time}")
    print(f"prbs_insert_time = {prbs_insert_time}")
    print(f"prbs_delete_time = {prbs_delete_time}")


