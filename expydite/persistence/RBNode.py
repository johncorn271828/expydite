"""
This module contains an implementation of the Okasaki/Germane/Might algorithm
for persistent Red-Black trees. It is intended to support set-like and dict-like
collections adhering to collections.abc (see RBSet.py, RBDict.py)

The deletion algorithm is tricky, and required some tweaks to the published
version. Originally implemented with pattern matching to mimick the Haskell in
Germane/Might, then optimized with nested if/else statements. See appendix for
pattern matching version of delete().
"""
import datetime
from typing import Optional, Any
from dataclasses import dataclass
from enum import Enum
from collections import OrderedDict, deque

from expydite.recursion import tco


class Color(Enum):
    "Represents the color of a Germane-Might tree node (includes double black)"
    R = 0
    B = 1
    BB = 2

    def __str__(self):
        return ("R" if self == Color.R else
                "B" if self == Color.B else
                "BB")


class AbstractRBNode:
    ""
    pass


class EmptyRBNode(AbstractRBNode, Enum):
    ""
    E = 1
    EE = 2

    def __bool__(self): return False

    def __str__(self): return "E" if self == EmptyRBNode.E else "EE"

    def __len__(self): return 0



@dataclass(init=True, repr=True, eq=True, slots=True)
class RBDatum():
    "Data holder pointed to by the Red-Black tree node."
    key : Any = None

    def __str__(self): return str(self.key)

    def __eq__(self, other): return self.key == other.key

    def __lt__(self, other): return self.key < other.key

    def __le__(self, other): return self.key <= other.key

    def __gt__(self, other): return self.key > other.key

    def __ge__(self, other): return self.key >= other.key

    def __hash__(self): return self.key.__hash__()


@dataclass(init=True, repr=True, eq=True, slots=True)
class RBDictDatum(RBDatum):
    "A dictionary mapping (key-value pair)"
    key: Any = None
    value : Any = None

    def __str__(self): return str(self.key) + ":" + str(self.value)

    def __eq__(self, other): return self.key == other.key

    def __lt__(self, other): return self.key < other.key

    def __le__(self, other): return self.key <= other.key

    def __gt__(self, other): return self.key > other.key

    def __ge__(self, other): return self.key >= other.key

    def __hash__(self): return self.key.__hash__()


@dataclass(init=True, repr=True, eq=True, slots=True)
class RBNode(AbstractRBNode):
    "Non-empty Red-Black tree node"
    color: Color = Color.R
    left: AbstractRBNode = EmptyRBNode.E
    datum: RBDatum = RBDatum()
    right: AbstractRBNode = EmptyRBNode.E

    def __bool__(self): return True

    def __str__(self):
        return ("(" + ("R" if self.color == Color.R else
                       "B" if self.color == Color.B else "BB") +
                " " + str(self.left) +
                " " + str(self.datum) +
                " " + str(self.right) + ")")

    def __repr__(self): return str(self)

    def __len__(self): return count(self)


# Alias for less typing, faster execution
R = Color.R
B = Color.B
BB = Color.BB
E = EmptyRBNode.E
EE = EmptyRBNode.EE
T = RBNode


def insert(x, s):
    """
    Slightly different signature than Haskell.
    Done to avoid redefining _blacken and ins closures each invocation.
    
    insert x s = _blacken (ins s)
    where _ins E = T R E x E
          _ins (T color a y b) | x < y = _balance color (ins a) y b
                              | x == y = T color a y b
                              | x > y = _balance color a y (ins b)
          _blacken (T R (T R a x b) y c) = T B (T R a x b) y c
          _blacken (T R a x (T R b y c)) = T B a x (T R b y c)
          _blacken t = t
    """
    return _blacken(x, _ins(_make_datum(x), s))


def search(x, s):
    ""
    node = s
    while s:
        if s.datum.key == x:
            return s
        elif s.datum.key < x:
            s = s.right
        elif s.datum.key > x:
            s = s.left


