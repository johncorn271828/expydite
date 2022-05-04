"""
Data parallelism control flow functions.
"""
from functools import reduce
from itertools import chain
from multiprocessing import Pool, Manager, Process, Value
from multiprocessing.shared_memory import ShareableList
from math import ceil
from operator import add

import psutil


CPU_COUNT = psutil.cpu_count(logical=False)


def _pmap_builtin(func, *iterable, processes=CPU_COUNT):
    """
    Most obvious implementation of pmap.
    Why is this slower?
    """
    with Pool(processes) as pool:
        return pool.map(func, *iterable)


def pmap(func, *iterable, segments=CPU_COUNT, inplace=False, void_return=None):
    """
    Parallel map. inplace=True only makes sense when the iterable is shared
    memory, ie an instance of multiprocessing.shared_memory.ShareableList.
    """
    # Enable void return optimization based on type hints unless the caller
    # has set void_return=False
    void_annotation = (void_return is None and
                       getattr(func, "__annotations__", None) and
                       func.__annotations__.get("return", False) is None)

    return (map(func, *iterable) if segments == 1 else
            _pmap_void_return(func, *iterable, segments=segments)
            if void_return or void_annotation else
            _pmap_inplace(func, iterable[0], segments=segments)
            if (inplace and
                len(iterable) == 1 and
                isinstance(iterable[0], ShareableList)) else
            _pmap(func, *iterable, segments=segments))


