class CappedList:
    def __init__(self, data=[], max_length=100):
        self._list = list(data)
        self.max_length = max_length

    def __len__(self):
        return len(self._list)

    def __getitem__(self, i):
        return self._list[i]

    def __delitem__(self, i):
        del self._list[i]

    # def __setitem__(self, i, value):
    #     self._list[i] = value

    def __str__(self):
        return str(self._list)

    def __iter__(self):
        for e in self._list:
            yield e

    def insert(self, i, value):
        self._list.insert(i, value)

    def add(self, value):
        if len(self._list) == self.max_length:
            del self._list[-1]

        self.insert(0, value)

    def clear(self):
        self._list = []

    def log(self, value):
        if value not in self._list:
            self.add(value)
            return True
        return False