def delete(x, s):
    """
    delete x s = del (_redden s)
    where del E = E
          del (T R E y E) | x == y = E
                          | x /= y = T R E y E
          del (T B E y E) | x == y = EE
                          | x /= y = T B E y E
          del (T B (T R E y E) z E) | x < z = T B (del (T R E y E)) z E
                                    | x == z = T B E y E
                                    | x > z = T B (T R E y E) z E
          del (T c a y b) | x < y = rotate c (del a) y b
                          | x == y = let (y’,b’) = _min_del b
                                       in rotate c a y’ b’
                          | x > y = rotate c a y (del b)
          _redden (T B (T B a x b) y (T B c z d)) =
              T R (T B a x b) y (T B c z d)
          _redden t = t
    """
    x = _make_datum(x)
    result =  _del(x, _redden(x, s))
    # This step explained verbally in the paper but not present in the code.
    if result and result.color == Color.BB:
        result.color = Color.B
    return result


def count(s):
    ""
    result = 0
    todo = deque()
    if s:
        todo.appendleft(s)
    while len(todo) != 0:
        node = todo.pop()
        if node.left:
            todo.appendleft(node.left)
        if node.right:
            todo.appendleft(node.right)
        result += 1

    return result


# End of public interface


def _blacken(x, t):
    ""
    if t and t.color == R:
        return T(B, t.left, t.datum, t.right)
    else:
        return t


def _lbalance(color, left, key, right):
    "Okasaki exercise 3.10, but with BB clauses improvised by me"
    if left and left.color == R:
        if color == B:
            # _balance B (T R (T R a x b) y c) z d = T R (T B a x b) y (T B c z d)
            if left.left and left.left.color == R:
                return T(R, T(B, left.left.left,
                              left.left.datum, left.left.right),
                         left.datum, T(B, left.right, key, right))
            # _balance B (T R a x (T R b y c)) z d = T R (T B a x b) y (T B c z d)
            elif left.right and left.right.color == R:
                return T(R, T(B, left.left, left.datum, left.right.left),
                         left.right.datum, T(B, left.right.right, key, right))
        elif color == BB:
            # _balance BB (T R a x (T R b y c)) z d = T B (T B a x b) y (T B c z d)
            if left.right and left.right.color == R:
                return T(B, T(B, left.left, left.datum, left.right.left),
                         left.right.datum, T(B, left.right.right, key, right))
            # _balance color a x b = T color a x b
    return T(color, left, key, right)


def _rbalance(color, left, key, right):
    ""
    if right and right.color == R:
        if color == B:
            # _balance B a x (T R (T R b y c) z d) = T R (T B a x b) y (T B c z d)
            if right.left and right.left.color == R:
                return T(R, T(B, left, key, right.left.left), right.left.datum,
                         T(B, right.left.right, right.datum, right.right))
            # _balance B a x (T R b y (T R c z d)) = T R (T B a x b) y (T B c z d)
            elif right.right and right.right.color == R:
                return T(R, T(B, left, key, right.left), right.datum,
                         T(B, right.right.left, right.right.datum,
                           right.right.right))
        elif color == BB:
            # _balance BB a x (T R (T R b y c) z d) = T B (T B a x b) y (T B c z d)
            if right.left and right.left.color == R:
                return T(B, T(B, left, key, right.left.left), right.left.datum,
                         T(B, right.left.right, right.datum, right.right))
            # _balance color a x b = T color a x b
    return T(color, left, key, right)   


