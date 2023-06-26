"""
Test suite for Red Black tree dicts.
"""
import datetime
from random import randint

from expydite.persistence.RBNode import RBNode, E
from expydite.persistence.RBDict import RBDict


def test_basics():
    d = RBDict()
    assert d._root == E
    d = RBDict(E)
    assert d._root == E
    old = {1:2, 3:4, 5:6}
    d = RBDict(old)
    assert d[1] == 2
    for k in d:
        assert d[k] == old[k]
    assert len(d) == 3
    del d[1]
    assert d == RBDict({3:4, 5:6})
    assert 3 in d.keys()
    assert 4 in d.values()


def test_Mapping_mixins():
    # __contains__, keys, items, values, get, __eq__, and __ne__
    a = [(1, 2), (3, 4), (5, 6)]
    b = [(1, 2), (3, 4)]
    c = [(3, 4), (5, 6)]

    da = dict(a)
    db = dict(b)
    dc = dict(c)

    ra = RBDict(a)
    rb = RBDict(b)
    rc = RBDict(c)

    for i in range(6):
        assert (i in da) == (i in ra)
        assert (i in db) == (i in rb)
        assert (i in dc) == (i in rc)
        assert (i in da.keys()) == (i in ra.keys())
        assert (i in db.keys()) == (i in rb.keys())
        assert (i in dc.keys()) == (i in rc.keys())
        assert (i in da.items()) == (i in ra.items())
        assert (i in db.items()) == (i in rb.items())
        assert (i in dc.items()) == (i in rc.items())
        assert (i in da.values()) == (i in ra.values())
        assert (i in db.values()) == (i in rb.values())
        assert (i in dc.values()) == (i in rc.values())        

    for i in da:
        assert da.get(i) == ra.get(i)
    for i in db:
        assert db.get(i) == rb.get(i)
    for i in dc:
        assert dc.get(i) == rc.get(i)

    assert RBDict(a) == ra
    assert RBDict(b) == rb
    assert RBDict(c) == rc


def test_MutableMapping_mixins():
    # pop, popitem, clear, update, and setdefault
    a = [(1, 2), (3, 4), (5, 6)]
    b = [(1, 2), (3, 4)]
    c = [(3, 4), (5, 6)]

    da = dict(a)
    db = dict(b)
    dc = dict(c)

    ra = RBDict(a)
    rb = RBDict(b)
    rc = RBDict(c)

    da.pop(1)
    ra.pop(1)
    assert RBDict(da) == ra

    # Not sure whether this is expected to be same element?
    #assert db.popitem() == rb.popitem()
    #assert RBDict(db) == rb
    assert type(db.popitem()) == type(rb.popitem())
    assert len(db) == len(rb)

    da.clear()
    ra.clear()
    assert RBDict(da) == ra

    updates = [(5,7), (8,9)]
    dc.update(updates)
    rc.update(updates)
    assert RBDict(dc) == rc

    assert dc.setdefault(3, 5) == rc.setdefault(3,5)
    assert dc.setdefault(10, 11) == rc.setdefault(10, 11)
    assert RBDict(dc) == rc
    
