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