def _balance(color, left, key, right):
    ""
    if color == B:
        if left and left.color == R:
            # _balance B (T R (T R a x b) y c) z d = T R (T B a x b) y (T B c z d)
            if left.left and left.left.color == R:
                return T(R, T(B, left.left.left,
                              left.left.datum, left.left.right),
                         left.datum, T(B, left.right, key, right))
            # _balance B (T R a x (T R b y c)) z d = T R (T B a x b) y (T B c z d)
            elif left.right and left.right.color == R:
                return T(R, T(B, left.left, left.datum, left.right.left),
                         left.right.datum, T(B, left.right.right, key, right))
        if right and right.color == R:
            # _balance B a x (T R (T R b y c) z d) = T R (T B a x b) y (T B c z d)
            if right.left and right.left.color == R:
                return T(R, T(B, left, key, right.left.left), right.left.datum,
                         T(B, right.left.right, right.datum, right.right))
            # _balance B a x (T R b y (T R c z d)) = T R (T B a x b) y (T B c z d)
            elif right.right and right.right.color == R:
                return T(R, T(B, left, key, right.left), right.datum,
                         T(B, right.right.left, right.right.datum,
                           right.right.right))
    elif color == BB:
        # _balance BB a x (T R (T R b y c) z d) = T B (T B a x b) y (T B c z d)
        if right and right.color == R and right.left and right.left.color == R:
            return T(B, T(B, left, key, right.left.left), right.left.datum,
                     T(B, right.left.right, right.datum, right.right))
        # _balance BB (T R a x (T R b y c)) z d = T B (T B a x b) y (T B c z d)
        if left and left.color == R and left.right and left.right.color == R:
            return T(B, T(B, left.left, left.datum, left.right.left),
                     left.right.datum, T(B, left.right.right, key, right))
        # _balance color a x b = T color a x b
    return T(color, left, key, right)


def _make_datum(key):
    "Factory method to control set vs dict datum"
    if isinstance(key, tuple) and len(key) == 2:
        return RBDictDatum(key[0], key[1])
    else:
        return RBDatum(key)


def _ins(x, s):
    ""
    print(x)
    print(f"s == E ? {s == E}")
    if s != E:
        print(s.datum)
        print(x < s.datum)
        print(x == s.datum)
        print(x.key == s.datum.key)
        print(x > s.datum)
    if s == E:
        result =  T(R, E, x, E)
    elif x < s.datum:
        result =  _lbalance(s.color, _ins(x, s.left), s.datum, s.right)
    elif x == s.datum:
        result =  T(s.color, s.left, x, s.right) # x instead of s.datum for dict update
    elif x > s.datum:
        result =  _rbalance(s.color, s.left, s.datum, _ins(x, s.right))

    return result


def _min_del(s):
    ""
    if s and s.left == E:
        if s.right == E:
            # _min_del (T R E x E) = (x,E)
            if s.color == R:
                return s.datum, E
            # _min_del (T B E x E) = (x,EE)
            elif s.color == B:
                return s.datum, EE
            # _min_del (T B E x (T R E y E)) = (x,T B E y E)
        elif s.color == B and s.right and s.right.color == R:
            return s.datum, T(B, E, s.right.datum, E)
        # _min_del (T c a x b) = let (x’,a’) = _min_del a
        #                         in (x’,rotate c a’ x b)
    xp, ap = _min_del(s.left)
    return xp, rotate(s.color, ap, s.datum, s.right)
            

