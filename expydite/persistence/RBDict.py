"""
A persistent implementation of a collections.MutableMapping (key-value mapping)
using the Okasaki/Germane/Might algorithm.
"""
from collections.abc import MutableMapping, Mapping, Iterable

from expydite.persistence.RBNode import (
    AbstractRBNode, RBNode, insert, search, count, delete, E)
from expydite.persistence.RBIterator import (
    RBDictKeyIterator, RBDictValueIterator, RBDictItemsIterator)


class RBDict(MutableMapping):
    __slots__ = ["_root", "_length"]

    
    def __init__(self, initializer=None, length=None):
        if initializer is None:
            self._root = E
            self._length = 0
        elif isinstance(initializer, AbstractRBNode):
            self._root = initializer
            self._length = len(initializer) if length is None else length
        elif isinstance(initializer, Mapping):
            self._root = E
            self._length = 0
            for k in initializer.keys():
                self._root = insert((k, initializer[k]), self._root)
                self._length += 1
        elif isinstance(initializer, Iterable):
            self._root = E
            self._length = 0
            for elem in iter(initializer):
                if len(elem) != 2:
                    raise ValueError(f"dictionary update sequence element {elem} has length {len(elem)}; 2 is required")
                self._root = insert(elem, self._root)
                self._length += 1
        else:
            raise ValueError("initializer is not an instance of collections.abc.Mapping")

        
    # Mapping methods
    def __getitem__(self, key):
        sr = search(key, self._root)
        if sr is None:
            raise KeyError(key)
        return sr.datum.value

    
    def __iter__(self): return RBDictKeyIterator(self._root)

    
    def __len__(self): return count(self._root)

    
    # MutableMapping methods
    def __setitem__(self, key, value):
        if key not in self:  # Todo figure out how to not search here but also keep length
            self._root = insert((key, value), self._root)
            self._length += 1
        else:
            self._root = insert((key, value), self._root)  # update


    def __delitem__(self, key):
        if key in self:
            self._root = delete(key, self._root)
            self._length -= 1


    # Mapping mixin methods:
    # __contains__, keys, items, values, get, __eq__, and __ne__
    def __contains__(self, key):
        for k in self:
            if k == key:
                return True

        return False


    def keys(self): return iter(self)

    
    def items(self): return RBDictItemsIterator(self._root)


    def values(self): return RBDictValueIterator(self._root)

    
    def get(self, key): return self.__getitem__(key)


    def __eq__(self, other):
        "Better way to do this?"
        if self._length != other._length:
            return False
        it = iter(other)
        for k in self:
            try:
                next_k = next(it)
            except StopIteration:
                return False
            if k != next_k:
                return False
            if self[k] != other[k]:
                return False
        try:
            next(it)
            return False
        except StopIteration:
            return True


    def __ne__(self, other): return not self.__eq__(other)
    

    # MutableMapping mixin methods:
    # pop, popitem, clear, update, and setdefault
    def pop(self, key):
        """
        Idea: update RBNode.delete to return a tuple consisting of the deleted
        datum and the resulting tree. This way RBDict.pop can avoid the search
        before the delete.
        """
        node = search(key, self._root)
        if node is None:
            raise KeyError(key)
        self._root = delete(key, self._root)
        self._length -= 1

        return node.datum.value


    def popitem(self):
        result = (self._root.datum.key, self._root.datum.value)
        self._root = delete(self._root.datum.key, self._root)
        self._length -= 1

        return result
        

    def clear(self):
        self._root = E
        self._length = 0


    def update(self, updates):
        for item in updates:
            sr = search(item[0], self._root)
            if sr is None:
                self._root = insert(item, self._root)
                self._length += 1
            else:
                self._root = insert(item, self._root)
        

    def setdefault(self, key, value):
        if key in self:
            return self[key]
        else:
            self[key] = value
            return value
