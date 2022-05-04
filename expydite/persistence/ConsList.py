"""

"""
from math import ceil
from copy import deepcopy
from collections.abc import MutableSequence, Iterable

from expydite.persistence.ConsCell import ConsCell
from expydite.persistence.ConsIterator import ConsIterator


CONS_CELL_TYPE = type(ConsCell())  # AutoProxy[ConsCell] or something dynamic


class ConsList(MutableSequence):
    """
    A pointer to a persistent ConsCell in shared memory.
    Dunder methods implement the MutableSequence interface.
    These objects are persistent, ie updates to an instance in one process do
    not affect references to that instance for other processes.
    """
    __slots__ = ["_head", "_length"]
    
    def __init__(self, initializer=None, length=None):
        """
        Initialize head pointer to given ConsCell, or construct some from
        iterable.
        """
        if initializer is None:
            self._head = None
            self._length = 0
        elif isinstance(initializer, CONS_CELL_TYPE):
            self._head = initializer
            if isinstance(length, int):
                self._length = length
            else:
                self._compute_length()
        elif isinstance(initializer, Iterable):
            self._make_shared_cons_cells(initializer)
        else:
            raise ValueError(
                f"Cannot construct ConsList from {type(initializer)}")

    def __str__(self):
        result = "("
        node = self._head
        while node is not None:
            result += str(node.car()) + " "
            node = node.cdr()
        if len(result) == 1:
            result += ")"
        else:
            result = result[:-1] + ")"

        return result

    __repr__ = __str__
    
    def __eq__(self, other):
        """
        Avoid recursing on cdr to ensure O(1) memory
        """
        if self._length != other._length:
            result = False
        else:  # Walk _head
            result = True
            node = self._head
            other_node = other._head
            while node is not None:
                # ConsCell does not equal a non-ConsCell
                if type(node) != type(other_node):
                    result = False
                    break
                # Given two ConsCells, compare their cars
                elif node.car() != other_node.car():
                    result = False
                    break
                node = node.cdr()
                other_node = other_node.cdr()
            if other_node is not None:
                result = False

        return result

    def __bool__(self):
        return (isinstance(self._head, CONS_CELL_TYPE) and
                (self._head.car() is not None or
                 self._head.cdr() is not None))
    
    def __copy__(self): return self._copy()
    
    def __deepcopy__(self, memodict=dict()): return self._copy(deep=True)

    def __add__(self, other):
        write_node = ConsCell()
        previous = None
        result = write_node
        result_length = 0
        node = self._head
        while node is not None:
            write_node.rplaca(node.car())
            write_node.rplacd(ConsCell())
            result_length += 1
            previous = write_node
            write_node = write_node.cdr()
            node = node.cdr()
        if previous is None:  # self was empty
            result = other._head
        else:
            previous.rplacd(other._head)  # No need to copy other
            result_length += other._length

        return ConsList(initializer=result, length=result_length)

    # Sequence methods
    def __getitem__(self, index):
        # Deal with negative indices without walking backwards
        negative_step, index = self._denegative_slice(index)
                
        # index is an int. return the value
        if isinstance(index, int):
            if index > self._length:
                raise IndexError("Cons index out of range")
            node = self._head
            i = 0
            while node is not None:
                if i == index:
                    result = node.car()
                    break
                node = node.cdr()
                i += 1
            # Case of index > len(self)  ?
            if node is None:
                raise IndexError("Cons index out of range")
        # index gets whole thing. return reference without copying
        elif not index.start and index.step is None and index.stop is None:
            result = self
        # index gets tail. return the tail without copying
        elif index.step is None and index.stop is None:
            if index.start > self._length:
                raise IndexError("Cons index out of range")
            result = None
            node = self._head
            i = 0
            while node is not None:
                if i == index.start:
                    result = ConsList(node)
                    break
                node = node.cdr()
                i += 1
            if result is None:  # how?
                raise IndexError("Cons index out of range")
        # Otherwise, make a copy on the slice
        else:
            result = ConsCell()
            write_node = result
            previous = None
            node = self._head
            i = 0
            while node is not None:
                if ConsList._on_slice(i, index, negative_step):
                    write_node.rplaca(node.car())
                    write_node.rplacd(ConsCell())
                    previous = write_node
                    write_node = write_node.cdr()
                node = node.cdr()
                i += 1
            if previous is not None:
                previous.rplacd(None)
            result = ConsList(result)

        if negative_step:
            result = reversed(result)

        return result
        
    def __len__(self): return self._length

    def __contains__(self, value):
        result = False
        node = self._head
        while node is not None:
            if node.car() == value:
                result = True
                break
            node = node.cdr()
            
        return result
    
    def __iter__(self): return ConsIterator(self)

    def __reversed__(self):
        result = None
        node = self._head
        while node is not None:
            result = ConsCell(node.car(), result)
            node = node.cdr()

        return ConsList(result)

    def index(self, value):
        result = None
        i = 0
        node = self._head
        while node is not None:
            if node.car() == value:
                result = i
                break
            node = node.cdr()
            i += 1
        if result is None:
            raise ValueError(f"{value} is not in Cons")

        return result

    def count(self, value):
        result = 0
        node = self._head
        while node is not None:
            if node.car() == value:
                result += 1
            node = node.cdr()

        return result

    # MutableSequence methods
    def __setitem__(self, index, value):
        """
        Copy ConsCells from self._head except for those with indices on the
        slice index, which are replaced by successive elements from value.
        Recycle the tail of self once the end of the slice is reached.
        """
        negative_step, index = self._denegative_slice(index)
        if isinstance(index, int):
            index = slice(index, index + 1, None)
            value = [value]
        if index.start > self._length:
            raise IndexError("Cons index out of range")
        # Check length of value vs length of slice?
        seq_top = index.stop if index.stop is not None else self._length
        seq_bottom = index.start if index.start is not None else 0
        seq_size = abs(ceil((seq_top - seq_bottom) /
                           (1 if index.step is None else index.step)))
        stop_index = max(seq_top, seq_bottom) + 1
        value_length = len(value)
        if value_length > seq_size:
            raise ValueError(
                f"attempt to assign sequence of size {value_length} " +
                f"to extended slice of size {seq_size}")
        if negative_step:
            value = reversed(value)
        # The plan: copy from self except when on slice, then take from value.
        # Assign tail pointer at the end
        write_node = ConsCell()
        previous = None
        result = write_node
        node = self._head
        i = 0
        iterator = iter(value)
        while node is not None:
            if i == stop_index:
                break
            if ConsList._on_slice(i, index, negative_step):
                try:
                    val = next(iterator)
                except StopIteration:
                    raise ValueError(
                        f"attempt to assign sequence of size {value_length} " +
                        f"to extended slice of size {seq_size}")
                write_node.rplaca(val)
            else:
                write_node.rplaca(node.car())
            write_node.rplacd(ConsCell())
            previous = write_node
            write_node = write_node.cdr()
            node = node.cdr()
            i += 1
        if node is None:
            previous.rplacd(None)
        else:
            write_node.rplaca(node.car())
            write_node.rplacd(node.cdr())  # Recycle tail of list
        self._head = result

        return
        
    def __delitem__(self, index):
        """
        """
        negative_step, index = self._denegative_slice(index)
        if isinstance(index, int):
            index = slice(index, index + 1, None)
        if index.start > self._length:
            raise IndexError("Cons index out of range")
        seq_top = index.stop if index.stop is not None else self._length
        seq_bottom = index.start if index.start is not None else 0
        seq_size = abs(ceil((seq_top - seq_bottom) /
                           (1 if index.step is None else index.step)))
        stop_index = max(seq_top, seq_bottom)
        # Plan: Copy list except where on slice, recycle tail of list.
        # Use arithmetic to determine new length to avoid iterating tail
        write_node = ConsCell()
        result = write_node
        previous = write_node
        node = self._head
        i = 0
        while node is not None:
            if i == stop_index:
                break
            if not ConsList._on_slice(i, index, negative_step):
                write_node.rplaca(node.car())
                write_node.rplacd(ConsCell())
                previous = write_node
                write_node = write_node.cdr()
            node = node.cdr()
            i += 1
        if node is None:  # Slice reached end of list, it's all a copy
            previous.rplacd(None)
        else:
            write_node.rplaca(node.car())
            write_node.rplacd(node.cdr())
        self._head = result if result else None
        self._length -= seq_size

        return

    def insert(self, index, value):
        write_node = ConsCell()
        result = write_node
        node = self._head
        i = 0
        while node is not None:
            if i == index:
                write_node.rplaca(value)
                break
            else:
                write_node.rplaca(node.car())
                write_node.rplacd(ConsCell())
            write_node = write_node.cdr()
            node = node.cdr()
            i += 1
        write_node.rplacd(node)
        self._head = result
        self._length += 1

        return
        
    def append(self, value):
        result = ConsCell(value, self._head)
        self._head = result
        self._length += 1

    def reverse(self):
        result = reversed(self)
        self._head = result._head

    def extend(self, other):
        if type(other) != type(self):
            raise NotImplementedError()
        node = self._head
        write_node = ConsCell()
        previous = None
        result = write_node
        while node is not None:
            write_node.rplaca(node.car())
            write_node.rplacd(ConsCell())
            node = node.cdr()
            previous = write_node
            write_node = write_node.cdr()
        if previous is not None:
            previous.rplacd(other._head)  # recycle other
        self._head = result
        self._length += other._length

    def pop(self, index=0):
        if index >= self._length:
            raise IndexError("Cons index out of range")
        node = self._head
        write_node = ConsCell()
        previous = None
        new_head = write_node
        i = 0
        while node is not None:
            if i == index and i == 0:
                result = node.car()
                new_head = node.cdr()
                break
            elif i == index and i != 0:
                result = node.car()
                previous.rplacd(node.cdr())
                break
            write_node.rplaca(node.car())
            write_node.rplacd(ConsCell())
            node = node.cdr()
            previous = write_node
            write_node = write_node.cdr()
            i += 1
        if node is None:
            raise IndexError("Cons index out of range")
        self._head = new_head
        self._length -= 1

        return result

    def remove(self, value):
        if self._head.car() == value:
            new_head = self._head.cdr()
        else:
            node = self._head
            write_node = ConsCell()
            previous = None
            new_head = write_node
            while node is not None:
                if node.car() == value:
                    previous.rplacd(node.cdr())
                    break
                write_node.rplaca(node.car())
                write_node.rplacd(ConsCell())
                node = node.cdr()
                previous = write_node
                write_node = write_node.cdr()
            if node is None:
                raise ValueError("ConsList.remove(x): x not in ConsList")
        self._head = new_head
        self._length -= 1        

    def __iadd__(self, other):
        result = self + other
        self._head = result._head
        self._length = result._length

        return self

    # Private helper methods
    def _compute_length(self):
        node = self._head
        self._length = 0
        while node is not None:
            self._length += 1
            node = node.cdr()
    
    @staticmethod
    def _on_slice(i, slc, negative_step):
        """
        Index arithmetic to deal with slices without iterating backwards O(n^2)
        """
        if negative_step:
            between_bounds = lambda n : (
                (slc.start is None or n > slc.start) and
                (slc.stop is None or n <= slc.stop))
        else:
            between_bounds = lambda n : (
                (slc.start is None or n >= slc.start) and
                (slc.stop is None or n < slc.stop))
        on_steps = lambda n: (
            (slc.step is None) or
            (slc.step > 0 and (n - slc.start) % slc.step == 0) or
            (slc.step < 0 and (slc.stop - n) % slc.step == 0))
        
        return between_bounds(i) and on_steps(i)


    def _denegative_slice(self, index):
        """
        Convert slices with negative indexes to positive using arithmetic and
        __len__. Flag negative step values.
        """
        negative_step = False
        if isinstance(index, int):
            if index < 0:
                length = len(self)
                if abs(index) > length:
                    raise IndexError("Cons index out of range")
                index = len(self) + index
        elif isinstance(index, slice):
            length = None
            if index.start is not None and index.start < 0:
                length = len(self) if length is None else length
                if abs(index.start) > length:
                    raise IndexError("Cons index out of range")
                index = slice(length + index.start, index.stop, index.step)
            if index.stop is not None and index.stop < 0:
                length = len(self) if length is None else length
                index = slice(index.start, length + index.stop, index.step)
            if index.step is not None and index.step < 0:
                negative_step = True
                # Swap start and stop to use index arithmetic and not need to
                # iterate backwards down singly linked list.
                index = slice(index.stop, index.start, index.step)

        return negative_step, index
    
    def _copy(self, deep=False):
        copy_head = ConsCell()
        write_cons = copy_head  # write location
        previous = None
        node = self._head
        while node is not None:
            write_cons.rplaca(deepcopy(node.car())
                              if deep else node.car())

            write_cons.rplacd(ConsCell())
            previous = write_cons
            write_cons = write_cons.cdr()
            node = node.cdr()
        # End list with None instead of empty ConsCell
        if previous is not None:
            previous.rplacd(None) 

        return ConsList(copy_head)
    
    def _make_shared_cons_cells(self, iterable):
        self._head = ConsCell()
        self._length = 0
        if iterable is not None:
            node = self._head
            previous = None
            for value in iterable:
                previous = node
                node.rplacd(ConsCell())
                node.rplaca(value)
                node = node.cdr()
                self._length += 1
            if previous is None:
                self._head = None
            else:
                previous.rplacd(None)