def rotate(color, left, key, right):
    """
    """
    if color == R:
        if right and right.color == B:
            # rotate R (T BB a x b) y (T B c z d) = _balance B (T R (T B a x b) y c) z d
            if left and left.color == BB:
                return _balance(B, T(R, T(B, left.left, left.datum, left.right,),
                                     key, right.left), right.datum, right.right)
            # rotate R EE y (T B c z d) = _balance B (T R E y c) z d
            if left == EE:
                return _balance(B, T(R, E, key, right.left),
                                right.datum, right.right)
        if left and left.color == B:
            # rotate R (T B a x b) y (T BB c z d) = _balance B a x (T R b y (T B c z d))
            if right and right.color == BB:
                return _balance(B, left.left, left.datum,
                                T(R, left.right, key, T(B, right.left,
                                                        right.datum, right.right)))
            # rotate R (T B a x b) y EE = _balance B a x (T R b y E)
            if right == EE:
                return _balance(B, left.left, left.datum,
                                T(R, left.right, key, E))
    if color == B:
        if right and right.color == B:
            # rotate B (T BB a x b) y (T B c z d) = _balance BB (T R (T B a x b) y c) z d
            if left and left.color == BB:
                return _balance(BB, T(R, T(B, left.left, left.datum, left.right),
                                      key, right.left), right.datum, right.right)
            # rotate B EE y (T B c z d) = _balance BB (T R E y c) z d
            if left == EE:
                return _balance(BB, T(R, E, key, right.left), right.datum,
                                right.right)
        if left and left.color == B:
            # rotate B (T B a x b) y (T BB c z d) = _balance BB a x (T R b y (T B c z d))
            if right and right.color == BB:
                return _balance(BB, left.left, left.datum,
                                T(R, left.right, key,
                                  T(B, right.left, right.datum, right.right)))
            # rotate B (T B a x b) y EE = _balance BB a x (T R b y E)
            if right == EE:
                return _balance(BB, left.left, left.datum,
                                T(R, left.right, key, E))
        if right and right.color == R and right.left and right.left.color == B:
            # rotate B (T BB a w b) x (T R (T B c y d) z e) =
            #    T B (balance B (T R (T B a w b) x c) y d) z e
            if left and left.color == BB:
                return T(B, _balance(B, T(R, T(B, left.left,
                                               left.datum, left.right),
                                          key, right.left.left),
                                     right.left.datum, right.left.right),
                         right.datum, right.right)
            # rotate B EE x (T R (T B c y d) z e) = T B (balance B (T R E x c) y d) z e
            if left == EE:
                return T(B, _balance(B, T(R, E, key, right.left.left),
                                     right.left.datum, right.left.right),
                         right.datum, right.right)
        if left and left.color == R and left.right and left.right.color == B:
            # rotate B (T R a w (T B b x c)) y (T BB d z e) =
            #   T B a w (balance B b x (T R c y (T B d z e)))
            if right and right.color == BB:
                return T(B, left.left, left.datum,
                         _balance(B, left.right.left, left.right.datum,
                                  T(R, left.right.right, key,
                                    T(B, right.left, right.datum, right.right))))
            # rotate B (T R a w (T B b x c)) y EE = T B a w (balance B b x (T R c y E))
            if right == EE:
                return T(B, left.left, left.datum,
                         _balance(B, left.right.left, left.right.datum,
                                  T(R, left.right.right, key, E)))

    # rotate color a x b = T color a x b
    return T(color, left, key, right)
                                

def _redden(x, s):
    """
    _redden (T B (T B a x b) y (T B c z d)) =
        T R (T B a x b) y (T B c z d)
    """
    if (isinstance(s, T) and s.datum == x and s.color == B and
        isinstance(s.left, T) and s.left.color == B and
        isinstance(s.right, T) and s.right.color == B):
        return T(R, T(B, s.left.left, s.left.datum, s.left.right), s.datum,
                 T(B, s.right.left, s.right.datum, s.right.right))
    # _redden t = t
    else:
        return s


def _del(x, s):
    ""
    if s == E:
        return E
    # this clause not in Haskell
    if s == EE:
        return EE
    if s.right == E:
        if s.left == E:
            if s.color == R:
                return E if x == s.datum else T(R, E, s.datum, E)
            if s.color == B:
                return EE if x == s.datum else T(B, E, s.datum, E)
        if s.left.color == R and s.left.left == E and s.left.right == E:
            return (T(B, _del(x, T(R, E, s.left.datum, E)), s.datum, E)
                    if x < s.datum else
                    T(B, E, s.left.datum, E) if x == s.datum else
                    T(B, T(R, E, s.left.datum, E), s.datum, E))

    return (rotate(s.color, _del(x, s.left), s.datum, s.right) if x < s.datum else
            rotate(s.color, s.left, *_min_del(s.right)) if x == s.datum else
            rotate(s.color, s.left, s.datum, _del(x, s.right)))

        

# APPENDIX: Structural pattern matching version of above code matching Haskell
# in references. Tested this originally and refactored for performance.

# def _blacken_old(x, t):
#     """
#     In the haskell, _blacken is inside a closure with a given x.

