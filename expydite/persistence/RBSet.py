from collections.abc import Set

from expydite.persistence.RBNode import RBSetNode
from expydite.persistence.rb_utils import _search, _size
from expydite.persistence.RBIterator import RBIterator


class RBSet(Set):
    __slots__ = ["_root", "_length"]
    
    def __init__(self, initializer=None, length=None):
        if initializer is None:
            self._root = initializer
            self._length = 0
        elif isinstance(initializer, RBSetNode):
            self._root = initializer
            self._length = _size(initializer) if length is None else length
        # TODO iterator ctor

    # Set methods
    def __contains__(self, key):
        return _search(self._root, key) is not None
    
    def __len__(self): return self._length

    def __iter__(self): return RBIterator(self._root)

    # MutableSet Methods
    def add(self, key):
        if not self.__contains__(key):
            self._root = RBSet._ins(self._root, key)
            self._length += 1

    def remove(self, key): pass

    # Private helper methods
    @staticmethod
    def _ins(node, key):
        if node is None:
            return RBSetNode(True, key, None, None)
        else:
            return (RBSet._lbalance(node.red, node.key,
                                    RBSet._ins(node.left, key), node.right)
                    if key < node.key else
                    RBSet._rbalance(node.red, node.key,
                                    node.left, RBSet._ins(node.right, key))
                    if key > node.key else node)

    @staticmethod
    def _lbalance(red, key, left, right):
        """
        See Okasaki page 27. Big pretty picture.
        """
        if not red:
            if left.red:
                # black node with red left child with red left child
                if left.left is not None and left.left.red:
                    return RBSetNode(True, left.key,
                                     RBSetNode(False, left.left.key,
                                               left.left.left, left.left.right),
                                     RBSetNode(False, key,
                                               left.right, right))
                # black node with red left child with red right child
                if left.right is not None and left.right.red:
                    return RBSetNode(True, left.right.key,
                                     RBSetNode(False, left.key,
                                               left.left, left.right.left),
                                     RBSetNode(False, key,
                                               left.right.right, right))
        return RBSetNode(red, key, left, right)

    @staticmethod
    def _rbalance(red, key, left, right):
        if not red:
            if right.red:
                # Black node with red right child with red right child
                if right.right is not None and right.right.red:
                    return RBSetNode(True, right.key,
                                     RBSetNode(False, key,
                                               left, right.left),
                                     RBSetNode(False, right.right.key,
                                               right.right.left,
                                               right.right.right))
                # Black node with red right child with red left child
                if right.left is not None and right.left.red:
                    return RBSetNode(True, right.left.key,
                                     RBSetNode(False, key,
                                               left, right.left.left),
                                     RBSetNode(False, right.key,
                                               right.left.right, right.right))
        return RBSetNode(red, key, left, right)
