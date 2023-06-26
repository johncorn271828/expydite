"""
A persistent implementation of a collections.MutableSet using the
Okasaki/Germane/Might algorithm.
"""
from collections.abc import MutableSet, Iterable

from expydite.persistence.RBIterator import RBSetIterator
from expydite.persistence.RBNode import (
    _make_datum,
    AbstractRBNode, RBNode, insert, search, delete, E, R, B, _balance)


class RBSet(MutableSet):
    __slots__ = ["_root", "_length"]
    
    def __init__(self, initializer=None, length=None):
        ""
        if initializer is None:
            self._root = E  # Is this ok?
            self._length = 0
        elif isinstance(initializer, AbstractRBNode):
            self._root = initializer
            self._length = len(initializer) if length is None else length
        elif isinstance(initializer, Iterable):
            self._root = E
            self._length = 0
            it = iter(initializer)
            for elem in it:
                self._root = insert(elem, self._root)
                self._length += 1
        else: # Some data
            self._root = RBNode(B, E, _make_datum(initializer), E)
            self._length = 1

            
    # Set abstract methods
    def __contains__(self, key):
        ""
        #print(f"called contains on a {type(key)}")
        result =  search(key, self._root) is not None
        #print(f"finished __contains__ with result {result}")
        return result

    
    def __len__(self): return self._length

    
    def __iter__(self): return RBSetIterator(self._root)

    
    # MutableSet - abstract methods
    def add(self, key):
        ""
        #print(f"called add({self._root}, {key})")
        if key not in self: # TODO keep track of length witout this?
            #print("finished add's contains call")
            self._root = insert(key, self._root)
            self._length += 1
        else:
            #print("nothing to do, finished add")
            pass

        
    def discard(self, key):
        ""
        if key in self:  # TODO keep track of length witout this?
            self._root = delete(key, self._root)
            self._length -= 1

            
    # Other methods
    def __str__(self):
        ""
        return str(self._root)

    
    # Mixin methods from Set - override to prevent silly auto implementation
    # __le__, __lt__, __eq__, __ne__, __gt__, __ge__, __and__, __or__, __sub__, __xor__, and isdisjoint
    def __le__(self, other):
        ""
        for elem in self:
            if elem not in other:
                return False

        return True


    def __lt__(self, other):
        ""
        return self._length < other._length and self.__le__(other)


    def __eq__(self, other):
        ""
        if self._length != other._length:
            return False
        it = iter(other)
        for elem in self:
            try:
                if next(it) != elem:
                    return False
            except StopIteration:
                return False
        try:
            next(it)
            return False
        except StopIteration:
            return True


    def __ne__(self, other): return not self.__eq__(other)


    def __gt__(self, other):
        ""
        return self._length > other._length and self.__ge__(other)


    def __ge__(self, other):
        ""
        for elem in other:
            if elem not in self:
                return False

        return True
    

    def __and__(self, other):
        ""
        result = RBSet()
        for elem in self:
            if elem in other:
                result.add(elem)

        return result


    def __or__(self, other):
        ""
        result = RBSet()
        for elem in self:
            result.add(elem)
        for elem in other:
            result.add(elem)

        return result


    def __sub__(self, other):
        ""
        result = RBSet()
        for elem in self:
            if elem not in other:
                result.add(elem)

        return result


    def __xor__(self, other):
        ""
        result = RBSet()
        for elem in self:
            if elem not in other:
                result.add(elem)
        for elem in other:
            if elem not in self:
                result.add(elem)
                
        return result


    def isdisjoint(self, other):
        ""
        for elem in self:
            if elem in other:
                return False


        return True

    
    # Mixin methods from MutableSet
    # clear, pop, remove, __ior__, __iand__, __ixor__, and __isub__
    def clear(self):
        ""
        self._root = E
        self._length = 0


    def pop(self):
        ""
        node = self._root
        while node.left:
            node = node.left
        result = node.datum.key
        self.discard(result)

        return result


    def remove(self, elem):
        ""
        self.discard(elem)


    def __ior__(self, other):
        ""
        for elem in other:
            self.add(elem)

        return self


    def __iand__(self, other):
        ""
        result = RBSet()
        for elem in self:
            if elem in other:
                result.add(elem)
        self._root = result._root
        self._length = result._length

        return self


    def __ixor__(self, other):
        ""
        result = RBSet()
        for elem in self:
            if elem not in other:
                result.add(elem)
        for elem in other:
            if elem not in self:
                result.add(elem)

        self._root = result._root
        self._length = result._length

        return self


    def __isub__(self, other):
        ""
        for elem in other:
            self.discard(elem)


        return self
