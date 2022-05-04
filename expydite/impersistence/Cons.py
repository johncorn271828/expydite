"""
Provides an implementation of cons cells like Lisp's.
TODO: try @nuitka on class members, or move members into nuitka-ed module vars
TODO? generator
TODO? __mul__, __imul__, __rmul__ like deque
TODO? appendright, extendleft, popright analogous to deque
TODO? rotate like deque
TODO: support for circular lists
TODO: Is this ok? Google "python __str__ vs __repr__"
TODO: check that this is the correct behavior of reversed(mycons)

"""
from copy import copy, deepcopy
from collections.abc import MutableSet


class ConsIterator():
    """
    A pointer that walks the linked list.
    TODO: Should this check for circular lists? Just keep going?
    """
    __slots__ = ["_car", "_cdr"]

    def __init__(self, start_node):
        """
        The iterator is a list pointer initialized to head.
        """
        self._car = getattr(start_node, "_car", None)
        self._cdr = getattr(start_node, "_cdr", None)

    def __iter__(self):
        """
        Avoid "ConsIterator is not iterable" error
        """
        return self

    def __next__(self):
        """
        Move the pointer to its cdr and return the old car.
        Raise StopIteration at the end of the list.
        """
        if self._car is None and self._cdr is None:
            raise StopIteration
        result = self._car
        self._car = getattr(getattr(self, "_cdr", None), "_car", None)
        self._cdr = getattr(getattr(self, "_cdr", None), "_cdr", None)

        return result


