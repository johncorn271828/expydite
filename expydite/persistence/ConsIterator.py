"""
"""
from expydite.persistence.ConsCell import ConsCell

class ConsIterator():
    """
    A pointer that walks the linked list.
    TODO: Should this check for circular lists? Just keep going?
    """
    __slots__ = ["_head"]

    def __init__(self, cons_list):
        """
        The iterator is a list pointer initialized to head.
        Start on a copy of head to avoid advancing cons_list pointer itself.
        """
        self._head = ConsCell(cons_list._head.car(), cons_list._head.cdr())

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
        if self._head.car() is None and self._head.cdr() is None:
            raise StopIteration
        result = self._head.car()
        if self._head.cdr() is not None:
            self._head.rplaca(self._head.cdr().car())
            self._head.rplacd(self._head.cdr().cdr())
        else:
            self._head.rplaca(None)
            self._head.rplacd(None)

        return result