#     _blacken (T R (T R a x b) y c) = T B (T R a x b) y c
#     _blacken (T R a x (T R b y c)) = T B a x (T R b y c)
#     _blacken t = t
#     """
#     match t:
#         case T(color=Color.R, left=T(color=Color.R, left=a, key=key, right=b),
#                key=y, right=c) if key == x:
#             return T(B, T(R, a, x, b), y, c)
#         case T(color=Color.R, left=a, key=key,
#                right=T(color=Color.R, left=b, key=y, right=c)) if key == x:
#             return T(B, a, x, T(R, b, y, c))
#         case _:
#             return t



# def _balance_old(color, left, key, right):
#     """
#     _balance B (T R (T R a x b) y c) z d = T R (T B a x b) y (T B c z d)
#     _balance B (T R a x (T R b y c)) z d = T R (T B a x b) y (T B c z d)
#     _balance B a x (T R (T R b y c) z d) = T R (T B a x b) y (T B c z d)
#     _balance B a x (T R b y (T R c z d)) = T R (T B a x b) y (T B c z d)
#     _balance BB a x (T R (T R b y c) z d) = T B (T B a x b) y (T B c z d)
#     _balance BB (T R a x (T R b y c)) z d = T B (T B a x b) y (T B c z d)
#     _balance color a x b = T color a x b
#     """
#     ##print(f"balance {color} {left} {key} {right}")
#     match color, left, key, right:
#         case (Color.B, T(color=Color.R,
#                          left=T(color=Color.R, left=a, key=x, right=b),
#                          key=y, right=c), z, d):
#             result = T(R, T(B, a, x, b), y, T(B, c, z, d))
#         case (Color.B, T(color=Color.R, left=a, key=x,
#                          right=T(color=Color.R, left=b, key=y, right=c)), z, d):
#             result = T(R, T(B, a, x, b), y, T(B, c, z, d))
#         case (Color.B, a, x, T(color=Color.R,
#                                left=T(color=Color.R, left=b, key=y, right=c),
#                                key=z, right=d)):
#             result = T(R, T(B, a, x, b), y, T(B, c, z, d))
#         case (Color.B, a, x, T(color=Color.R, left=b, key=y,
#                          right=T(color=Color.R, left=c, key=z, right=d))):
#             result = T(R, T(B, a, x, b), y, T(B, c, z, d))
#         case (Color.BB, a, x, T(color=Color.R,
#                                 left=T(color=Color.R, left=b, key=y, right=c),
#                                 key=z, right=d)):
#             result = T(B, T(B, a, x, b), y, T(B, c, z, d))
#         case (Color.BB, T(color=Color.R, left=a, key=x,
#                           right=T(color=Color.R, left=b, key=y, right=c)),
#               z, d):
#             result = T(B, T(B, a, x, b), y, T(B, c, z, d))
#         case color, a, x, b:
#             result = T(color, a, x, b)

#     ##print(f"balance result {result}")
#     return result


# def _ins_old(x, s):
#     """
#     In the haskell, _ins is a closure with a fixed x.
    
#     _ins E = T R E x E
#     _ins (T color a y b) | x < y = _balance color (ins a) y b
#                         | x == y = T color a y b
#                         | x > y = _balance color a y (ins b)
#     """
#     match s:
#         case EmptyRBNode.E:
#             result = T(R, E, x, E)
#         case T(color=color, left=a, key=y, right=b) if x < y:
#             result = _balance(color, _ins(x, a), y, b)
#         case T(color=color, left=a, key=y, right=b) if x == y:
#             result = T(color, a, y, b)
#         case T(color=color, left=a, key=y, right=b) if x > y:
#             result = _balance(color, a, y, _ins(x, b))

#     return result


# def _min_del_old(s):
#     """
#     _min_del (T R E x E) = (x,E)
#     _min_del (T B E x E) = (x,EE)
#     _min_del (T B E x (T R E y E)) = (x,T B E y E)
#     _min_del (T c a x b) = let (x’,a’) = _min_del a
#                             in (x’,rotate c a’ x b)
#     """
#     ##print(f"_min_del {s}")
#     match s:
#         case T(color=Color.R, left=EmptyRBNode.E, key=x, right=EmptyRBNode.E):
#             result = x, E
#         case T(color=Color.B, left=EmptyRBNode.E, key=x, right=EmptyRBNode.E):
#             result = x, EE
#         case T(color=Color.B, left=EmptyRBNode.E, key=x,
#                right=T(color=Color.R, left=EmptyRBNode.E, key=y,
#                        right=EmptyRBNode.E)):
#             result = x, T(B, E, y, E)
#         case T(color=c, left=a, key=x, right=b):
#             xp, ap = _min_del(a)
#             result = xp, rotate(c, ap, x, b)

