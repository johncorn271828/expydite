import threading
import time

from expydite.sharedmem import shared

@shared
class Foo:

    __slots__ = ["bar", "baz"]

    def __init__(self, a, b):
        print("init called")
        self.bar = a
        self.baz = b

    def __str__(self):
        return str(self.bar) + " : " + str(self.baz)

    def hello(self):
        print("hello")

    def set_bar(self, a):
        self.bar = a

    def set_baz(self, b):
        self.baz = b

    def get_bar(self):
        return self.bar

    def get_baz(self):
        return self.baz


def test_SharedMemoryObject():
    # Creation works
    foo = Foo(1, 2)
    assert foo.get_bar() == 1
    foo.set_baz(3)
    assert foo.get_baz() == 3

    # Subsequent objects act right
    foo2 = Foo(3, 4)
    assert foo.get_baz() == 3
    assert foo2.get_bar() == 3

    # Threads correctly share
    def set_one_expect_two(x):
        x.set_bar(1)
        time.sleep(3)
        assert x.get_bar()  == 2

    def set_two(x):
        time.sleep(1)
        x.set_bar(2)
        time.sleep(2)

    foo3 = Foo(3, 4)
    t1 = threading.Thread(target=set_one_expect_two, args=(foo3,))
    t2 = threading.Thread(target=set_two, args=(foo3,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
