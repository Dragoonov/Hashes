from abc import ABC, abstractmethod
from enum import Enum
import random
import matplotlib.pyplot as plt

comparisons_amount_for_element = 0


class Dict(ABC):

    def __init__(self):
        self._size = 0
        self._data = []

    @abstractmethod
    def find(self, key):
        pass

    @abstractmethod
    def insert(self, element):
        pass

    @abstractmethod
    def delete(self, key):
        pass

    def _key(self, element):
        return element

    def _h(self, key):
        return hash(key) % len(self._data)

    def __delitem__(self, key):
        self.delete(key)

    def __getitem__(self, item):
        return self.find(item)

    def __len__(self):
        return self._size

    def __contains__(self, item):
        return self.find(item) is not None


class ChainDict(Dict):
    MAX_PER_LIST = 100

    def __init__(self):
        super().__init__()
        self._data = [[] for i in range(16)]

    def _find_index(self, key):
        global comparisons_amount_for_element
        h = hash(key) % len(self._data)
        for i in range(len(self._data[h])):
            comparisons_amount_for_element += 1
            if self._key(self._data[h][i]) == key:
                return h, i
        return h, -1

    def find(self, key):
        global comparisons_amount_for_element
        comparisons_amount_for_element = 0
        h, i = self._find_index(key)
        if i == -1:
            return None
        return self._data[h][i]

    def insert(self, element):
        h, i = self._find_index(self._key(element))
        if i == -1:
            self._data[h].append(element)
            self._size += 1
            if self._size > len(self._data) * self.MAX_PER_LIST:
                self._data = self._new_data(2 * len(self._data))
        else:
            self._data[h][i] = element

    def delete(self, key):
        h, i = self._find_index(key)
        if i != -1:
            self._data[h][i] = self._data[h][len(self._data[h]) - 1]
            self._data[h].pop()
            self._size -= 1
            if (len(self._data)) > 1 and 4 * self._size < len(self._data) * self.MAX_PER_LIST:
                self._data = self._new_data(int(len(self._data) / 2))

    def _new_data(self, new_size):
        r = [[] for i in range(new_size)]
        for tab in self._data:
            for e in tab:
                r[hash(self._key(e)) % len(r)].append(e)
        return r


class LinearDict(Dict):
    N = 999
    D = 1000

    def __init__(self):
        super().__init__()
        self._data = [LinearDict.Special.EMPTY] * 16

    def _empty(self, i):
        return self._data[i] == LinearDict.Special.EMPTY

    def _deleted(self, i):
        return self._data[i] == LinearDict.Special.DELETED

    def _scan_for(self, key):
        global comparisons_amount_for_element
        first_index = self._h(key)
        step = 1
        first_deleted_index = -1
        i = first_index
        while not self._empty(i):
            comparisons_amount_for_element += 1
            if self._deleted(i):
                if first_deleted_index == -1:
                    first_deleted_index = i
            elif self._key(self._data[i]) == key:
                return i
            i = (i + step) % len(self._data)
            if i == first_index:
                return first_deleted_index
        if first_deleted_index != -1:
            return first_deleted_index
        return i

    def find(self, key):
        global comparisons_amount_for_element
        comparisons_amount_for_element = 0
        i = self._scan_for(key)
        if i == -1 or self._empty(i) or self._deleted(i):
            return None
        return self._data[i]

    def insert(self, element):
        i = self._scan_for(self._key(element))
        if self._empty(i) or self._deleted(i):
            self._data[i] = element
            self._size += 1
            if self._size * self.D > len(self._data) * self.N:
                self._data = self._new_data(2 * len(self._data))
        else:
            self._data[i] = element

    def delete(self, key):
        i = self._scan_for(key)
        if not self._empty(i) and not self._deleted(i):
            self._data[i] = LinearDict.Special.DELETED
            self._size -= 1
            if len(self._data) > 1 and self._size * 4 * self.D < len(self._data) * self.N:
                self._data = self._new_data(len(self._data) / 2)

    def _new_data(self, new_size):
        r = [LinearDict.Special.EMPTY] * new_size
        for src_i in range(len(self._data)):
            if not self._empty(src_i) and not self._deleted(src_i):
                key = self._key(self._data[src_i])
                i = self._h(key) % len(r)
                step = 1
                while r[i] != LinearDict.Special.EMPTY:
                    i = (i + step) % len(r)
                r[i] = self._data[src_i]
        return r

    class Special(Enum):
        EMPTY = -1
        DELETED = -2


chainDict = ChainDict()
linearDict = LinearDict()

chaindata = [[], []]
lineardata = [[], []]
rang = 5000
data = random.sample(range(rang), rang)

for i in range(rang):
    chainDict.insert(data[i])
    linearDict.insert(data[i])
    chainDict.find(-1)
    chaindata[0].append(len(chainDict))
    chaindata[1].append(comparisons_amount_for_element)
    linearDict.find(i)
    lineardata[0].append(len(linearDict))
    lineardata[1].append(comparisons_amount_for_element)

plt.plot(chaindata[0], chaindata[1], label="Lancuchowy")
plt.plot(lineardata[0], lineardata[1], label="Liniowy")
plt.xlabel = "Wielkosc slownika"
plt.ylabel('Liczba porownan')
plt.ylim(0, 500)
plt.title('Porownanie lancuchowego i liniowego')
plt.legend()
plt.show()