#     ##print(f"_min_del result {result}")
#     return result


# def rotate_old(color, left, key, right):
#     ##print(f"rotate {color} {left} {key} {right}")
#     """
#     rotate R (T BB a x b) y (T B c z d) = _balance B (T R (T B a x b) y c) z d
#     rotate R EE y (T B c z d) = _balance B (T R E y c) z d
#     rotate R (T B a x b) y (T BB c z d) = _balance B a x (T R b y (T B c z d))
#     rotate R (T B a x b) y EE = _balance B a x (T R b y E)
#     rotate B (T BB a x b) y (T B c z d) = _balance BB (T R (T B a x b) y c) z d
#     rotate B EE y (T B c z d) = _balance BB (T R E y c) z d
#     rotate B (T B a x b) y (T BB c z d) = _balance BB a x (T R b y (T B c z d))
#     rotate B (T B a x b) y EE = _balance BB a x (T R b y E)
#     rotate B (T BB a w b) x (T R (T B c y d) z e) =
#         T B (balance B (T R (T B a w b) x c) y d) z e
#     rotate B EE x (T R (T B c y d) z e) = T B (balance B (T R E x c) y d) z e
#     rotate B (T R a w (T B b x c)) y (T BB d z e) =
#         T B a w (balance B b x (T R c y (T B d z e)))

#     rotate B (T R a w (T B b x c)) y EE = T B a w (balance B b x (T R c y E))
#     rotate color a x b = T color a x b
#     """
#     global B, BB   # Why is this necessary???
#     match color, left, key, right:
#         case (Color.R, T(color=Color.BB, left=a, key=x, right=b), y,
#               T(color=Color.B, left=c, key=z, right=d)):
#             result = _balance(B, T(R, T(B, a, x, b), y, c), z, d)
#         case (Color.R, EmptyRBNode.EE, y,
#               T(color=Color.B, left=c, key=z, right=d)):
#             result = _balance(B, T(R, E, y, c), z, d)
#         case (Color.R, T(color=Color.B, left=a, key=x, right=b), y,
#               T(color=Color.BB, left=c, key=z, right=d)):
#             result = _balance(B, a, x, T(R, b, y, T(B, c, z, d)))
#         case (Color.R, T(color=Color.B, left=a, key=x, right=b),
#               y, EmptyRBNode.EE):
#             result = _balance(B, a, x, T(R, b, y, E))
#         case (Color.B, T(color=Color.BB, left=a, key=x, right=b), y,
#               T(color=Color.B, left=c, key=z, right=d)):
#             result = _balance(BB, T(R, T(B, a, x, b), y, c), z, d)
#         case (Color.B, EmptyRBNode.EE, y,
#               T(color=Color.B, left=c, key=z, right=d)):
#             result = _balance(BB, T(R, E, y, c), z, d)
#         case (Color.B, T(color=Color.B, left=a, key=x, right=b), y,
#               T(color=Color.BB, left=c, key=z, right=d)):
#             result = _balance(BB, a, x, T(R, b, y, T(B, c, z, d)))
#         case (Color.B, T(color=Color.B, left=a, key=x, right=b),
#               y, EmptyRBNode.EE):
#             result = _balance(BB, a, x, T(R, b, y, E))
#         case (Color.B, T(color=Color.BB, left=a, key=w, right=b), x,
#               T(color=Color.R, left=T(color=Color.B, left=c, key=y, right=d),
#                 key=z, right=e)):
#             result = T(B, _balance(B, T(R, T(B, a, w, b), x, c), y, d), z, e)
#         case (Color.B, EmptyRBNode.EE, x,
#               T(color=Color.R, left=T(color=Color.B, left=c, key=y, right=d),
#                 key=z, right=e)):
#             result = T(B, _balance(B, T(R, E, x, c), y, d), z, e)
#         case (Color.B, T(color=Color.R, left=a, key=w,
#                          right=T(color=Color.B, left=b, key=x, right=c)),
#               y, T(color=Color.BB, left=d, key=z, right=e)):
#             result = T(B, a, w, _balance(B, b, x, T(R, c, y, T(B, d, z, e))))
#         case (Color.B, T(color=Color.R, left=a, key=w,
#                          right=T(color=Color.B, left=b, key=x, right=c)),
#               y, EmptyRBNode.EE):
#             result = T(B, a, w, _balance(B, b, x, T(R, c, y, E)))
#         case color, a, x, b:
#             result = T(color, a, x, b)

