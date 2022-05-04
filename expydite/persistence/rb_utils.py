from expydite.recursion import tco

@tco
def _search(node, key):
    if key == node.key:
        return node
    elif key < node.key and node.left is not None:
        return _search(node.left, key)
    elif key > node.key and node.right is not None:
        return _search(node.right, key)
    else:
        return None


def _size(node):
    size = 1
    if node.left is not None:
        size += _size(node.left)
    if node.right is not None:
        size += _size(node.right)

    return size