class Cons(MutableSet):
    """
    MutableSet is the best choice for getting free mixin implementations.
    Within this class say type(self)() instead of
    just "Cons()" so that other classes can borrow methods directly and
    instantiate the right stuff therein.
    """
    __slots__ = ["_car", "_cdr"]

    def __init__(self, iterable=None):
        """
        Matches other python collection constructors, not lisp function cons.
        No argument constructor does NOT initialize slots.
        """
        if iterable is not None:
            node = self
            previous = None
            for value in iterable:
                previous = node
                node._cdr = type(self)()
                node._car = value
                node = node._cdr
            if previous is not None:
                previous._cdr = None

    def __str__(self):
        """
        List representation of a cons list to match that of lisp.
        """
        result = "("
        node = self
        while node is not None:
            result += str(node._car) + " "
            node = node._cdr
        if len(result) == 1:
            result += ")"
        else:
            result = result[:-1] + ")"

        return result

    def __repr__(self):
        """
        Same as __str__ to make debugging in pytest easier. 
        """
        return self.__str__()

    def __eq__(self, other):
        """
        Implements == 
        """
        node = self
        other_node = other
        result = True
        while node is not None:
            # Other data types in cdr, delegate to their __eq__
            if (not isinstance(node, Cons) and
                not isinstance(other_node, Cons) and
                node != other_node):
                result = False
                break
            # A Cons never equals a not-Cons
            if isinstance(node, Cons) ^ isinstance(other_node, Cons):
                result = False
                break
            # Node and other node are Cons. Compare _cars. (Recursion here)
            if (getattr(node, "_car", None) !=
                getattr(other_node, "_car", None)):
                result = False
                break
            node = getattr(node, "_cdr", None)
            other_node = getattr(other_node, "_cdr", None)
        if other_node is not None:  # self is prefix of other
            result = False

        return result

    def __bool__(self):
        """
        Probably faster to use "while node is not None" instead of "while node"
        """
        return (getattr(self, "_car", None) is not None or
                getattr(self, "_cdr", None) is not None)

    def __contains__(self, value):
        """
        Implements in keyword
        """
        node = self
        result = False
        while node:
            if node._car == value:
                result = True
                break
            node = node._cdr

        return result

    def __iter__(self):
        """
        This iterator is needed to avoid keeping a "head" pointer to revert
        to after the iteration is complete.
        """
        return ConsIterator(self)

    def reverse(self):
        """
        Imperatively reverse self in place.
        """
        # Start on a copy of the head to avoid a circular list
        node = type(self)()
        node._car = getattr(self, "_car", None)
        node._cdr = getattr(self, "_cdr", None)
        # Walk across list reversing pointers
        previous = None
        while node:
            next_node = node._cdr
            node._cdr = previous
            previous = node
            node = next_node
        # Make the old tail the new head
        if previous is not None:
            self._car = previous._car
            self._cdr = previous._cdr

    def _copy(self, deep=False):
        """
        Helper function constructs copy of list by consing.
        """
        result = type(self)()
        node = self
        while node:
            head = type(self)()
            head._car = deepcopy(node._car) if deep else node._car
            head._cdr = result
            result = head
            node = node._cdr
        result.reverse()

        return result

    def __copy__(self):
        """
        Copy cons one layer deep
        """
        return self._copy()

    def __deepcopy__(self, memodict=dict()):
        """
        Copy Cons all the way down
        """
        return self._copy(deep=True)

    def __reversed__(self):
        """
        """
        reversed_copy = copy(self)
        reversed_copy.reverse()
        
        return iter(reversed_copy)

    def __len__(self):
        """
        Implements len(mycons)
        """
        node = self
        length = 0
        while node:
            length += 1
            node = node._cdr

        return length

    def index(self, value):
        """
        Finds index of first occurrence of value.
        Implement this to prevent mixin implementation using __getitem__
        """
        node = self
        i = 0
        while node:
            if node._car == value:
                return i
            node = node._cdr
            i += 1
        raise ValueError(f"{value} is not in Cons")

    def count(self, value):
        """
        Counts instances of value.
        Implement this to prevent mixin implementation using __getitem__
        """
        node = self
        count = 0
        while node:
            if node._car == value:
                count += 1
            node = node._cdr

        return count

    @staticmethod
    def _on_slice(index, islice, negative_step):
        """
        Index arithmetic to deal with slices without counting backwards etc.
        """
        if negative_step:
            between_bounds = lambda i : (
                (islice.start is None or i > islice.start) and
                (islice.stop is None or i <= islice.stop))
        else:
            between_bounds = lambda i : (
                (islice.start is None or i >= islice.start) and
                (islice.stop is None or i < islice.stop))
        on_steps = lambda i: (
            (islice.step is None) or
            (islice.step > 0 and (i - islice.start) % islice.step == 0) or
            (islice.step < 0 and (islice.stop - i) % islice.step == 0))
        
        return between_bounds(index) and on_steps(index)


    def _denegative_slice(self, islice):
        """
        Convert slices with negative indexes to positive using arithmetic and
        __len__. Flag negative step values.
        """
        negative_step = False
        if isinstance(islice, int):
            if islice < 0:
                length = len(self)
                if abs(islice) > length:
                    raise IndexError("Cons index out of range")
                islice = len(self) + islice
        elif isinstance(islice, slice):
            length = None
            if islice.start is not None and islice.start < 0:
                length = len(self) if length is None else length
                if abs(islice.start) > length:
                    raise IndexError("Cons index out of range")
                islice = slice(length + islice.start, islice.stop, islice.step)
            if islice.stop is not None and islice.stop < 0:
                length = len(self) if length is None else length
                islice = slice(islice.start, length + islice.stop, islice.step)
            if islice.step is not None and islice.step < 0:
                negative_step = True
                # Swap start and stop to use index arithmetic and not need to
                # iterate backwards down singly linked list.
                islice = slice(islice.stop, islice.start, islice.step)

        return negative_step, islice

    def __getitem__(self, islice):
        """
        Get a Cons of the elements on slice.
        If islice is the tail, return the appropriate pointer without copying.
        """
        # Deal with negative indices without walking backwards
        negative_step, islice = self._denegative_slice(islice)
                
        # islice is an int. return the value
        if isinstance(islice, int):
            node = self
            i = 0
            while node is not None:
                if i == islice:
                    result = node._car
                    break
                node = node._cdr
                i += 1
            # Case of islice > len(self)
            if node is None:
                raise IndexError("Cons index out of range")
        # islice gets whole thing. return reference without copying
        elif not islice.start and islice.step is None and islice.stop is None:
            result = self
        # islice gets tail. return the tail without copying
        elif islice.step is None and islice.stop is None:
            result = type(self)()
            node = self
            i = 0
            while node is not None:
                if i == islice.start:
                    result = node
                    break
                node = node._cdr
                i += 1
        # Otherwise, make a copy on the slice
        else:
            result = None
            node = self
            i = 0
            while node is not None:
                if Cons._on_slice(i, islice, negative_step):
                    head = type(self)()
                    head._car = node._car
                    head._cdr = result
                    result = head
                node = node._cdr
                i += 1
            if result is None:
                result = type(self)()
            else:
                result.reverse()

        # O(2n) still better than O(n^2)
        if negative_step:
            result.reverse()

        return result

    def __setitem__(self, islice, value):
        """
        Bracket assignment optimized for slices on the tail and middle
        """
        # Deal with negative indices without walking backwards
        negative_step, islice = self._denegative_slice(islice)
                
        # Integer islice so replace one value and quit
        if isinstance(islice, int):
            node = self
            i = 0
            while node is not None:
                if i == islice:
                    node._car = value
                    break
                node = node._cdr
                i += 1
        # Assigning the tail of a Cons to another Cons.
        # Move the pointer to value and done
        elif (isinstance(value, Cons) and islice.stop is None and
              (islice.step is None or islice.step == 1)):
            node = self
            i = 0
            while node is not None:
                if i == islice.start - 1:
                    break
                node = node._cdr
                i += 1
            node._cdr = value
        # Assigning the inside of a list.
        # Find start node and end node pointers, then splice in value
        elif (isinstance(value, Cons) and
              (islice.step is None or islice.step == 1)):
            node = self
            i = 0
            while node is not None:
                if i == islice.start - 1:
                    front = node
                if i == islice.stop:
                    back = node
                    break
                node = node._cdr
                i += 1
            front._cdr = value
            # Find end of value to point to back
            node = front
            while node is not None:
                if node._cdr is None:
                    break
                node = node._cdr
            node._cdr = back
        # Otherwise iterate over value and Cons its elements in on splice
        else:
            # Check length of value vs length of slice?
            seq_size = abs(int((islice.stop + 1 - islice.start) /
                               (1 if islice.step is None else islice.step)))
            value_length = len(value)
            if value_length > seq_size:
                raise ValueError(
                    f"attempt to assign sequence of size {value_length} " +
                    f"to extended slice of size {seq_size}")
            # Use index arithmetic to avoid walking backwards
            node = self
            previous = None
            i = 0
            if negative_step:
                value = reversed(value)
            iterator = iter(value)
            while node is not None:
                if Cons._on_slice(i, islice, negative_step):
                    try:
                        node._car = next(iterator)
                        previous = node
                    except StopIteration:  # Done pushing values, delete slice
                        # assign empty value to slice ending at 0...?
                        if previous is None: 
                            break 
                        previous._cdr = node._cdr
                node = node._cdr
                i += 1

    def __delitem__(self, islice):
        """
        del keyword optimized to remove tail without slice arithmetic
        """
        # Deal with negative indices without walking backwards
        negative_step, islice = self._denegative_slice(islice)
                
        # Integer islice so replace one value and quit
        if isinstance(islice, int):
            node = self
            previous = None
            i = 0
            while node is not None:
                if i == islice and i == 0:
                    self._car = self._cdr._car
                    self._cdr = self._cdr._cdr
                    break
                elif i == islice:
                    previous._cdr = node._cdr
                    break
                previous = node
                node = node._cdr
                i += 1
        # Delete tail
        elif (isinstance(islice, slice) and
            (islice.step is None or islice.step == 1) and
            islice.stop is None):
            node = self
            previous = None
            i = 0
            while node is not None:
                if i == islice.start and i == 0:
                    self._car = None
                    self._cdr = None
                    break
                elif i == islice.start:
                    previous._cdr = None
                    break
                previous = node
                node = node._cdr
                i += 1
        # Delete general slice
        else:
            node = self
            previous = None
            i = 0
            while node is not None:
                if Cons._on_slice(i, islice, negative_step) and i == 0:
                    self._car = self._cdr._car
                    self._cdr = self._cdr._cdr
                elif Cons._on_slice(i, islice, negative_step):
                    previous._cdr = node._cdr
                else:
                    previous = node
                node = node._cdr
                i += 1

        return
                
    def insert(self, index, value):
        """
        Put the value into the Cons at index, scooting the rest to the right.
        """
        previous = None
        node = self
        i = 0
        while node is not None:
            if i == index and i == 0:
                patch = type(self)()
                patch._car = self._car
                patch._cdr = self._cdr
                self._cdr = patch
                self._car = value
                break
            elif i == index:
                patch = type(self)()
                patch._car = value
                patch._cdr = node
                previous._cdr = patch
                break
            previous = node
            node = node._cdr
            i += 1
        if node is None:
            raise IndexError("Cons index out of range")

    def append(self, value):
        """
        Append to the front in O(1) time
        """
        if not self:
            self._car = value
            self._cdr = None
        else:
            patch = type(self)()
            patch._car = self._car
            patch._cdr = self._cdr
            self._cdr = patch
            self._car = value

    def extend(self, iterable):
        """
        Imperatively add elements from iterable to the end of self.
        If iterable is also a Cons, just assign the last cdr
        """
        node = self
        while node._cdr is not None:
            node = node._cdr
        if isinstance(iterable, Cons):
            node._cdr = iterable
        else:
            for value in iterable:
                back = type(self)()
                back._cdr = None
                back._car = value
                node._cdr = back
                node = back

    def pop(self, index=0):
        """
        Remove the value from self at index, return it
        """
        if not self:
            raise IndexError("pop from empty Cons")
        if index == 0:
            result = self._car
            self._car = getattr(self._cdr, "_car", None)
            self._cdr = getattr(self._cdr, "_cdr", None)
        else:
            node = self
            previous = None
            i = 0
            while node is not None:
                if i == index:
                    result = node._car
                    previous._cdr = node._cdr
                    break
                previous = node
                node = node._cdr
                i += 1
            if node is None:
                raise IndexError("pop index out of range")

        return result

    def remove(self, value):
        """
        Remove the first element of value from self imperatively
        """
        if self._car == value:
            self._car = getattr(self._cdr, "_car", None)
            self._cdr = getattr(self._cdr, "_cdr", None)
        else:
            previous = None
            node = self
            while node is not None:
                if node._car == value:
                    previous._cdr = node._cdr
                    break
                previous = node
                node = node._cdr
            if node is None:
                raise ValueError("Cons.remove(x): x not in Cons")

    def __iadd__(self, other):
        """
        This is the += operator
        """
        self.extend(other)

        return self
    
    def add(self, value):
        """
        Make this behave like python set.
        """
        if value not in self:
            self.append(value)

    def discard(self, value):
        """
        Make this behave like python set, kinda. Remove all the value-s
        """
        previous = None
        node = self
        while node is not None:
            if node._car == value and previous is None:
                self._car = getattr(self._cdr, "_car", None)
                self._cdr = getattr(self._cdr, "_cdr", None)
            elif node._car == value:
                previous._cdr = node._cdr
                node = node._cdr
            else:
                previous = node
                node = node._cdr

    def __or__(self, other):
        """
        The automatic mixin implementation of this seems broken.
        """
        result = type(self)()
        for value in self:
            result.add(value)
        for value in other:
            result.add(value)

        return result

    def __ior___(self, other):
        """
        The automatic mixin implementation of this seems broken.
        Do it O(mn) to 
        """
        for value in other:
            self.add(value)

    def clear(self):
        """
        The automatic mixin implementation of this seems broken.
        """
        self._car = None
        self._cdr = None

    # For clarity of understanding (these are automatically inherited)
    __le__ = MutableSet.__le__
    __lt__ = MutableSet.__lt__
    __ne__ = MutableSet.__ne__
    __ge__ = MutableSet.__ge__
    __gt__ = MutableSet.__gt__
    __and__ = MutableSet.__and__
    __iand__ = MutableSet.__iand__
    __sub__ = MutableSet.__sub__
    __isub__ = MutableSet.__isub__
    isdisjoint = MutableSet.isdisjoint
