from expydite.sharedmem import make_shared
from expydite.sharedmem import shared
from expydite.recursion import tco


class AbstractConsCell:
    """
    A lisp-like Cons cell for singly-linked lists or trees.
    """
    __slots__ = ["_car", "_cdr"]
    
    def __init__(self, a=None, b=None):
        self._car = a
        self._cdr = b

    def car(self): return self._car

    def cdr(self): return self._cdr

    def cons(self, newcar):
        # This fails because it refers to the vanilla __new__
        newcdr = self.__class__(self._car, self._cdr)  
        # newcdr = self.__class__.__new__(
        #     self.__class__, self._car, self._cdr)
        # newcdr.__init__(self._car, self._cdr)
        self._cdr = newcdr
        self._car = newcar

    def rplaca(self, newcar):
        self._car = newcar

    def rplacd(self, newcdr):
        self._cdr = newcdr

    def __deepcopy__(self, memodict=dict()):
        # Can't call deepcopy from shared object, so implement here
        copyscar = (self._car.__deepcopy__()
                     if hasattr(self._car, "__deepcopy__") else self._car)
        copyscdr = (self._cdr.__deepcopy__()
                     if hasattr(self._cdr, "__deepcopy__") else self._cdr)
        the_copy = make_shared(self.__class__, copyscar, copyscdr)
        
        return the_copy


    def _eq(self, other):
        return (False if not self._same_type_as(other) else
                # Avoid bad tail recusion optimization via __ne__
                # Can still blow the stack here for badly constructed list
                False if self.car() != other.car() else
                # Good tail recursion here
                self.cdr() == other.cdr())

    # Want to prevent blowing the stack on long lists.
    # TODO make sure this works
    __eq__ = tco(_eq)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        print("called __str__")
        return "(" + str(self._car) + " . " + str(self._cdr) + ")"

    def __bool__(self):
        return self._car is not None or self._cdr is not None

    def _same_type_as(self, other):
        # For the case of a legit comparison to another ConsCell, other will
        # really be an AutoProxy[ConsCell] because of the __new__ hacking.
        # So check proxy._token.typeid.
        same_type = type(self) == type(other)
        other_is_proxy = (
            hasattr(other, "_token") and
            getattr(other._token, "typeid") == self.__class__.__name__)

        return same_type or other_is_proxy

    def _equal_cdrs(self, other):
        """
        Avoid blowing the stack by replacing equality checking on cdrs with a
        while loop.
        """
        result = True
        node = self.cdr()
        other_node = other.cdr()
        print(type(node))
        print(type(other_node))
        while self._same_type_as(node) and self._same_type_as(other_node):
            if node.car() != other_node.car():
                result = False
                break
            node = node.cdr()
            other_node = other_node.cdr()
        # Now one of these guys isn't a ConsCell proxy
        if node != other_node:
            result = False

        return True


class ConsCell(AbstractConsCell):
    pass

@shared
class SharedConsCell(AbstractConsCell):
    def cons(self, newcar):
        # This fails because it refers to the vanilla __new__
        # newcdr = self.__class__(self._car, self._cdr)  
        # newcdr = self.__class__.__new__(
        #     self.__class__, self._car, self._cdr)
        # newcdr.__init__(self._car, self._cdr)
        newcdr = make_shared(self.__class__, self._car, self._cdr)
        self._cdr = newcdr
        self._car = newcar

    pass
