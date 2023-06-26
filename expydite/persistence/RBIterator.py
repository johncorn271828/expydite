"""
This iterator class walks through the Red Black tree (see RBNode.py) in a
deterministic order, but the client cannot assume an ordering.
"""
from collections import deque


class AbstractRBIterator:
    "Return one of these from a Red-Black tree collection's iter() call"
    __slots__ = ["_root", "_todo", "_node"]
    
    def __init__(self, tree):
        self._root = tree
        self._node = tree
        self._todo = deque()

    def __iter__(self): return self

    def _walk(self):
        #if self._node is None:
        if not self._node:
            raise StopIteration
        # First visit to a node cases
        if len(self._todo) == 0 or self._todo[-1] != self._node:
            # Has left node -> recurse and come back later
            if self._node and self._node.left:
                self._todo.append(self._node)
                self._node = self._node.left
                return self._walk()
            # Has right node -> return this one and then go there
            elif self._node and not self._node.left and self._node.right:
                result = self._node
                self._node = self._node.right
                return result
            # No children -> proceed down todo list
            else:
                result = self._node
                if len(self._todo) == 0: # No children, nothing else to do
                    self._node = None
                else:
                    self._node = self._todo[-1]
                return result

        # Return to a node cases
        elif self._todo[-1] == self._node:
            # Has right node -> return this then go there
            if self._node and self._node.right:
                result = self._node
                self._node = self._node.right
                self._todo.pop()
                return result
            # No children -> back up
            else:
                result = self._node
                self._todo.pop()  # ?
                try:
                    self._node = self._todo[-1]
                except IndexError:
                    self._node = None
                return result

            
class RBSetIterator(AbstractRBIterator):
    ""
    def __next__(self):
        return self._walk().datum.key


class RBDictKeyIterator(AbstractRBIterator):
    ""
    def __next__(self):
        return self._walk().datum.key
    

class RBDictValueIterator(AbstractRBIterator):
    ""
    def __next__(self):
        return self._walk().datum.value    


class RBDictItemsIterator(AbstractRBIterator):
    ""
    def __next__(self):
        datum = self._walk().datum
        return datum.key, datum.value
    