def _pmap_void_return(func, *iterable, segments=CPU_COUNT):
    """
    Optimized implementation of pmap for func returning None.
    """
    # ceil rather than floor prevents a segment_ of size 1 at the end.
    segment_size = ceil(len(iterable[0]) / segments)
    processes = []
    def sublist_proc(segment):
        for i in range(segment_size):
            func(*segment[i])
    for i in range(segments):
        segs = tuple(iterable[j][i * segment_size : (i + 1) * segment_size]
                     for j in range(len(iterable)))
        process = Process(target=sublist_proc,  args=(segs,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()

    return


def _pmap_inplace(func, shareable_list, segments=CPU_COUNT):
    """
    Parallel map that modifies its argument, an instance of ShareableList.
    """
    def map_sublist_inplace(start, end):
        for i in range(start, end):
            shareable_list[i] = func(shareable_list[i])

    # ceil rather than floor prevents a segment_ of size 1 at the end.
    segment_size = ceil(len(shareable_list) / segments)
    processes = []
    for i in range(segments):
        start = i * segment_size
        #end = min((i + 1) * segment_size, len(shareable_list))
        end = (i + 1) * segment_size
        process = Process(target=map_sublist_inplace,
                    args=(start, end))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()

    return shareable_list


def _pmap(func, *iterable, segments=CPU_COUNT):
    """
    Data-parallel implementation of map.
    """
    # ceil rather than floor prevents a segment_ of size 1 at the end.
    segment_size = ceil(len(iterable[0]) / segments)
    processes = []
    return_dict = Manager().dict()
    def subseq_proc(subseqs, index, return_dict):
        return_dict[index] = list(map(func, *subseqs))
    iterators = [iter(iterable[j]) for j in range(len(iterable))]
    for i in range(segments):
        # O(segments) partitioning
        if hasattr(iterable[0], "__getitem__"):
            subseqs = tuple(iterable[j][i * segment_size :
                                        (i + 1) * segment_size]
                            for j in range(len(iterable)))
        else:  # O(len(iterable[0])) partitioning
            subseqs = tuple(
                [next(iterators[j]) for k in range(segment_size)]  # TODO iterator instead of list?
                for j in range(len(iterable)))
        process = Process(target=subseq_proc,
                          args=(subseqs, i, return_dict,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()

    return type(iterable[0])(reduce(add, return_dict.values()))    # TODO don't use add, use next()


def pfilter(func, iterable, segments=CPU_COUNT):
    """
    Parallel filter.
    Probably only useful when func is slow.
    ShareableList has no operations that change the length, so it isn't possible
    to pfilter inplace.
    """
    return (filter(func, iterable) if segments == 1 else
            _pfilter(func, iterable))


def _pfilter(func, iterable, segments=CPU_COUNT):
    """
    Data-parallel implementation of filter.
    """
    # ceil rather than floor prevents a segment_ of size 1 at the end.
    segment_size = ceil(len(iterable) / segments)
    processes = []
    return_dict = Manager().dict()
    def subseq_proc(subseq, index, return_dict):
        return_dict[index] = list(filter(func, subseq))
    iterator = iter(iterable)
    for i in range(segments):
        if hasattr(iterable, "__getitem__"):  # O(segments) partitioning
            subseq = iterable[i * segment_size : (i + 1) * segment_size]
        else:  # O(len(iterable)) partitioning
            
            subseq = [next(iterator) for j in range(segment_size)]
        process = Process(target=subseq_proc,
                          args=(subseq, i, return_dict,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()

    return type(iterable)(reduce(add, return_dict.values()))


def preduce(func, iterable, segments=CPU_COUNT):
    """
    Parallel reduce.
    Agrees with serial result when func is associative.
    """
    return (reduce(func, iterable) if segments == 1 else
            _preduce(func, iterable, segments=segments))


def _preduce(func, iterable, segments=CPU_COUNT):
    """
    Data parallel reduce implementation for lists.
    """
    # ceil rather than floor prevents a segment_ of size 1 at the end.
    segment_size = ceil(len(iterable) / segments)
    processes = []
    # Dict rather than list maintains the ordering.
    return_dict = Manager().dict()
    def subseq_proc(sublist, index, return_dict):
        return_dict[index] = reduce(func, sublist)
    iterator = iter(iterable)
    for i in range(segments):
        if hasattr(iterable, "__getitem__"):  # O(segments) partitioning
            subseq = iterable[i * segment_size : (i + 1) * segment_size]
        else:  # O(len(iterable)) partitioning
            subseq = [next(iterator) for j in range(segment_size)]
        process = Process(target=subseq_proc,
                          args=(subseq, i, return_dict,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()

    return reduce(func, return_dict.values())


def psum(iterable):
    """
    Parallel sum.
    """
    return preduce(add, iterable)


def pmax(iterable, segments=CPU_COUNT):
    """
    Parallel all.
    """
    return preduce(max, iterable, segments=segments)


def pmin(iterable, segments=CPU_COUNT):
    """
    Parallel min.
    """
    return preduce(min, iterable, segments=segments)


def _search_with_data_parallelism(iterable, segments=CPU_COUNT, demorgan=False):
    """
    Helper function for pany and pall (DeMorgan flag swaps which).
    Converts iterable to list, partitions list, and searches for a truthy
    element of the partitions in parallel.
    A found truthy interrupts the other processes.
    """
    # ceil rather than floor prevents a chunk of size 1 at the end.
    segment_size = ceil(len(iterable) / segments)
    processes = []
    found_truthy = Value("i", 0)
    iterator = iter(iterable)
    def partial_any(segment, found_truthy):
        for entry in segment:
            if found_truthy.value == 1 or (entry if not demorgan
                                           else not entry):
                # Raise shared done flag to kill other processes.
                found_truthy.value = 1
                return
    for i in range(segments):
        if hasattr(iterable, "__getitem__"):  # O(segments) partitioning
            subseq = iterable[i * segment_size : (i + 1) * segment_size]
        else:  # O(len(iterable)) partitioning
            subseq = [next(iterator) for j in range(segment_size)]
        process = Process(target=partial_any, args=(subseq, found_truthy,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    found = bool(found_truthy.value)

    return found if not demorgan else not found


def pany(iterable, segments=CPU_COUNT):
    """
    Parallel any.
    Only faster than serial version when __bool__ is overridden?
    """
    return _search_with_data_parallelism(iterable, segments=segments)


def pall(iterable, segments=CPU_COUNT):
    """
    Parallel all.
    Only faster than serial version when __bool__ is overridden?
    """
    return _search_with_data_parallelism(iterable, segments=segments,
                                         demorgan=True)