#     ##print(f"rotate result {result}")
#     return result


# def _redden_old(x, s):
#     """
#     _Redden has a closure captured x in the Haskell.
    
#     _redden (T B (T B a x b) y (T B c z d)) =
#         T R (T B a x b) y (T B c z d)
#     _redden t = t
#     """
#     match s:
#         case T(color=Color.B, left=T(color=Color.B, left=a, key=key, right=b),
#                key=y, right=T(color=Color.B, left=c, key=z, right=d)
#         ) if key == x:
#             return T(R, T(B, a, x, b), y, T(B, c, z, d))
#         case t:
#             return t


# def _del_old(x, s):
#     """
#     del has a closure captured x in the Haskell.
    
#     del E = E
#     del (T R E y E) | x == y = E
#                     | x /= y = T R E y E
#     del (T B E y E) | x == y = EE
#                     | x /= y = T B E y E
#     del (T B (T R E y E) z E) | x < z = T B (del (T R E y E)) z E
#                               | x == z = T B E y E
#                               | x > z = T B (T R E y E) z E
#     del (T c a y b) | x < y = rotate c (del a) y b
#                     | x == y = let (y’,b’) = _min_del b
#                                  in rotate c a y’ b’
#                     | x > y = rotate c a y (del b)
#     """
#     ##print(f"_del {x} from {s}")
#     match s:
#         case EmptyRBNode.E:
#             result = E
#         case T(color=Color.R, left=EmptyRBNode.E, key=y, right=EmptyRBNode.E
#         ) if x == y:
#             result = E
#         case T(color=Color.R, left=EmptyRBNode.E, key=y, right=EmptyRBNode.E
#         ) if x != y:
#             result = T(R, E, y, E)
#         case T(color=Color.B, left=EmptyRBNode.E, key=y, right=EmptyRBNode.E
#         ) if x == y:
#             result = EE
#         case T(color=Color.B, left=EmptyRBNode.E, key=y, right=EmptyRBNode.E
#         ) if x != y:
#             result = T(B, E, y, E)
#         case T(color=Color.B, left=T(color=Color.R, left=EmptyRBNode.E,
#                                      key=y, right=EmptyRBNode.E),
#                key=z, right=EmptyRBNode.E) if x < z:
#             result = T(B, _del(x, T(R, E, y, E)), z, E)
#         case T(color=Color.B, left=T(color=Color.R, left=EmptyRBNode.E,
#                                      key=y, right=EmptyRBNode.E),
#                key=z, right=EmptyRBNode.E) if x == z:
#             result = T(B, E, y, E)
#         case T(color=Color.B, left=T(color=Color.R, left=EmptyRBNode.E,
#                                      key=y, right=EmptyRBNode.E),
#                key=z, right=EmptyRBNode.E) if x > z:
#             result = T(B, T(R, E, y, E), z, E)
#         case T(c, a, y, b) if x < y:
#             result = rotate(c, _del(x, a), y, b)
#         case T(c, a, y, b) if x == y:
#             result = rotate(c, a, *_min_del(b))
#         case T(c, a, y, b) if x > y:
#             result = rotate(c, a, y, _del(x, b))

#     ##print(f"_del result {result}")
#     return result


