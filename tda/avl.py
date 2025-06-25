class AVLNode:
    def __init__(self, key, frequency=1):
        self.key = key
        self.frequency = frequency
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        if not node:
            return AVLNode(key)
        elif key == node.key:
            node.frequency += 1
            return node
        elif key < node.key:
            node.left = self._insert(node.left, key)
        else:
            node.right = self._insert(node.right, key)

        node.height = 1 + max(self._get_height(node.left),
                              self._get_height(node.right))
        return self._balance(node)

    def _get_height(self, node):
        return node.height if node else 0

    def _get_balance(self, node):
        return (self._get_height(node.left) -
                self._get_height(node.right)) if node else 0

    def _balance(self, node):
        balance = self._get_balance(node)

        # Left heavy
        if balance > 1:
            if self._get_balance(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right heavy
        if balance < -1:
            if self._get_balance(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _rotate_left(self, z):
        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        z.height = 1 + max(self._get_height(z.left),
                           self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left),
                           self._get_height(y.right))

        return y

    def _rotate_right(self, z):
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        z.height = 1 + max(self._get_height(z.left),
                           self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left),
                           self._get_height(y.right))

        return y

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append((node.key, node.frequency))
            self._inorder(node.right, result)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        if not node:
            return None
        if key == node.key:
            return node.frequency
        elif key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)
