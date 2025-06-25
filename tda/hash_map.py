class HashMap:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.map = [[] for _ in range(capacity)]

    def _hash(self, key):
        return hash(key) % self.capacity

    def insert(self, key, value):
        index = self._hash(key)
        for pair in self.map[index]:
            if pair[0] == key:
                pair[1] = value
                return
        self.map[index].append([key, value])

    def get(self, key):
        index = self._hash(key)
        for pair in self.map[index]:
            if pair[0] == key:
                return pair[1]
        return None

    def delete(self, key):
        index = self._hash(key)
        for i, pair in enumerate(self.map[index]):
            if pair[0] == key:
                del self.map[index][i]
                return True
        return False

    def keys(self):
        keys = []
        for bucket in self.map:
            keys.extend([pair[0] for pair in bucket])
        return keys

    def values(self):
        values = []
        for bucket in self.map:
            values.extend([pair[1] for pair in bucket])
        return values

    def items(self):
        result = []
        for bucket in self.map:
            for k, v in bucket:
                result.append((k, v))
        return result

    def __contains__(self, key):
        return self.get(key) is not None

    def __len__(self):
        return sum(len(bucket) for bucket in self.map)
