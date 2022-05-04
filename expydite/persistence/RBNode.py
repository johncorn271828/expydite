from expydite.sharedmem import shared, make_shared


class AbstractRBNode:

    def __str__(self):
        return ("(" + ("R" if self.red else "B") + " " + str(self.key) +
                (" : " + str(self.value)  if hasattr(self, "value") else "") +
                ((" " + str(self.left) + " " + str(self.right))
                 if  self.left is not None or self.right is not None else "") +
                ")")

    __repr__ = __str__

    def __eq__(self, other):
        return (type(self) == type(other) and
                all(getattr(self, attr) == getattr(other, attr)
                    for attr in self.__slots__))


class AbstractRBSetNode(AbstractRBNode):
    __slots__ = ["red", "key", "left", "right"]
    def __init__(self, red, key, left=None, right=None):
        self.red = red
        self.key = key
        self.left = left
        self.right = right


class RBSetNode(AbstractRBSetNode):
    pass


#TODO class SharedRBSetNode(AbstractRBSetNode):


class AbstractRBDictNode(AbstractRBNode):
    __slots__ = ["red", "key", "value", "left", "right"]
    def __init__(self, red, key, value=None, left=None, right=None):
        self.red = red
        self.key = key
        self.value = value
        self.left = left
        self.right = right


class RBDictNode(AbstractRBDictNode):
    pass

# TODO class SharedRBDictNode
