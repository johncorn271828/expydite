import datetime
from random import randint
from collections import deque

from expydite.impersistence.Cons import Cons
# from expydite.compilation import jit_import
# jit_Cons = jit_import("expydite.impersistence.Cons")
# Cons = jit_Cons.Cons


def test_stack_performance_vs_deque():
    N = 1000000

    start = datetime.datetime.now()
    a = Cons()
    for i in range(N):
        a.append(randint(0, 10))
    cons_append_time = datetime.datetime.now() - start
    start = datetime.datetime.now()
    for i in range(N):
        a.pop()
    cons_pop_time = datetime.datetime.now() - start

    start = datetime.datetime.now()
    a = deque()
    for i in range(N):
        a.append(randint(0, 10))
    deque_append_time = datetime.datetime.now() - start
    start = datetime.datetime.now()
    for i in range(N):
        a.pop()
    deque_pop_time = datetime.datetime.now() - start

    # Way slower. Why?
    assert cons_append_time < 2.5 * deque_append_time
    assert cons_pop_time < 10 * deque_pop_time


def test___contains__performance_vs_set():
    N = 1000000
    n = 10

    # Populate lots of random sets
    sets = []
    for i in range(N):
        sets.append(set())
        for j in range(n):
            sets[i].add(randint(0, 10))

    # Check for membership
    start = datetime.datetime.now()
    found = 0 
    for i in range(N):
        for j in range(n):
            if randint(0, 10) in sets[i]:
                found += 1
    set_time = datetime.datetime.now() - start

    # Populate lots of random conses
    conses = []
    for i in range(N):
        conses.append(Cons())
        for j in range(n):
            conses[i].add(randint(0, 10))

    # Check for membership
    start = datetime.datetime.now()
    found = 0 
    for i in range(N):
        for j in range(n):
            if randint(0, 10) in conses[i]:
                found += 1
    cons_time = datetime.datetime.now() - start

    # Slower, but not too bad
    assert cons_time < 3 * set_time


def test_insert_performance_vs_list():
    N = 1000
    
    thelist = list(range(N))
    list_prepends = 0
    start = datetime.datetime.now()
    while datetime.datetime.now() - start < datetime.timedelta(seconds=5):
        thelist[10:20] = list(range(N))
        list_prepends += 1
        
    clist = Cons(range(N))
    clist_prepends = 0
    start = datetime.datetime.now()
    while datetime.datetime.now() - start < datetime.timedelta(seconds=5):
        clist[10:20] = Cons(range(N))
        clist_prepends += 1

    assert clist_prepends > 1.2 * list_prepends
    
    N = 100000
    M = 1000
    n = 100
    count = 10000
    thelist = list(range(N))
    theconslist = Cons(range(N))

    # Lots of insertions to middle of list
    start = datetime.datetime.now()
    for i in range(count):
        thelist[n:n+1] = list(range(M))
    list_time = datetime.datetime.now() - start

    # Same for Cons
    start = datetime.datetime.now()
    for i in range(count):
        theconslist[n:n+1] = Cons(range(M))
    conslist_time = datetime.datetime.now() - start

    assert list_time > 1.2 * conslist_time


